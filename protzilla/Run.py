from __future__ import annotations

import logging
from pathlib import Path

import protzilla.constants.paths as paths
from protzilla.disk_operator import DiskOperator
from protzilla.steps import (
    ImportMaxQuant,
    ImputationMinPerProtein,
    Output,
    Step,
    StepManager,
)


class Run:
    def __init__(self, run_name: str = None):
        self.run_name: str = run_name
        self.steps: StepManager = StepManager()
        self.disk_operator: DiskOperator = DiskOperator()
        self.workflow_manager: WorkflowManager = WorkflowManager()

    def run_write(self):
        self.disk_operator.write_run(self)

    @classmethod
    def run_read(cls, run_name: str) -> Run:
        run = cls(run_name)
        run.steps = run.disk_operator.read_steps(run.run_disk_path)
        run.steps.current_step_index = run.disk_operator.read_step_index(
            run.run_disk_path
        )
        return run

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

    @staticmethod
    def available_runs() -> list[str]:
        return DiskOperator.get_available_runs()

    @property
    def run_disk_path(self) -> Path:
        assert self.run_name is not None
        return paths.RUNS_PATH / self.run_name

    @property
    def current_plots(self):
        return self.steps.current_step.plots

    @property
    def current_outputs(self) -> Output:
        return self.steps.current_step.output

    @property
    def current_messages(self) -> list[str]:
        return self.steps.current_step.messages.messages

    @property
    def current_step(self) -> Step:
        return self.steps.current_step

    @property
    def is_at_last_step(self) -> bool:
        return self.steps.current_step_index == len(self.steps.all_steps) - 1


class WorkflowManager:
    @staticmethod
    def available_workflows():
        return DiskOperator.get_available_workflows()


if __name__ == "__main__":
    run = Run("new_stepwrapper")
    run.step_add(ImportMaxQuant())
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
    run2 = Run()
    run2.run_read("new_stepwrapper")
    run2.step_previous()
    run2.step_previous()
    run2.step_calculate()
    run2.step_calculate()

    print("done")
