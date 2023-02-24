from pathlib import Path
from .run import Run


class RunManager:
    def __int__(self):
        self.available_runs = []
        for p in Path("user_data/runs").iterdir():
            self.available_runs.append(p.name)

        self.active_runs = {}

    def create_run(self, run_name, workflow_config=None):
        self.active_runs[run_name] = Run(run_name, workflow_config)
