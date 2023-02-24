import json

from constants import method_mapping


class Run:
    def __int__(self, run_name, workflow_config=None):
        self.run_name = run_name
        with open("constants/workflow_meta.json", "r") as f:
            self.workflow_meta = json.load(f)

        self.section = None
        self.step = None
        self.method = None

        self.previous_df = None
        self.current_df = None
        self.current_out = None

        if workflow_config is None:
            with open("constants/workflow_config_standard.json", "r") as f:
                self.workflow_config = json.load(f)
        else:
            with open(f"user_data/workflows/{workflow_config}", "r") as f:
                self.workflow_config = json.load(f)

        # self.history = History()

    def calculate(self, section, step, method, parameters):
        location = (section, step, method)
        self.execute(method_mapping[location], parameters)

    def execute(self, method_callable, parameters):
        self.current_df, self.current_out = method_callable(
            self.previous_df, **parameters
        )
