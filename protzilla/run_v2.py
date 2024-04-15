from __future__ import annotations

import logging

import protzilla.constants.paths as paths
from protzilla.steps import Plots, Step, StepManager


def get_available_run_names() -> list[str]:
    return [
        directory.name
        for directory in paths.RUNS_PATH.iterdir()
        if not directory.name.startswith(".")
    ]


class Run:
    def auto_save(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self._run_write()
            return result

        return wrapper

    def __init__(
        self, run_name: str, workflow_name: str | None = None, df_mode: str = "disk"
    ):
        from protzilla.disk_operator import DiskOperator  # to avoid a circular import

        self.run_name = run_name
        self.workflow_name = workflow_name

        self.disk_operator = DiskOperator(run_name, workflow_name)
        self.steps = StepManager()
        self.df_mode = df_mode

        if run_name in get_available_run_names():
            self._run_read()
        elif workflow_name:
            self._workflow_read()
        else:
            raise ValueError(
                f"No run named {run_name} has been found and no workflow has been provided. Please reference an existing run or provide a workflow to create a new one."
            )

    def __repr__(self):
        return f"Run({self.run_name}) with {len(self.steps.all_steps)} steps."

    def _run_read(self):
        self.steps = self.disk_operator.read_run()

    def _run_write(self):
        self.disk_operator.write_run(self.steps)

    def _workflow_read(self):
        self.steps = self.disk_operator.read_workflow()

    def _workflow_write(self):
        self.disk_operator.export_workflow(self.steps)

    @auto_save
    def step_add(self, step: Step, step_index: int | None = None):
        self.steps.add_step(step, step_index)

    @auto_save
    def step_remove(self, step: Step | None = None, step_index: int | None = None):
        self.steps.remove_step(step=step, step_index=step_index)

    @auto_save
    def step_calculate(self, inputs: dict | None = None):
        self.steps.current_step.calculate(self.steps, inputs)

    @auto_save
    def step_next(self):
        if self.steps.current_step_index < len(self.steps.all_steps) - 1:
            self.steps.current_step_index += 1
        else:
            logging.warning("Cannot go forward from the last step")

    @auto_save
    def step_previous(self):
        if self.steps.current_step_index > 0:
            self.steps.current_step_index -= 1
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
    def current_plots(self) -> Plots | None:
        return self.steps.current_step.plots

    @property
    def current_outputs(self):
        return self.steps.current_step.output

    @property
    def current_step(self):
        return self.steps.current_step
