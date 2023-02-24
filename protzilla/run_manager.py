from pathlib import Path

from .run import Run


class RunManager:
    def __int__(self):
        self.available_runs = []
        for p in Path("user_data/runs").iterdir():
            self.available_runs.append(p.name)

        self.active_runs = {}

    def create_run(self, run_name, workflow_config_name):
        assert run_name not in self.available_runs
        self.active_runs[run_name] = Run.create(run_name, workflow_config_name)
        self.available_runs.append(run_name)

    def continue_run(self, run_name):
        assert run_name in self.available_runs
        self.active_runs[run_name] = Run.continue_existing(run_name)
