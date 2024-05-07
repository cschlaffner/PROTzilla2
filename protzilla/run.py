import base64
import json
import logging
import shutil
import traceback
from io import BytesIO
from pathlib import Path
from shutil import rmtree

import plotly
from PIL import Image

from .constants.location_mapping import location_map, method_map, plot_map
from .constants.paths import RUNS_PATH, WORKFLOW_META_PATH, WORKFLOWS_PATH
from .history import History
from .run_helper import log_messages
from .utilities import format_trace
from .workflow import (
    get_global_index_of_step,
    get_parameter_type,
    get_workflow_default_param_value,
    set_output_name,
)


class Run:
    """
    A class to represent a complete data analysis run in protzilla.

    :param run_path: the path to this runs' dir
    :type run_path: str
    :param workflow_config: Contains the contents of the workflow .json
        that was selected for this run at first. It is always updated when
        the workflow gets changed throughout the run (e.g. change of a parameter).
    :type workflow_config: dict
    :param run_name: name of the run
    :type run_name: str
    :param history: an instance of the history class to access the history of this run
    :type history: protzilla.History
    :param step_index: index of the current step over all steps in the workflow
    :type step_index: int
    :param workflow_meta: contains contents of the workflow meta file that contains all
        methods and parameters that exist in protzilla
    :type workflow_meta: dict

    :param section: current section
    :type section: str
    :param step: current step
    :type step: str
    :param method: current method
    :type method: str
    :param df: dataframe that will be used as input for the next data preprocessing step
        (Not used in data analysis! Due to the more flexible dataflow during analysis
        the input dataframe for an analysis step needs to be selectable in the frontend and is an
        input parameter for each new step)
    :type df: pandas.DataFrame
    :param result_df: contains the modified intensity dataframe after a step
    :type result_df: pandas.DataFrame
    :param current_out: contains other outputs from the current step
    :type current_out: dict
    :param current_parameters: calculation parameters that were used to calculate the current step
        (e.g. to update workflow_config correctly)
    :type current_parameters: dict
    :param current_plot_parameters: plot parameters that were used to generate plots for the
        current step (Not used in data analysis! A plot is its own step in that section
        to allow for more flexibility)
    :type current_plot_parameters: dict
    :param calculated_method: method that was used to calculate the current step
    :type calculated_method: str
    :param plots: contains the plots generated in the current step
    :type plots: list[Figure]
    :param plotted_for_parameters: calculation parameters that were used to generate the results that were used to generate current plots, not used in data analysis
    :type plotted_for_parameters: dict
    """

    @classmethod
    def available_runs(cls):
        available_runs = []
        if RUNS_PATH.exists():
            for p in RUNS_PATH.iterdir():
                if p.name.startswith("."):
                    continue
                available_runs.append(p.name)
        return available_runs

    @classmethod
    def available_workflows(cls):
        available_workflows = []
        if WORKFLOWS_PATH.exists():
            for p in WORKFLOWS_PATH.iterdir():
                if p.name.startswith("."):
                    continue
                available_workflows.append(p.stem)
        return available_workflows

    @classmethod
    def create(cls, run_name, workflow_config_name="standard", df_mode="memory"):
        run_path = Path(f"{RUNS_PATH}/{run_name}")
        if run_path.exists():
            rmtree(run_path)
        run_path.mkdir()
        run_config = dict(workflow_config_name=workflow_config_name, df_mode=df_mode)
        with open(run_path / "run_config.json", "w") as f:
            json.dump(run_config, f)
        history = History(run_name, df_mode)
        return cls(run_name, workflow_config_name, df_mode, history, run_path)

    @classmethod
    def continue_existing(cls, run_name):
        run_path = Path(f"{RUNS_PATH}/{run_name}")
        with open(f"{run_path}/run_config.json", "r") as f:
            run_config = json.load(f)
        current_messages = []
        try:
            history = History.from_disk(run_name, run_config["df_mode"])
        except FileNotFoundError:
            history = History(run_name, run_config["df_mode"])
            msg = "Missing calculated Data. Restarted Run."
            current_messages.append(dict(level=logging.ERROR, msg=msg))

        return cls(
            run_name,
            run_config["workflow_config_name"],
            run_config["df_mode"],
            history,
            run_path,
            current_messages,
        )

    def __init__(
        self,
        run_name,
        workflow_config_name,
        df_mode,
        history,
        run_path,
        current_messages=None,
    ):
        if current_messages is None:
            current_messages = []
        self.run_name = run_name
        self.history = history
        self.df = self.history.steps[-1].dataframe if self.history.steps else None
        self.step_index = len(self.history.steps)
        self.run_path = run_path
        self.workflow_config_name = workflow_config_name

        self.workflow_config = self.read_local_workflow()

        with open(WORKFLOW_META_PATH, "r") as f:
            self.workflow_meta = json.load(f)

        # make these a result of the step to be compatible with CLI?
        self.section, self.step, self.method = self.current_workflow_location()
        self.result_df = None
        self.current_out = None
        self.current_messages = current_messages
        self.calculated_method = None
        self.current_parameters = {}
        self.current_plot_parameters = {}
        self.plotted_for_parameters = None
        self.plots = []
        self.current_out_sources = {}

    def update_workflow_config(self, params, location=None, update_params=True):
        if not location:
            (section, step, method) = self.current_workflow_location()
        else:
            (section, step, method) = location
        index = self.step_index_in_current_section()

        if update_params:
            parameters_no_file_path = {
                k: params[k]
                for k in params
                if get_parameter_type(self.workflow_meta, section, step, method, k)
                != "file"
            }
            self.workflow_config["sections"][section]["steps"][index][
                "parameters"
            ] = parameters_no_file_path

        self.workflow_config["sections"][section]["steps"][index]["method"] = method
        self.write_local_workflow()

    def perform_current_calculation_step(self, parameters):
        self.perform_calculation_from_location(*self.current_run_location(), parameters)

    def perform_current_calculation_step_and_next(self, parameters, name=None):
        self.perform_calculation_from_location(*self.current_run_location(), parameters)
        self.next_step(name=name)

    def perform_calculation_from_location(self, section, step, method, parameters):
        location = (section, step, method)
        self.perform_calculation(method_map[location], parameters)
        self.update_workflow_config(parameters, location)

    def perform_calculation(self, method_callable, parameters: dict):
        self.section, self.step, self.method = location_map[method_callable]
        call_parameters = self.exchange_named_outputs_with_data(parameters)
        if "metadata_df" in call_parameters:
            call_parameters["metadata_df"] = self.metadata
        if "peptide_df" in call_parameters:
            call_parameters["peptide_df"] = self.peptide_data
        if "run_name" in call_parameters:
            call_parameters["run_name"] = self.run_name

        calculation_failed = False
        if self.section in ["importing", "data_preprocessing"]:
            try:
                self.result_df, self.current_out = method_callable(
                    self.df, **call_parameters
                )
                if "messages" in self.current_out and any(
                    messages["level"] == logging.ERROR
                    for messages in self.current_out["messages"]
                ):
                    calculation_failed = True
                self.current_messages.extend(self.current_out.pop("messages", {}))
            except Exception as e:
                calculation_failed = True
                msg = f"An error occurred while calculating this step: {e.__class__.__name__} {e} Please check your parameters or report a potential programming issue."
                self.current_out = {}
                self.current_messages.append(
                    dict(
                        level=logging.ERROR,
                        msg=msg,
                        trace=format_trace(traceback.format_exception(e)),
                    )
                )
        else:
            self.result_df = None
            try:
                self.current_out = method_callable(**call_parameters)
                if "messages" in self.current_out and any(
                    messages["level"] == logging.ERROR
                    for messages in self.current_out["messages"]
                ):
                    calculation_failed = True
                self.current_messages.extend(self.current_out.pop("messages", []))
            except Exception as e:
                calculation_failed = True
                self.current_out = {}
                msg = f"An error occurred while calculating this step: {e.__class__.__name__} {e} Please check your parameters or report a potential programming issue."
                self.current_messages.append(
                    dict(
                        level=logging.ERROR,
                        msg=msg,
                        trace=format_trace(traceback.format_exception(e)),
                    )
                )

        self.plots = []  # reset as not up to date anymore
        self.current_parameters[self.method] = parameters
        self.calculated_method = self.method

        if calculation_failed:
            self.result_df = None
            self.current_parameters.pop(self.method, None)
            self.calculated_method = None

    def calculate_and_next(
        self, method_callable, name=None, **parameters
    ):  # to be used for CLI
        self.perform_calculation(method_callable, parameters)
        self.next_step(name=name)

    def create_plot_from_current_location(self, parameters):
        location = (section, step, method) = self.current_run_location()
        if step == "plot":
            self.update_workflow_config(parameters, location=location)
            self.create_step_plot(plot_map[location], parameters)
        elif plot_map.get(location):
            self.workflow_config["sections"][section]["steps"][
                self.step_index_in_current_section()
            ]["graphs"] = [parameters]
            self.write_local_workflow()
            self.create_plot(plot_map[location], parameters)

        if section in ["importing", "data_preprocessing"]:
            self.plotted_for_parameters = self.current_parameters.get(method)
            self.current_plot_parameters[method] = parameters
        else:  # not used in data analysis
            self.plotted_for_parameters = None
            self.current_plot_parameters = {}  # expected dict for all_button_parameters

    def create_plot(self, method_callable, parameters):
        try:
            self.plots = method_callable(
                self.df, self.result_df, self.current_out, **parameters
            )
            for plot in self.plots:
                if isinstance(plot, dict) and "messages" in plot:
                    self.current_messages.extend(plot["messages"])
                    self.plots.remove(plot)

        except Exception as e:
            self.plots = []
            msg = f"An error occurred while plotting: {e.__class__.__name__} {e} Please check your parameters or report a potential programming issue."
            self.current_messages.append(
                dict(
                    level=logging.ERROR,
                    msg=msg,
                    trace=format_trace(traceback.format_exception(e)),
                )
            )

    def create_step_plot(self, method_callable, parameters):
        if "term_name" in parameters:
            parameters["term_name"] = parameters["term_dict"][1]
        call_parameters = self.exchange_named_outputs_with_data(parameters)
        if "proteins_of_interest_input" in call_parameters:
            del call_parameters["proteins_of_interest_input"]
        try:
            self.plots = method_callable(**call_parameters)
            self.result_df = self.df
            self.current_out = {}
            self.current_parameters[self.method] = parameters
            self.calculated_method = self.method

            for plot in self.plots:
                if isinstance(plot, dict) and "messages" in plot:
                    self.current_messages.extend(plot["messages"])
                    self.plots.remove(plot)
        except Exception as e:
            self.plots = []
            self.result_df = None
            self.current_out = {}
            msg = f"An error occurred while plotting: {e.__class__.__name__} {e} Please check your parameters or report a potential programming issue."
            self.current_messages.append(
                dict(
                    level=logging.ERROR,
                    msg=msg,
                    trace=format_trace(traceback.format_exception(e)),
                )
            )
            self.current_parameters.pop(self.method, None)
            self.calculated_method = None

    def insert_step(self, step_to_be_inserted, section, method, index):
        step_dict = dict(name=step_to_be_inserted, method=method, parameters={})
        if section == "data_preprocessing":
            step_dict["graphs"] = [{}]
        self.workflow_config["sections"][section]["steps"].insert(index, step_dict)
        self.write_local_workflow()

    def write_local_workflow(self):
        workflow_local_path = f"{self.run_path}/workflow.json"
        with open(workflow_local_path, "w") as f:
            json.dump(self.workflow_config, f, indent=2)

    def read_local_workflow(self):
        workflow_local_path = f"{self.run_path}/workflow.json"
        if not Path(workflow_local_path).is_file():
            workflow_template_path = (
                f"{WORKFLOWS_PATH}/{self.workflow_config_name}.json"
            )
            shutil.copy2(workflow_template_path, workflow_local_path)

        with open(workflow_local_path, "r") as f:
            self.workflow_config = json.load(f)
        return self.workflow_config

    def insert_at_next_position(self, step_to_be_inserted, section, method):
        if self.section == section:
            past_steps_of_section = self.history.number_of_steps_in_section(section)

            self.insert_step(
                step_to_be_inserted, section, method, past_steps_of_section + 1
            )
        else:
            self.insert_step(step_to_be_inserted, section, method, 0)

        self.section, self.step, self.method = self.current_workflow_location()

    def export_workflow(self, name):
        with open(f"{WORKFLOWS_PATH}/{name}.json", "w") as f:
            json.dump(self.workflow_config, f, indent=2)

    def delete_step(self, section, index):
        del self.workflow_config["sections"][section]["steps"][index]
        self.write_local_workflow()

    def next_step(self, name=None):
        if name is None:
            name = get_workflow_default_param_value(
                self.workflow_config,
                *self.current_run_location(),
                self.step_index_in_current_section(),
                "output_name",
            )
        try:
            parameters = self.current_parameters.get(self.calculated_method, {})
            self.history.add_step(self.section)
            self.update_workflow_config(parameters)
            index = self.step_index_in_current_section()
            self.workflow_config["sections"][self.section]["steps"][index][
                "method"
            ] = self.calculated_method
            self.name_step(-1, name)

        except AssertionError as e:
            self.history.pop_step()
            self.current_messages.append(dict(level=logging.ERROR, msg=f"{e}"))
        except Exception as e:
            self.history.pop_step()
            msg = f"An error occurred while saving this step: {e.__class__.__name__} {e} Please check your parameters or report a potential programming issue."
            self.current_messages.append(
                dict(
                    level=logging.ERROR,
                    msg=msg,
                    trace=format_trace(traceback.format_exception(e)),
                )
            )

        else:
            self.step_index += 1
            self.section, self.step, self.method = self.current_workflow_location()
            self.df = self.result_df
            self.result_df = None
            self.calculated_method = None
            self.current_out = {}
            self.current_parameters = {}
            self.current_plot_parameters = {}
            self.plotted_for_parameters = None
            self.plots = []
            self.current_out_sources = {}

    def back_step(self):
        self.navigate_relative(-1)

    def navigate_relative(self, steps: int):
        """
        Navigates to a step relative to the current step.

        :param steps: the number of steps to navigate. Negative values navigate backwards.
        """
        if steps > 0:
            raise Exception(f"Can not navigate to future step.")
        elif steps < 0:
            assert self.history.steps
            for i in range(-steps - 1):
                self.history.pop_step()
            popped_step, popped_result_df = self.history.pop_step()
            self.section = popped_step.section
            self.step = popped_step.step
            self.method = popped_step.method
            self.calculated_method = self.method
            self.df = self.history.steps[-1].dataframe if self.history.steps else None
            self.result_df = popped_result_df
            self.current_out = popped_step.outputs
            self.current_messages = popped_step.messages
            self.current_parameters = {self.method: popped_step.parameters}
            self.current_plot_parameters = {}
            # TODO: add plotted_for_parameter to History?
            self.plotted_for_parameters = None
            self.plots = popped_step.plots
            self.step_index += steps

    def navigate(self, section_name: str, step_index: int):
        """
        Navigates to a specific step in the run.

        :param step_index: the index of the step to navigate to within the section
        :param section_name: the name of the section in which the step is located
        """
        # Find the global index of the step within the specified section
        global_index = get_global_index_of_step(
            self.workflow_config, section_name, step_index
        )

        self.navigate_relative(global_index - self.step_index)

    def current_workflow_location(self):
        try:
            return self.all_steps()[self.step_index]
        except IndexError:
            return "", "", ""

    def step_index_in_current_section(self):
        steps_before_this_section = 0
        for section, step, method in self.all_steps():
            if section == self.section:
                return self.step_index - steps_before_this_section
            steps_before_this_section += 1
        raise Exception(f"section {self.section} not found")

    def all_steps(self):
        steps = []
        for section_key, section_dict in self.workflow_config["sections"].items():
            for step in section_dict["steps"]:
                steps.append((section_key, step["name"], step["method"]))
        return steps

    def current_run_location(self):
        return self.section, self.step, self.method

    def exchange_named_outputs_with_data(self, parameters):
        call_parameters = {}
        for k, v in parameters.items():
            param_dict = self.workflow_meta[self.section][self.step][self.method][
                "parameters"
            ].get(k)
            if param_dict and param_dict.get("type") == "named_output":
                # v should consist of values [named_step, output]
                assert (
                    v is not None
                ), f"please set default values for the named_output: {k} in workflow file"
                call_parameters[k] = self.history.output_of_named_step(*v)
            elif param_dict and param_dict.get("type") == "multi_named_output":
                for call_parameter, output_name in param_dict.get("mapping").items():
                    call_parameters[call_parameter] = self.history.output_of_named_step(
                        v, output_name
                    )
            elif param_dict and param_dict.get("type") == "named_output_v2":
                call_parameters[k] = self.current_out_sources[v]
            else:
                call_parameters[k] = v
        return call_parameters

    @property
    def metadata(self):
        for step in self.history.steps:
            if step.step == "metadata_import":
                return step.outputs["metadata"]
        raise AttributeError("Metadata was not yet imported.")

    @property
    def has_metadata(self):
        try:
            _ = self.metadata
        except AttributeError:
            return False
        else:
            return True

    @property
    def peptide_data(self):
        for step in self.history.steps:
            if step.step == "peptide_import":
                return step.outputs["peptide_df"]
        raise AttributeError("Peptides were not yet imported.")

    def export_plots(self, format_):
        exports = []
        for plot in self.plots:
            if isinstance(plot, plotly.graph_objs.Figure):
                if format_ in ["eps", "tiff"]:
                    png_binary = plotly.io.to_image(plot, format="png", scale=4)
                    img = Image.open(BytesIO(png_binary)).convert("RGB")
                    binary = BytesIO()
                    if format_ == "tiff":
                        img.save(binary, format="tiff", compression="tiff_lzw")
                    else:
                        img.save(binary, format=format_)
                    exports.append(binary)
                else:
                    binary_string = plotly.io.to_image(plot, format=format_, scale=4)
                    exports.append(BytesIO(binary_string))
            elif isinstance(plot, dict) and "plot_base64" in plot:
                plot = plot["plot_base64"]

            if isinstance(plot, bytes):  # base64 encoded plots
                if format_ in ["eps", "tiff"]:
                    img = Image.open(BytesIO(base64.b64decode(plot))).convert("RGB")
                    binary = BytesIO()
                    if format_ == "tiff":
                        img.save(binary, format="tiff", compression="tiff_lzw")
                    else:
                        img.save(binary, format=format_)
                    binary.seek(0)
                    exports.append(binary)
                elif format_ in ["png", "jpg"]:
                    exports.append(BytesIO(base64.b64decode(plot)))
        return exports

    def name_step(self, index, name):
        self.history.name_step_in_history(index, name)
        self.history.save()
        set_output_name(
            self.workflow_config,
            self.section,
            self.step_index_in_current_section(),
            name,
        )
        self.write_local_workflow()
