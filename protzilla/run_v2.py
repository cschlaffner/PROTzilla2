from __future__ import annotations

import logging
import threading

import protzilla.constants.paths as paths
from protzilla.steps import Messages, Output, Plots, Step, StepManager


def get_available_run_names() -> list[str]:
    return [
        directory.name
        for directory in paths.RUNS_PATH.iterdir()
        if not directory.name.startswith(".")
    ]


class Run:
    def auto_save(func):
        """
        Decorator to automatically save the run in the background after the function is called.
        """

        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            thread = threading.Thread(target=self._run_write)
            thread.daemon = True
            thread.start()
            self.steps.df_mode = self.df_mode
            self.steps.disk_operator = self.disk_operator
            return result

        return wrapper

    def __init__(
        self, run_name: str, workflow_name: str | None = None, df_mode: str = "disk"
    ):
        from protzilla.disk_operator import DiskOperator  # to avoid a circular import

        self.run_name = run_name
        self.workflow_name = workflow_name
        self.df_mode = df_mode

        self.disk_operator: DiskOperator = DiskOperator(run_name, workflow_name)
        self.steps: StepManager = StepManager(
            df_mode=self.df_mode, disk_operator=self.disk_operator
        )

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

    @auto_save
    def _run_read(self) -> None:
        self.steps = self.disk_operator.read_run()

    def _run_write(self) -> None:
        self.disk_operator.write_run(self.steps)

    @auto_save
    def _workflow_read(self) -> None:
        self.steps = self.disk_operator.read_workflow()

    def _workflow_export(self, workflow_name: str | None = None) -> None:
        if workflow_name:
            self.workflow_name = workflow_name
        self.disk_operator.export_workflow(self.steps, self.workflow_name)

    @auto_save
    def step_add(self, step: Step, step_index: int | None = None) -> None:
        self.steps.add_step(step)

    @auto_save
    def step_remove(
        self, step: Step | None = None, step_index: int | None = None
    ) -> None:
        self.steps.remove_step(step=step, step_index=step_index)

    @auto_save
    def step_calculate(self, inputs: dict | None = None) -> None:
        self.steps.current_step.calculate(self.steps, inputs)

    @auto_save
    def step_plot(self) -> None:
        self.steps.current_step.plot()

    def step_next(self) -> None:
        self.steps.next_step()

    def step_previous(self) -> None:
        if self.steps.current_step_index > 0:
            self.steps.current_step_index -= 1
        else:
            logging.warning("Cannot go back from the first step")

    @auto_save
    def step_change_method(self, new_method: str) -> None:
        self.steps.change_method(new_method)

    @property
    def current_messages(self) -> Messages:
        return self.steps.current_step.messages

    @property
    def current_plots(self) -> Plots | None:
        return self.steps.current_step.plots

    @property
    def current_outputs(self) -> Output:
        return self.steps.current_step.output

    @property
    def current_step(self) -> Step | None:
        return self.steps.current_step
