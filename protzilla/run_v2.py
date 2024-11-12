from __future__ import annotations

import logging
import threading
import traceback

import os
import shutil

import protzilla.constants.paths as paths
from protzilla.steps import Messages, Output, Plots, Step
from protzilla.utilities import format_trace


def get_available_run_names() -> list[str]:
    if not paths.RUNS_PATH.exists():
        return []
    return [
        directory.name
        for directory in paths.RUNS_PATH.iterdir()
        if not directory.name.startswith(".")
    ]

def delete_run_folder(run_name) -> None:
    path = os.path.join(paths.RUNS_PATH, run_name)

    if os.path.isdir(path):
        shutil.rmtree(path)


class Run:
    class ErrorHandlingContextManager:
        def __init__(self, run):
            self.run = run

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, tb):
            if exc_type:
                formatted_trace = format_trace(traceback.format_exception(exc_value))
                if self.run.steps.current_step is not None:
                    self.run.steps.current_step.messages.append(
                        dict(
                            level=logging.ERROR,
                            msg=(
                                f"An error occurred: {exc_value.__class__.__name__}: {exc_value}."
                                f"Please check your parameters or report a potential programming issue if this is unexpected."
                            ),
                            trace=formatted_trace,
                        )
                    )
                return True

    def error_handling(func):
        """
        Decorator to handle errors in the run, will log the errors.
        :return:
        """

        def wrapper(self, *args, **kwargs):
            with Run.ErrorHandlingContextManager(self):
                return func(self, *args, **kwargs)

        return wrapper

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
        self.disk_operator: DiskOperator = DiskOperator(run_name, workflow_name)

        if run_name in get_available_run_names():
            self._run_read()
        elif workflow_name:
            self.df_mode = df_mode
            self._workflow_read()
        else:
            raise ValueError(
                f"No run named {run_name} has been found and no workflow has been provided. Please reference an existing run or provide a workflow to create a new one."
            )

    def __repr__(self):
        return f"Run({self.run_name}) with {len(self.steps.all_steps)} steps."

    @error_handling
    def _run_read(self) -> None:
        self.steps = self.disk_operator.read_run()
        self.steps.disk_operator = self.disk_operator
        self.df_mode = self.steps.df_mode

    @error_handling
    def _run_write(self) -> None:
        self.disk_operator.write_run(self.steps)

    @property
    def run_path(self) -> str:
        return self.disk_operator.run_dir

    @error_handling
    @auto_save
    def _workflow_read(self) -> None:
        self.steps = self.disk_operator.read_workflow()

    @error_handling
    def _workflow_export(self, workflow_name: str | None = None) -> None:
        if workflow_name:
            self.workflow_name = workflow_name
        self.disk_operator.export_workflow(self.steps, self.workflow_name)

    @error_handling
    @auto_save
    def step_add(self, step: Step, step_index: int | None = None) -> None:
        self.steps.add_step(step)

    @error_handling
    @auto_save
    def step_remove(
        self,
        step: Step | None = None,
        step_index: int | None = None,
        section: str | None = None,
    ) -> None:
        self.steps.remove_step(step=step, step_index=step_index, section=section)

    @error_handling
    @auto_save
    def step_calculate(self, inputs: dict | None = None) -> None:
        self.steps.current_step.calculate(self.steps, inputs)

    @error_handling
    @auto_save
    def step_plot(self) -> None:
        self.steps.current_step.plot()

    @error_handling
    @auto_save
    def step_next(self) -> None:
        self.steps.next_step()

    @error_handling
    def step_previous(self) -> None:
        self.steps.previous_step()

    @error_handling
    def step_goto(self, step_index: int, section: str) -> None:
        self.steps.goto_step(step_index, section)

    @error_handling
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
