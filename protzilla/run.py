import json
from pathlib import Path

from .constants import method_mapping
from .constants.constants import PATH_TO_PROJECT, PATH_TO_RUNS, PATH_TO_WORKFLOWS


class Run:
    @classmethod
    def create(cls, run_name, workflow_config_name="standard"):
        run_path = Path(f"{PATH_TO_RUNS}/{run_name}")
        run_path.mkdir(exist_ok=False)
        run_config = dict(workflow_config_name=workflow_config_name)
        with open(run_path / "run_config.json", "w") as f:
            json.dump(run_config, f)
        return cls(run_name, workflow_config_name)

    @classmethod
    def continue_existing(cls, run_name):
        with open(f"{PATH_TO_RUNS}/{run_name}/run_config.json", "r") as f:
            run_config = json.load(f)
        return cls(run_name, run_config["workflow_config_name"])

    def __init__(self, run_name, workflow_config_name):
        self.run_name = run_name
        with open(f"{PATH_TO_WORKFLOWS}/{workflow_config_name}.json", "r") as f:
            self.workflow_config = json.load(f)

        with open(f"{PATH_TO_PROJECT}/constants/workflow_meta.json", "r") as f:
            self.workflow_meta = json.load(f)

        self.section = None
        self.step = None
        self.method = None

        self.previous_df = None
        self.current_df = None
        self.current_out = None

        # self.history = History()

    def apply_method_from_location(self, section, step, method, parameters):
        location = (section, step, method)
        self.execute(method_mapping[location], parameters)

    def apply_method(self, method_callable, parameters):
        self.current_df, self.current_out = method_callable(
            self.previous_df, **parameters
        )
