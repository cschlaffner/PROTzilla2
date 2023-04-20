import logging
import os
from pathlib import Path

from .constants.paths import RUNS_PATH
from .run import Run
from .run_helper import get_parameters
from .utilities.random import random_string
from .workflow_helper import get_defaults


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
        workflow,
        ms_data_path,
        meta_data_path,
        run_name,
        df_mode,
        all_plots,
        verbose,
    ):
        logging.basicConfig(level=logging.INFO)

        self.verbose = verbose
        if self.verbose:
            logging.info(f"Parsed arguments: {locals()}")

        self.ms_data_path = ms_data_path
        self.meta_data_path = meta_data_path
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

        self.run = Run.create(
            run_name=self.run_name,
            workflow_config_name=self.workflow,
            df_mode=self.df_mode,
        )
        logging.info(f"Run {self.run_name} created at {self.run.run_path}")

        self.all_plots = all_plots
        if self.all_plots:
            self.plots_path = Path(f"{self.run.run_path}/plots")
            self.plots_path.mkdir()
            logging.info(f"Saving plots at {self.plots_path}")

    def compute_workflow(self):
        logging.info("------ computing workflow\n")
        for section, steps in self.run.workflow_config["sections"].items():
            for step in steps["steps"]:
                if section == "importing":
                    self._importing(step)
                else:
                    logging.info(
                        f"performing step: {*self.run.current_workflow_location(),}"
                    )
                    params = get_parameters(self.run, *self.run.current_workflow_location())
                    self._perform_current_step(get_defaults(params))
                    if self.all_plots:
                        self._create_plots_for_step(section, step)
                self.run.next_step(f"{self.run.current_workflow_location()}")

    def _importing(self, step):
        if step["name"] == "ms_data_import":
            params = step["parameters"]
            params["file_path"] = self.ms_data_path
            self._perform_current_step(params)
            logging.info("imported MS Data")

        elif step["name"] == "metadata_import":
            if self.meta_data_path is None:
                raise ValueError(
                    f"MetadataPath (--meta_data_path) is not specified, "
                    f"but is required for {step['name']}"
                )
            params = step["parameters"]
            params["file_path"] = self.meta_data_path
            self._perform_current_step(params)
            logging.info("imported Meta Data")

        else:
            raise ValueError(f"Cannot find step with name {step['name']} in importing")

    def _perform_current_step(self, params):
        self.run.perform_calculation_from_location(
            *self.run.current_workflow_location(), params
        )

    def _create_plots_for_step(self, section, step):
        params = dict()
        if "graphs" in step:
            params = _serialize_graphs(step["graphs"])

        self.run.create_plot_from_location(
            *self.run.current_workflow_location(),
            parameters=params,
        )
        for i, plot in enumerate(self.run.plots):
            plot_path = f"{self.plots_path}/{self.run.step_index}-{section}-{step['name']}-{step['method']}-{i}.html"
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
