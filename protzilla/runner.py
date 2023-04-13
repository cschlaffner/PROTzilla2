import logging
import sys

from .run import Run
from .utilities.random import random_string

# from .constants.paths import PROJECT_PATH

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Runner:
    def __init__(self, args):
        print("args:", args)
        self.args = args
        self.run_name = (
            args.name if args.name is not None else f"runner_{random_string()}"
        )
        self.df_mode = args.dfMode if args.dfMode is not None else "disk"
        self.run = Run.create(
            run_name=self.run_name,
            workflow_config_name=self.args.workflow,
            df_mode=self.df_mode,
        )

        # print(self.run.workflow_config.items())
        # print()
        # for section, steps in self.run.workflow_config["sections"].items():
        #     for step in steps["steps"]:
        #         for param in step["parameters"]:
        #             print(section, step, param)

        self.compute_workflow()

    def compute_workflow(self):
        print("\n\n------ compute workflow\n")
        for section, steps in self.run.workflow_config["sections"].items():
            for step in steps["steps"]:
                logging.info(
                    f"performing step: {section, step['name'], step['method']}"
                )
                if section == "importing":
                    self._importing(section, step)
                    self.run.next_step(f"{self.run.current_workflow_location()}")
                elif section == "data_analysis":
                    logging.warning("data_analysis not implemented yet")
                    exit(0)
                else:
                    logging.log(
                        0, f"performing step: {section, step['name'], step['method']}"
                    )
                    self.run.perform_calculation_from_location(
                        section, step["name"], step["method"], step["parameters"]
                    )

                    if self.args.allPlots:
                        params = dict()
                        if "graphs" in step:
                            print(step["graphs"])
                            params = self._serialize_graphs(step["graphs"])

                        print(params)
                        if "transformation" in step["name"]:
                            pass
                        self.run.create_plot_from_location(
                            *self.run.current_workflow_location(),
                            parameters=params,
                        )
                        for plot in self.run.plots:
                            plot.show()
                    self.run.next_step(f"{self.run.current_workflow_location()}")
                    # assert False

    def _importing(self, section, step):
        if step["name"] == "ms_data_import":
            params = step["parameters"]
            params["file_path"] = self.args.msDataPath
            self._perform_step(section, step, params)
            logging.log(0, "imported MS Data")

        elif step["name"] == "metadata_import":
            if self.args.metaDataPath is None:
                raise ValueError(
                    f"MetadataPath (--metaDataPath) is not specified, "
                    f"but is required for {step['name']}"
                )
            params = step["parameters"]
            params["file_path"] = self.args.metaDataPath
            self._perform_step(section, step, params)
            logging.log(0, "imported Meta Data")

        else:
            raise ValueError(f"Cannot find step with name {step['name']} in importing")

    def _perform_step(self, section, step, params):
        self.run.perform_calculation_from_location(
            section, step["name"], step["method"], params
        )

    def _serialize_graphs(self, graphs):
        return {k: v for graph in graphs for k, v in graph.items()}
