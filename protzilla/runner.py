import logging
import os
from pathlib import Path

from .constants.paths import RUNS_PATH
from .run_helper import log_messages
from .run_v2 import Run
from .utilities import random_string


class Runner:
    """
    Intended for use with runner_cli.py-Script (at PROTzilla2/runner_cli.py).
    Then .compute_workflow() is called, the workflow, with all it's steps will be
    executed. If specified, the Plots will be saved to <run_name>/plots.
    Results can be viewed after completion in the PROTzilla UI via `Continue Run`.

    :ivar workflow: str, name of workflow in user_data/workflows
    :ivar ms_data_path: str, path to MS-Data
    :ivar meta_data_path: str, path to Meta-Data
    :ivar run_name: str, name of run to be created
    :ivar df_mode: str, keep DFs in memory or write on disk, default: disk
    :ivar all_plots: bool, if set all plots will be generated and save in the
    :ivar verbose: bool, logs this input dict (args), default: false
    """

    def __init__(
        self,
        workflow: str,
        ms_data_path: str,
        meta_data_path: str | None,
        peptides_path: str | None,
        run_name: str | None,
        df_mode: str | None = "disk",
        all_plots: bool = False,
        verbose: bool = False,
    ):
        logging.basicConfig(level=logging.INFO)

        self.verbose = verbose
        if self.verbose:
            logging.info(f"Parsed arguments: {locals()}")

        self.ms_data_path = ms_data_path
        self.meta_data_path = meta_data_path
        self.peptides_path = peptides_path
        self.df_mode = df_mode if df_mode is not None else "disk"
        self.workflow = workflow

        self.run_name = (
            run_name.strip()
            if run_name is not None and run_name.strip() is not None
            else f"runner_{random_string()}"
        )

        if os.path.exists(Path(f"{RUNS_PATH}/{self.run_name}")):
            self._overwrite_run_prompt()
            print("\n\n")

        self.run = Run(
            run_name=self.run_name,
            workflow_name=self.workflow,
            df_mode=self.df_mode,
        )
        logging.info(f"Run {self.run_name} created at {self.run.run_path}")

        self.all_plots = all_plots
        self.plots_path = Path(f"{self.run.run_path}/plots")
        self.plots_path.mkdir(parents=True)
        logging.info(f"Saving plots at {self.plots_path}")

        log_messages(self.run.current_messages)
        self.run.current_messages.clear()

    def compute_workflow(self):
        logging.info("------ computing workflow\n")
        for step in self.run.steps.all_steps:
            logging.info(f"performing step: {*self.run.steps.current_location,}")
            if step.section == "importing":
                self._insert_commandline_inputs(step)
            self._perform_current_step()
            if self.all_plots and step.section == "data_preprocessing":
                step.plot()
            if step.plots:
                self._save_plots_html(step)

            self.run.step_next()

            log_messages(self.run.current_messages)
            self.run.current_messages.clear()
        self.run._run_write()

    def _insert_commandline_inputs(self, step):
        if step.operation == "msdataimport":
            step.inputs["file_path"] = self.ms_data_path

        elif step.operation == "metadataimport":
            if self.meta_data_path is None:
                raise ValueError(
                    f"meta_data_path (--meta_data_path=<path/to/data) is not specified,"
                    f" but is required for {step['name']}"
                )
            step.inputs["file_path"] = self.meta_data_path
        elif step.operation == "peptideimport":
            if self.peptides_path is None:
                raise ValueError(
                    f"peptide_path (--peptide_path=<path/to/data>) is not specified, "
                    f"but is required for {step['name']}"
                )
            step.inputs["file_path"] = self.peptides_path
        else:
            raise ValueError(f"Cannot find step with name {step['name']} in importing")

    def _perform_current_step(self, params=None):
        self.run.current_step.calculate(self.run.steps, params)

    def _save_plots_html(self, step):
        for i, plot in enumerate(step.plots):
            plot_path = f"{self.plots_path}/{self.run.step_index}-{step.section}-{step['name']}-{step['method']}-{i}.html"
            plot.write_html(plot_path)

    def _overwrite_run_prompt(self):
        answer = input(
            "A run with the this name already exists. "
            "Do you want to overwrite it? [y/n]: "
        )
        if answer in ["n", "no"]:
            print("exiting")
            exit(0)
        elif answer in ["y", "yes"]:
            return
        else:
            print("\n\n----- Please answer with one of the given options")
            self._overwrite_run_prompt()


def _serialize_graphs(graphs):
    return {k: v for graph in graphs for k, v in graph.items()}
