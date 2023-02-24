import json


class Run:
    def __int__(self, run_name, workflow_config=None):
        self.run_name = run_name
        with open("constants/workflow_meta.json", "r") as f:
            self.workflow_meta = json.load(f)

        self.section = None
        self.step = None
        self.method = None

        if workflow_config is None:
            with open("constants/workflow_config_standard.json", "r") as f:
                self.workflow_config = json.load(f)
        else:
            with open(f"user_data/workflows/{workflow_config}", "r") as f:
                self.workflow_config = json.load(f)

        # self.history = History()

    def calculate(self, section, step, method, parameters):
        pass
