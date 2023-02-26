from pathlib import Path

from .run import Run


class RunManager:
    def __init__(self):
        self.available_runs = []
        # only contains all runs if only one run manager active
        runs_path = Path("user_data/runs")
        if runs_path.exists():
            for p in runs_path.iterdir():
                self.available_runs.append(p.name)
        else:
            runs_path.mkdir(parents=True)

        self.active_runs = {}

    def create_run(self, run_name, workflow_config_name):
        assert run_name not in self.available_runs
        self.active_runs[run_name] = Run.create(run_name, workflow_config_name)
        self.available_runs.append(run_name)

    def continue_run(self, run_name):
        assert run_name in self.available_runs
        self.active_runs[run_name] = Run.continue_existing(run_name)
