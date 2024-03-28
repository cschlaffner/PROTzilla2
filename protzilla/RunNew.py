from __future__ import annotations

import logging

import protzilla.constants.paths as paths
from protzilla.disk_operator import DiskOperator
from protzilla.steps import ImputationMinPerProtein, MaxQuantImport, Step, StepManager


class RunNew:
    def __init__(self, run_name: str = None):
        self.run_name: str = run_name
        self.steps: StepManager = StepManager()
        self.disk_operator: DiskOperator = DiskOperator()

    def run_write(self):
        self.disk_operator.write_run(self)

    def run_read(self, run_name: str = None):
        if run_name is None:
            run_name = self.run_name
        else:
            self.run_name = run_name

        self.steps = self.disk_operator.read_steps(self.run_disk_path)
        self.steps.current_step_index = self.disk_operator.read_step_index(
            self.run_disk_path
        )

    def step_add(self, step: Step, step_index: int = None):
        if step_index is None:
            self.steps.add_step(step)
        else:
            raise NotImplementedError
            self.steps.add_step(step, step_index)

    def step_remove(self, step: Step = None, step_index: int = None):
        self.steps.remove_step(step=step, step_index=step_index)

    def step_calculate(self, inputs: dict = None):
        self.steps.current_step.calculate(self.steps, inputs)
        self.step_next()

    def step_next(self):
        if self.steps.current_step_index < len(self.steps.all_steps) - 1:
            self.steps.current_step_index += 1
        else:
            logging.warning("Cannot go forward from the last step")

    def step_previous(self):
        if self.steps.current_step_index > 0:
            self.steps.current_step_index -= 1
        else:
            logging.warning("Cannot go back from the first step")

    @property
    def available_runs(self):
        return self.disk_operator.available_runs

    @property
    def run_disk_path(self):
        assert self.run_name is not None
        return paths.RUNS_PATH / self.run_name


class WorkflowManager:
    def __init__(self):
        self.workflows = {}

    @property
    def available_workflows(self):
        return self.workflows.keys()


if __name__ == "__main__":
    run = RunNew("new_stepwrapper")
    run.step_add(MaxQuantImport())
    run.step_add(ImputationMinPerProtein())

    run.step_calculate(
        {
            "file_path": "/home/henning/BP2023BR1/PROTzilla2/example/MaxQuant_data/proteinGroups_small.txt",
            "map_to_uniprot": True,
            "intensity_name": "Intensity",
        }
    )
    run.step_calculate({"shrinking_value": 0.5})
    run.run_write()
    run2 = RunNew()
    run2.run_read("new_stepwrapper")
    run2.step_previous()
    run2.step_previous()
    run2.step_calculate()
    run2.step_calculate()

    print("done")
