import json
from pathlib import Path

from .constants.method_mapping import method_map
from .constants.paths import RUNS_PATH, WORKFLOW_META_PATH, WORKFLOWS_PATH
from .history import History


class Run:
    @classmethod
    def available_runs(cls):
        available_runs = []
        runs_path = PATH_TO_RUNS
        if runs_path.exists():
            for p in runs_path.iterdir():
                available_runs.append(p.name)
        return available_runs

    @classmethod
    def create(cls, run_name, workflow_config_name="standard", df_mode="memory"):
        run_path = Path(f"{RUNS_PATH}/{run_name}")
        run_path.mkdir(exist_ok=False)
        # TODO add "are you sure you want to overwrite" to frontend
        run_config = dict(workflow_config_name=workflow_config_name, df_mode=df_mode)
        with open(run_path / "run_config.json", "w") as f:
            json.dump(run_config, f)
        history = History(run_name, df_mode)
        return cls(run_name, workflow_config_name, df_mode, history)

    @classmethod
    def continue_existing(cls, run_name):
        with open(f"{RUNS_PATH}/{run_name}/run_config.json", "r") as f:
            run_config = json.load(f)
        history = History.from_disk(run_name, run_config["df_mode"])
        return cls(
            run_name, run_config["workflow_config_name"], run_config["df_mode"], history
        )

    def __init__(self, run_name, workflow_config_name, df_mode, history):
        self.run_name = run_name
        self.history = history
        self.df = self.history.steps[-1].dataframe if self.history.steps else None
        with open(f"{WORKFLOWS_PATH}/{workflow_config_name}.json", "r") as f:
            self.workflow_config = json.load(f)

        with open(WORKFLOW_META_PATH, "r") as f:
            self.workflow_meta = json.load(f)

        self.step_index = 0

        # make these a result of the step to be compatible with CLI?
        self.section = None
        self.step = None
        self.method = None

        self.section = "data-preprocessing"
        self.step = self.workflow_config["sections"][self.section]["steps"][0]["name"]
        self.method = self.workflow_config["sections"][self.section]["steps"][0][
            "method"
        ]
        self.step_dict = self.workflow_meta["sections"][self.section][self.step]

        # TODO this should probaly be part of the history

        self.preset_args = self.workflow_config["sections"][self.section]["steps"][
            self.step_index
        ]
        self.current_args = []

        self.df = None
        self.result_df = None
        self.current_out = None
        self.current_parameters = None

    def perform_calculation_from_location(self, section, step, method, parameters):
        self.section, self.step, self.method = location = (section, step, method)
        method_callable = method_map.get(location, lambda df, **kwargs: (df, {}))
        self.perform_calculation(method_callable, parameters)

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
        self.step_index += 1

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
        self.step_index -= 1

    def workflow_location(self):
        steps = []
        for section_key, section_dict in self.workflow_config["sections"].items():
            if section_key == "importing":
                continue  # not standardized yet
            for step in section_dict["steps"]:
                steps.append((section_key, step["name"], step["method"]))
        return steps[self.step_index]
