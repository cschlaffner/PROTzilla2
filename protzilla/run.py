import json
import shutil
import traceback
from io import BytesIO
from pathlib import Path
from shutil import rmtree

import plotly
from PIL import Image

from .constants.location_mapping import location_map, method_map, plot_map
from .constants.logging import MESSAGE_TO_LOGGING_FUNCTION
from .constants.paths import RUNS_PATH, WORKFLOW_META_PATH, WORKFLOWS_PATH
from .history import History
from .workflow_helper import (
    get_all_default_params_for_methods,
    get_workflow_default_param_value,
)


class Run:
    """
    :ivar run_path: the path to this runs' dir
    :ivar workflow_config
    :ivar run_name
    :ivar history
    :ivar step_index
    :ivar workflow_meta

    :ivar section
    :ivar step
    :ivar method
    :ivar df: dataframe that will be used as input for the next data preprocessing step, not used in data analysis
    :ivar result_df
    :ivar current_out
    :ivar current_parameters: calculation parameters that were used to calculate for each method
    :ivar current_plot_parameters: plot parameters that were used to generate plots for each method, not used in data analysis
    :ivar calculated_method: method that was last used to calculate
    :ivar plots
    :ivar plotted_for_parameters: calculation parameters that were used to generate the results that were used to generate plots, not used in data analysis
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
        history = History.from_disk(run_name, run_config["df_mode"])
        return cls(
            run_name,
            run_config["workflow_config_name"],
            run_config["df_mode"],
            history,
            run_path,
        )

    def __init__(self, run_name, workflow_config_name, df_mode, history, run_path):
        self.run_name = run_name
        self.history = history
        self.df = self.history.steps[-1].dataframe if self.history.steps else None
        self.step_index = len(self.history.steps)
        self.run_path = run_path

        workflow_local_path = f"{self.run_path}/workflow.json"
        if not Path(workflow_local_path).is_file():
            workflow_template_path = f"{WORKFLOWS_PATH}/{workflow_config_name}.json"
            shutil.copy2(workflow_template_path, workflow_local_path)

        with open(workflow_local_path, "r") as f:
            self.workflow_config = json.load(f)

        with open(WORKFLOW_META_PATH, "r") as f:
            self.workflow_meta = json.load(f)

        # make these a result of the step to be compatible with CLI?
        self.section, self.step, self.method = self.current_workflow_location()
        self.result_df = None
        self.current_out = None
        self.calculated_method = None
        self.current_parameters = {}
        self.current_plot_parameters = {}
        self.plotted_for_parameters = None
        self.plots = []

    def update_workflow_config(self, section, index, parameters):
        self.workflow_config["sections"][section]["steps"][index][
            "parameters"
        ] = parameters
        self.write_local_workflow()

    def perform_calculation_from_location(self, section, step, method, parameters):
        location = (section, step, method)
        self.perform_calculation(method_map[location], parameters)

    def perform_calculation(self, method_callable, parameters: dict):
        self.section, self.step, self.method = location_map[method_callable]
        call_parameters = self.exchange_named_outputs_with_data(parameters)
        if "metadata_df" in call_parameters:
            call_parameters["metadata_df"] = self.metadata

        if self.section in ["importing", "data_preprocessing"]:
            self.result_df, self.current_out = method_callable(
                self.df, **call_parameters
            )
        else:
            self.result_df = None
            self.current_out = method_callable(**call_parameters)

        self.update_workflow_config(
            self.section, self.step_index_in_current_section(), parameters
        )
        self.plots = []  # reset as not up to date anymore
        self.current_parameters[self.method] = parameters
        self.calculated_method = self.method
        # error handling for CLI
        if "messages" in self.current_out:
            for message in self.current_out["messages"]:
                log_function = MESSAGE_TO_LOGGING_FUNCTION.get(message["level"])
                if log_function:
                    trace = f"\nTrace: {message['trace']}" if "trace" in message else ""
                    log_function(f"{message['msg']}{trace}")

    def calculate_and_next(
        self, method_callable, name=None, **parameters
    ):  # to be used for CLI
        self.perform_calculation(method_callable, parameters)
        self.next_step(name=name)

    def create_plot_from_location(self, section, step, method, parameters):
        location = (section, step, method)
        if step == "plot":
            self.create_step_plot(plot_map[location], parameters)
        elif plot_map.get(location):
            self.create_plot(plot_map[location], parameters)

        if section in ["importing", "data_preprocessing"]:
            self.plotted_for_parameters = self.current_parameters[method]
            self.current_plot_parameters[method] = parameters
        else:  # not used in data analysis
            self.plotted_for_parameters = None
            self.current_plot_parameters = {}  # expected dict for all_button_parameters

    def create_plot(self, method_callable, parameters):
        self.plots = method_callable(
            self.df, self.result_df, self.current_out, **parameters
        )

    def create_step_plot(self, method_callable, parameters):
        call_parameters = self.exchange_named_outputs_with_data(parameters)
        self.plots = method_callable(**call_parameters)
        self.result_df = self.df
        self.current_out = {}
        self.current_parameters[self.method] = parameters
        self.calculated_method = self.method

    def insert_step(self, step_to_be_inserted, section, method, index):
        params_default = get_all_default_params_for_methods(
            self.workflow_meta, section, step_to_be_inserted, method
        )
        step_dict = dict(
            name=step_to_be_inserted,
            method=method,
            parameters=params_default,
        )

        self.workflow_config["sections"][section]["steps"].insert(index, step_dict)

        self.write_local_workflow()

    def write_local_workflow(self):
        workflow_local_path = f"{self.run_path}/workflow.json"
        with open(workflow_local_path, "w") as f:
            json.dump(self.workflow_config, f, indent=2)

    def insert_at_next_position(self, step_to_be_inserted, section, method):
        if self.section == section:
            past_steps_of_section = self.history.number_of_steps_in_section(section)

            self.insert_step(
                step_to_be_inserted, section, method, past_steps_of_section + 1
            )
        else:
            self.insert_step(step_to_be_inserted, section, method, 0)

    def export_workflow(self, name):
        with open(f"{WORKFLOWS_PATH}/{name}.json", "w") as f:
            json.dump(self.workflow_config, f, indent=2)

    def delete_step(self, section, index):
        del self.workflow_config["sections"][section]["steps"][index]
        self.write_local_workflow()

    def next_step(self, name=None):
        if not name:
            name = get_workflow_default_param_value(
                self.workflow_config, *(self.current_run_location()), "output_name"
            )
        try:
            self.history.add_step(
                self.section,
                self.step,
                self.calculated_method,
                self.current_parameters[self.calculated_method],
                self.result_df,
                self.current_out,
                self.plots,
                name=name,
            )
        except TypeError:  # catch error when serializing json
            # remove "broken" step from history again
            self.history.pop_step()
            traceback.print_exc()
            # TODO 100 add message to user?
        else:  # continue normally when no error occurs
            self.step_index += 1
            # important for runner, we do not want to update anything, when we do not have a step
            try:
                self.section, self.step, self.method = self.current_workflow_location()
                self.df = self.result_df
                self.result_df = None
                self.calculated_method = None
                self.current_parameters = {}
                self.current_plot_parameters = {}
                self.plotted_for_parameters = None
                self.plots = []
            except IndexError:
                self.step_index -= 1

    def back_step(self):
        assert self.history.steps
        popped_step, result_df = self.history.pop_step()
        self.section = popped_step.section
        self.step = popped_step.step
        self.method = popped_step.method
        self.calculated_method = self.method
        self.df = self.history.steps[-1].dataframe if self.history.steps else None
        self.result_df = result_df
        self.current_out = popped_step.outputs
        self.current_parameters = {self.method: popped_step.parameters}
        self.current_plot_parameters = {}
        # TODO: add plotted_for_parameter to History?
        self.plotted_for_parameters = None
        self.plots = popped_step.plots
        self.step_index -= 1

    def current_workflow_location(self):
        return self.all_steps()[self.step_index]

    def step_index_in_current_section(self):
        index = 0
        for section, step, method in self.all_steps():
            if section == self.section:
                if step == self.step:
                    return index
                index += 1

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
            else:
                call_parameters[k] = v
        return call_parameters

    @property
    def metadata(self):
        for step in self.history.steps:
            if step.step == "metadata_import":
                return step.outputs["metadata"]
        raise AttributeError("Metadata was not yet imported.")

    def export_plots(self, format_):
        exports = []
        for plot in self.plots:
            if isinstance(plot, plotly.graph_objs.Figure):  # to catch dicts
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
        return exports
