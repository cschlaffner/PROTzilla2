import json
import os.path
import shutil
from pathlib import Path
from shutil import rmtree

from .constants.location_mapping import method_map, plot_map
from .constants.paths import RUNS_PATH, WORKFLOW_META_PATH, WORKFLOWS_PATH
from .history import History
from .utilities.dynamic_parameters_provider import input_data_name_to_location
from .workflow_helper import get_all_default_params_for_methods


class Run:

    """
    :ivar run_path: the path to this runs' dir
    :ivar workflow_config
    :ivar run_name
    :ivar input_data_location
    :ivar history
    :ivar step_index
    :ivar workflow_meta

    :ivar section
    :ivar step
    :ivar method
    :ivar result_df
    :ivar current_out
    :ivar current_parameters
    :ivar plots
    :ivar step_name
    :ivar input_data
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

    def write_local_workflow(self):
        workflow_local_path = f"{self.run_path}/workflow.json"
        with open(workflow_local_path, "w") as f:
            json.dump(self.workflow_config, f, indent=2)

    def __init__(self, run_name, workflow_config_name, df_mode, history, run_path):
        self.run_name = run_name
        self.history = history
        self.input_data_location = (
            self.history.steps[-1].input_data_location if self.history.steps else None
        )
        self.input_data = (
            self.history.steps[self.input_data_location["step_index"]].output_mapping(
                self.input_data_location["key"]
            )
            if self.input_data_location
            else None
        )
        self.step_index = len(self.history.steps)
        self.run_path = run_path

        workflow_local_path = f"{self.run_path}/workflow.json"
        if not os.path.exists(workflow_local_path):
            workflow_template_path = f"{WORKFLOWS_PATH}/{workflow_config_name}.json"
            shutil.copy2(workflow_template_path, workflow_local_path)

        with open(workflow_local_path, "r") as f:
            try:
                self.workflow_config = json.load(f)
            except Exception as e:
                print("could not read json:", workflow_local_path)
                raise e

        with open(WORKFLOW_META_PATH, "r") as f:
            self.workflow_meta = json.load(f)

        # make these a result of the step to be compatible with CLI?
        self.section = None
        self.step = None
        self.method = None
        self.result_df = None
        self.current_out = None
        self.current_parameters = None
        self.plots = None
        self.step_name = None

    def prepare_calculation(self, step_name, input_data_name=None):
        # data_analysis or data_integration
        if input_data_name is not None:
            self.input_data_location = input_data_name_to_location(self)[
                input_data_name
            ]
            step_index = self.input_data_location["step_index"]
            key = self.input_data_location["key"]

            self.input_data = self.history.steps[step_index].output_mapping(key)
        # importing or data_preprocessing
        elif self.history.steps:
            self.input_data_location = dict(
                step_index=self.step_index - 1, key="dataframe"
            )
            self.input_data = self.history.steps[-1].dataframe

        self.step_name = step_name

    def perform_calculation_from_location(self, section, step, method, parameters):
        self.section, self.step, self.method = location = (section, step, method)
        method_callable = method_map[location]
        self.perform_calculation(method_callable, parameters)

    def perform_calculation(self, method_callable, parameters):
        self.result_df, self.current_out = method_callable(
            self.input_data, **parameters
        )
        self.current_parameters = parameters

    def calculate_and_next(self, method_callable, **parameters):  # to be used for CLI
        self.perform_calculation(method_callable, parameters)
        self.next_step()

    def create_plot_from_location(self, section, step, method, parameters):
        location = (section, step, method)
        self.create_plot(plot_map[location], parameters)

    def create_plot(self, method_callable, parameters):
        self.plots = method_callable(
            self.input_data, self.result_df, self.current_out, **parameters
        )

    def insert_as_next_step(self, insert_step):
        self.section, self.step, self.method = self.current_workflow_location()

        assert self.section is not None

        workflow_meta_step = self.workflow_meta[self.section][insert_step]
        first_method_name = list(workflow_meta_step.keys())[0]

        params_default = get_all_default_params_for_methods(
            self.workflow_meta, self.section, insert_step, first_method_name
        )

        insert_step_dict = dict(
            name=insert_step, method=first_method_name, parameters=params_default
        )

        past_steps_of_section = self.history.get_past_steps_of_section(self.section)

        self.workflow_config["sections"][self.section]["steps"].insert(
            past_steps_of_section + 1, insert_step_dict
        )

        self.write_local_workflow()

    def next_step(self):
        self.history.add_step(
            self.section,
            self.step,
            self.method,
            self.current_parameters,
            self.input_data_location,
            self.result_df,
            self.current_out,
            self.plots,
            self.step_name,
        )
        self.input_data_location = None
        self.input_data = None
        self.result_df = None
        self.step_index += 1
        self.current_parameters = None

    def back_step(self):
        assert self.history.steps is not None
        self.input_data_location = (
            self.history.steps[-1].input_data_location if self.history.steps else None
        )
        self.input_data = (
            self.history.steps[self.input_data_location["step_index"]].output_mapping(
                self.input_data_location["key"]
            )
            if self.input_data_location
            else None
        )
        self.history.remove_step()

        # popping from history.steps possible to get values again
        self.result_df = None
        self.current_out = None
        self.current_parameters = None

        self.section = None
        self.step = None
        self.method = None
        self.step_index -= 1

    def current_workflow_location(self):
        return self.all_steps()[self.step_index]

    def all_steps(self):
        steps = []
        for section_key, section_dict in self.workflow_config["sections"].items():
            for step in section_dict["steps"]:
                steps.append((section_key, step["name"], step["method"]))
        return steps
