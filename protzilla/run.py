import json
import shutil
from pathlib import Path
from shutil import rmtree

from .constants.location_mapping import location_map, method_map, plot_map
from .constants.logging import MESSAGE_TO_LOGGING_FUNCTION
from .constants.paths import RUNS_PATH, WORKFLOW_META_PATH, WORKFLOWS_PATH
from .history import History
from .workflow_helper import get_all_default_params_for_methods


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
    :ivar result_df
    :ivar current_out
    :ivar current_parameters
    :ivar plots
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

    @property
    def metadata(self):
        for step in self.history.steps:
            if step.step == "metadata_import":
                return step.outputs["metadata"]
        raise AttributeError("Metadata was not yet imported.")

    def write_local_workflow(self):
        workflow_local_path = f"{self.run_path}/workflow.json"
        with open(workflow_local_path, "w") as f:
            json.dump(self.workflow_config, f, indent=2)

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

        self.step_index = len(self.history.steps)
        # make these a result of the step to be compatible with CLI?
        try:
            self.section, self.step, self.method = self.current_workflow_location()
        except IndexError:
            self.handle_all_steps_completed()

        self.result_df = None
        self.current_out = None
        self.current_parameters = None
        self.current_plot_parameters = None
        self.plots = []

    def handle_all_steps_completed(self):
        # TODO 74 think about what should happen when all steps are completed
        self.step_index = len(self.all_steps()) - 1
        self.section, self.step, self.method = self.current_workflow_location()

    def perform_calculation_from_location(self, section, step, method, parameters):
        method_callable = method_map[(section, step, method)]
        self.perform_calculation(method_callable, parameters)

    def perform_calculation(self, method_callable, parameters):
        self.section, self.step, self.method = location_map[method_callable]
        call_parameters = {}
        for k, v in parameters.items():
            param_dict = self.workflow_meta[self.section][self.step][self.method][
                "parameters"
            ].get(k)
            if param_dict and param_dict.get("type") == "named":
                call_parameters[k] = self.history.output_of_named_step(*v)
            else:
                call_parameters[k] = v
        self.result_df, self.current_out = method_callable(self.df, **call_parameters)
        self.current_parameters = parameters
        # error handling for CLI
        if "messages" in self.current_out:
            for message in self.current_out["messages"]:
                log_function = MESSAGE_TO_LOGGING_FUNCTION.get(message["level"])
                if log_function:
                    trace = f"\nTrace: {message['trace']}" if "trace" in message else ""
                    log_function(f"{message['msg']}{trace}")

    def calculate_and_next(self, method_callable, **parameters):  # to be used for CLI
        self.perform_calculation(method_callable, parameters)
        self.next_step()

    def create_plot_from_location(self, section, step, method, parameters):
        location = (section, step, method)
        self.create_plot(plot_map[location], parameters)

    def create_plot(self, method_callable, parameters):
        self.plots = method_callable(
            self.df, self.result_df, self.current_out, **parameters
        )
        self.current_plot_parameters = parameters

    def insert_as_next_step(self, step_to_be_inserted):
        self.section, self.step, self.method = self.current_workflow_location()
        assert self.section is not None

        workflow_meta_step = self.workflow_meta[self.section][step_to_be_inserted]
        first_method_name = list(workflow_meta_step.keys())[0]

        params_default = get_all_default_params_for_methods(
            self.workflow_meta, self.section, step_to_be_inserted, first_method_name
        )
        step_dict = dict(
            name=step_to_be_inserted,
            method=first_method_name,
            parameters=params_default,
        )
        past_steps_of_section = self.history.number_of_steps_in_section(self.section)

        self.workflow_config["sections"][self.section]["steps"].insert(
            past_steps_of_section + 1, step_dict
        )

        self.write_local_workflow()

    def next_step(self, name=None):
        self.history.add_step(
            self.section,
            self.step,
            self.method,
            self.current_parameters,
            self.result_df,
            self.current_out,
            self.plots,
            name=name,
        )
        self.df = self.result_df
        self.result_df = None
        self.step_index += 1
        self.current_parameters = None
        self.current_plot_parameters = None
        self.plots = []
        try:
            self.section, self.step, self.method = self.current_workflow_location()
        except IndexError:
            self.handle_all_steps_completed()

    def back_step(self):
        assert self.history.steps
        popped_step, result_df = self.history.pop_step()
        self.section = popped_step.section
        self.step = popped_step.step
        self.method = popped_step.method
        self.df = self.history.steps[-1].dataframe if self.history.steps else None
        self.result_df = result_df
        self.current_out = popped_step.outputs
        self.current_parameters = popped_step.parameters
        self.current_plot_parameters = None
        self.plots = popped_step.plots
        self.step_index -= 1

    def current_workflow_location(self):
        return self.all_steps()[self.step_index]

    def all_steps(self):
        steps = []
        for section_key, section_dict in self.workflow_config["sections"].items():
            for step in section_dict["steps"]:
                steps.append((section_key, step["name"], step["method"]))
        return steps

    def current_run_location(self):
        return self.section, self.step, self.method
