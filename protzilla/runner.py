import logging
import os
import sys
from pathlib import Path

from .constants.paths import RUNS_PATH
from .run import Run
from .utilities.random import random_string

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Runner:
    def __init__(self, args):
        if args.verbose:
            logging.info(f"Parsed arguments: {args}")
        self.args = args
        self.run_name = (
            args.name.strip()
            if args.name.strip() is not None
            else f"runner_{random_string()}"
        )
        self.df_mode = args.dfMode if args.dfMode is not None else "disk"

        if os.path.exists(RUNS_PATH / self.run_name):
            self._overwrite_run_prompt()
            print("\n\n")

        self.run = Run.create(
            run_name=self.run_name,
            workflow_config_name=self.args.workflow,
            df_mode=self.df_mode,
        )
        logging.info(f"Run {self.run_name} created at {self.run.run_path}")

        if self.args.allPlots:
            self.plots_path = Path(f"{self.run.run_path}/plots")
            self.plots_path.mkdir()
            logging.info(f"Saving plots at {self.plots_path}")

    def compute_workflow(self):
        logging.info("\n\n------ computing workflow\n")
        for section, steps in self.run.workflow_config["sections"].items():
            for step in steps["steps"]:
                if section == "importing":
                    self._importing(step)
                elif section == "data_analysis":
                    logging.warning("data_analysis not implemented yet")
                    exit(0)
                else:
                    logging.info(
                        f"performing step: {*self.run.current_workflow_location(),}"
                    )
                    self.run.perform_calculation_from_location(
                        *self.run.current_workflow_location(), step["parameters"]
                    )
                    if self.args.allPlots:
                        self._create_plots_for_step(section, step)
                self.run.next_step(f"{self.run.current_workflow_location()}")

    def _importing(self, step):
        if step["name"] == "ms_data_import":
            params = step["parameters"]
            params["file_path"] = self.args.msDataPath
            self._perform_current_step(params)
            logging.info("imported MS Data")

        elif step["name"] == "metadata_import":
            if self.args.metaDataPath is None:
                raise ValueError(
                    f"MetadataPath (--metaDataPath) is not specified, "
                    f"but is required for {step['name']}"
                )
            params = step["parameters"]
            params["file_path"] = self.args.metaDataPath
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
