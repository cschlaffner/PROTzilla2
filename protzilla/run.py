import json
from pathlib import Path

from .constants.constants import PATH_TO_PROJECT, PATH_TO_RUNS, PATH_TO_WORKFLOWS
from .constants.method_mapping import method_map
from .history import History


class Run:
    @classmethod
    def create(cls, run_name, workflow_config_name="standard", df_mode="memory"):
        run_path = Path(f"{PATH_TO_RUNS}/{run_name}")
        run_path.mkdir(exist_ok=False)
        run_config = dict(workflow_config_name=workflow_config_name, df_mode=df_mode)
        with open(run_path / "run_config.json", "w") as f:
            json.dump(run_config, f)
        return cls(run_name, workflow_config_name, df_mode)

    @classmethod
    def continue_existing(cls, run_name):
        with open(f"{PATH_TO_RUNS}/{run_name}/run_config.json", "r") as f:
            run_config = json.load(f)
        # add reading history from disk
        # add reading df from history
        return cls(run_name, run_config["workflow_config_name"], run_config["df_mode"])

    def __init__(self, run_name, workflow_config_name, df_mode, history):
        self.run_name = run_name
        with open(f"{PATH_TO_WORKFLOWS}/{workflow_config_name}.json", "r") as f:
            self.workflow_config = json.load(f)

        with open(f"{PATH_TO_PROJECT}/constants/workflow_meta.json", "r") as f:
            self.workflow_meta = json.load(f)

        self.step_index = 0

        # make these a result of the step to be compatible with CLI?
        self.section = None
        self.step = None
        self.method = None

        self.df = None
        self.result_df = None
        self.current_out = None
        self.current_parameters = None
        self.history = History(self.run_name, df_mode)

    def perform_calculation_from_location(self, section, step, method, parameters):
        location = (section, step, method)
        self.perform_calculation(method_map[location], parameters)

    def perform_calculation(self, method_callable, parameters):
        self.result_df, self.current_out = method_callable(self.df, **parameters)
        self.current_parameters = parameters

    def calculate_and_next(self, method_callable, **parameters):  # to be used for CLI
        self.perform_calculation(method_callable, parameters)
        self.next_step()

    # TODO: plots (same method with plots param/<method_name>_plots)

    def next_step(self):
        self.history.add_step(
            self.section,
            self.step,
            self.method,
            self.current_parameters,
            self.result_df,
            self.current_out,
            plots=[],
        )
        self.df = self.result_df
        self.result_df = None

    def back_step(self):
        assert self.history.steps
        self.history.remove_step()
        self.df = self.history.steps[-1].dataframe if self.history.steps else None
        # popping from history.steps possible to get values again
        self.result_df = None
        self.current_out = None
        self.current_parameters = None

        self.section = None
        self.step = None
        self.method = None
