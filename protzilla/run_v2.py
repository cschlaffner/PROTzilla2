from __future__ import annotations

import logging

import protzilla.constants.paths as paths
from protzilla.methods.data_preprocessing import ImputationMinPerProtein
from protzilla.methods.importing import MaxQuantImport
from protzilla.steps import Step, StepManager


def get_available_run_names() -> list[str]:
    return [
        directory.name
        for directory in paths.RUNS_PATH.iterdir()
        if not directory.name.startswith(".")
    ]


class Run:
    def __init__(
        self, run_name: str, workflow_name: str | None = None, df_mode: str = "disk"
    ):
        from protzilla.disk_operator import DiskOperator  # to avoid a circular import

        self.run_name = run_name
        self.workflow_name = workflow_name

        self.steps = StepManager()
        self.disk_operator = DiskOperator()
        self.df_mode = df_mode

        if run_name in get_available_run_names():
            self._run_read_existing()
        elif workflow_name:
            self._run_read_new()
        else:
            raise ValueError(
                f"No run named {run_name} has been found and no workflow has been provided. Please reference an existing run or provide a workflow to create a new one."
            )

    def _run_write(self):
        self.disk_operator.write_run(self)

    def _run_read_existing(self):
        self.steps = self.disk_operator.read_steps(self.run_disk_path)
        self.steps.current_step_index = self.disk_operator.read_step_index(
            self.run_disk_path
        )

    def _run_read_new(self):
        self.steps = self.disk_operator.read_workflow(self.workflow_name)
        self.steps.current_step_index = 0
        self._run_write()

    def step_add(self, step: Step, step_index: int | None = None):
        self.steps.add_step(step, step_index)
        self._run_write()

    def step_remove(self, step: Step | None = None, step_index: int | None = None):
        self.steps.remove_step(step=step, step_index=step_index)
        self._run_write()

    def step_calculate(self, inputs: dict | None = None):
        self.steps.current_step.calculate(self.steps, inputs)
        self._run_write()

    def step_next(self):
        if self.steps.current_step_index < len(self.steps.all_steps) - 1:
            self.steps.current_step_index += 1
            self._run_write()
        else:
            logging.warning("Cannot go forward from the last step")

    def step_previous(self):
        if self.steps.current_step_index > 0:
            self.steps.current_step_index -= 1
            self._run_write()
        else:
            logging.warning("Cannot go back from the first step")

    @property
    def is_at_last_step(self):
        return self.steps.is_at_last_step

    @property
    def run_disk_path(self):
        assert self.run_name is not None
        return paths.RUNS_PATH / self.run_name

    @property
    def current_messages(self):
        return self.steps.current_step.messages

    @property
    def current_plots(self):
        return self.steps.current_step.plots

    @property
    def current_outputs(self):
        return self.steps.current_step.output

    @property
    def current_step(self):
        return self.steps.current_step


if __name__ == "__main__":
    run = Run("new_stepwrapper")
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
    run2 = Run()
    run2.run_read("new_stepwrapper")
    run2.step_previous()
    run2.step_previous()
    run2.step_calculate()
    run2.step_calculate()

    print("done")
