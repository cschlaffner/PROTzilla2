from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from protzilla.constants.paths import RUNS_PATH
from protzilla.data_preprocessing.imputation import by_min_per_protein
from protzilla.importing.ms_data_import import max_quant_import


class RunNew:
    RUN_PATH = Path("/home/henning/BP2023BR1/PROTzilla2/example")

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
        self.steps.current_step.calculate(self.steps.previous_steps, inputs)
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
    def run_disk_path(self):
        assert self.run_name is not None
        return RUNS_PATH / self.run_name


class StepManager:
    def __repr__(self):
        return f"Importing: {self.importing}\nData Preprocessing: {self.data_preprocessing}\nData Analysis: {self.data_analysis}\nData Integration: {self.data_integration}"

    def __init__(self, steps: list[Step] = None):
        self.importing = []
        self.data_preprocessing = []
        self.data_analysis = []
        self.data_integration = []
        self.current_step_index = 0

        if steps is not None:
            for step in steps:
                self.add_step(step)

    @property
    def all_steps(self):
        return (
            self.importing
            + self.data_preprocessing
            + self.data_analysis
            + self.data_integration
        )

    @property
    def previous_steps(self):
        return self.all_steps[: self.current_step_index]

    @property
    def current_step(self):
        return self.all_steps[self.current_step_index]

    def add_step(self, step, index=None):
        # TODO add support for index
        if step.section == "importing":
            self.importing.append(step)
        elif step.section == "data_preprocessing":
            self.data_preprocessing.append(step)
        elif step.section == "data_analysis":
            self.data_analysis.append(step)
        elif step.section == "data_integration":
            self.data_integration.append(step)
        else:
            raise ValueError(f"Unknown section {step.section}")

    def remove_step(self, step: Step, step_index: int = None):
        if step_index is not None:
            if step_index < self.current_step_index:
                self.current_step_index -= 1
            self.all_steps.pop(step_index)
        else:
            if step in self.all_steps:
                self.all_steps.remove(step)
            else:
                raise ValueError(f"Step {step} not found in steps")


class DiskOperator:
    @dataclass
    class KEYS:
        # We add this here to avoid typos and signal to the developer that accessing the keys should be done through this class only
        RUN_NAME = "run_name"
        CURRENT_STEP_INDEX = "current_step_index"
        STEPS = "steps"
        STEP_OUTPUTS = "output"
        STEP_INPUTS = "inputs"
        STEP_MESSAGES = "messages"
        STEP_INDEX = "step_index"

    def __init__(self):
        self.step_dictionary = None

    def read_step_index(self, base_dir: Path) -> int:
        run_file = base_dir / "run.yaml"
        with open(run_file, "r") as file:
            data = yaml.safe_load(file)
            return data[self.KEYS.CURRENT_STEP_INDEX]

    def read_step(self, step_type: str, step_data: dict, base_dir: Path) -> Step:
        try:
            step = StepFactory.create_step(step_type)
            step.inputs = step_data[self.KEYS.STEP_INPUTS]
            step.messages = Messages(step_data[self.KEYS.STEP_MESSAGES])

            if step_data[self.KEYS.STEP_OUTPUTS]:
                step.output = self.read_outputs(step_data[self.KEYS.STEP_OUTPUTS])
            return step
        except Exception as e:
            logging.error(f"Error while reading step {step_type}: {e}")
            raise

    def read_outputs(self, output: dict) -> Output:
        step_output = {}
        for key, value in output.items():
            if isinstance(value, str):
                if Path(value).exists():
                    try:
                        step_output[key] = pd.read_csv(Path(value))
                    except Exception as e:
                        logging.error(f"Error while reading output {key}: {e}")
                        step_output[key] = value
                else:
                    logging.warning(f"Output file {value} does not exist")
            else:
                output[key] = value
        return Output(step_output)

    def read_steps(self, base_dir: Path) -> StepManager:
        run_file = base_dir / "run.yaml"
        with open(run_file, "r") as file:
            data = yaml.safe_load(file)
            steps = [None] * len(data[self.KEYS.STEPS])
            for step_type, step_data in data[self.KEYS.STEPS].items():
                step_index = step_data[self.KEYS.STEP_INDEX]
                step = self.read_step(step_type, step_data, base_dir)
                steps[step_index] = step
            return StepManager(steps)

    def write_run(self, run: RunNew):
        run_data = {
            self.KEYS.RUN_NAME: run.run_name,
            self.KEYS.CURRENT_STEP_INDEX: run.steps.current_step_index,
            self.KEYS.STEPS: {
                step.__class__.__name__: self.save(step, index, run.run_disk_path)
                for index, step in enumerate(run.steps.all_steps)
            },
        }
        run_file = run.run_disk_path / "run.yaml"
        with open(run_file, "w") as file:
            yaml.dump(run_data, file)
        logging.info(f"Run {run.run_name} saved to {run_file}")

    def save(self, step: Step, step_index: int, base_dir: Path) -> dict:
        self.step_dictionary = {
            self.KEYS.STEP_INDEX: step_index,
            self.KEYS.STEP_INPUTS: {},
            self.KEYS.STEP_OUTPUTS: {},
            self.KEYS.STEP_MESSAGES: {},
        }
        if not step.output.is_empty:
            self.write_outputs(step, base_dir)

        if step.inputs:
            self.write_inputs(step)
        return self.step_dictionary

    def write_outputs(self, step: Step, base_dir: Path):
        dataframe_dir = base_dir / "dataframes"
        for key, value in step.output.output.items():
            if isinstance(value, pd.DataFrame):
                try:
                    dataframe_dir.mkdir(parents=True, exist_ok=True)
                    file_path = dataframe_dir / f"{step.__class__.__name__}.{key}.csv"
                    value.to_csv(file_path, index=False)
                    self.step_dictionary[self.KEYS.STEP_OUTPUTS][key] = str(file_path)
                except Exception as e:
                    self.step_dictionary[self.KEYS.STEP_OUTPUTS][key] = None
                    logging.error(f"Error while writing output {key}: {e}")

            else:
                self.step_dictionary[self.KEYS.STEP_OUTPUTS][key] = value

    def write_inputs(self, step: Step):
        for key, value in step.inputs.items():
            self.step_dictionary[self.KEYS.STEP_INPUTS][key] = value

    def write_messages(self, step: Step):
        for message in step.messages:
            self.step_dictionary[self.KEYS.STEP_MESSAGES].append(message)


class StepFactory:
    @staticmethod
    def create_step(step_type: str) -> Step:
        if step_type == "MaxQuantImport":
            return MaxQuantImport()
        elif step_type == "ImputationMinPerProtein":
            return ImputationMinPerProtein()
        else:
            raise ValueError(f"Unknown step type {step_type}")


class Step:
    def __init__(self):
        self.inputs: dict = None
        self.messages: Messages = None
        self.output: Output = None

    def __repr__(self):
        return self.__class__.__name__

    def calculate(self):
        raise NotImplementedError

    def validate_inputs(self, required_keys: list[str]):
        for key in required_keys:
            if key not in self.inputs:
                raise ValueError(f"Missing input {key} in inputs")

    def validate_outputs(self, required_keys: list[str]):
        for key in required_keys:
            if key not in self.output.output:
                raise ValueError(f"Missing output {key} in output")


class MaxQuantImport(Step):
    section = "importing"
    step = "msdataimport"
    method = "max_quant_import"

    def calculate(self, previous_steps: list[Step], inputs: dict = None):
        if inputs is not None:
            self.inputs = inputs

        # validate the inputs for the step
        self.validate_inputs(["file_path", "map_to_uniprot", "intensity_name"])

        # calculate the step
        output, messages = max_quant_import(None, **self.inputs)

        # store the output and messages
        self.output = Output({"intensity_df": output})
        self.messages = Messages(messages)

        # validate the output
        self.validate_outputs(["intensity_df"])


class ImputationMinPerProtein(Step):
    section = "data_preprocessing"
    step = "imputation"
    method = "by_min_per_protein"

    def calculate(self, previous_steps: list[Step], inputs: dict = None):
        if inputs is not None:
            self.inputs = inputs

        # validate the inputs for the step
        self.validate_inputs(["shrinking_value"])
        if previous_steps[-1].output.is_empty:
            raise ValueError("No data to impute")
        intensity_df = previous_steps[-1].output.intensity_df

        # calculate the step
        output, messages = by_min_per_protein(intensity_df, **self.inputs)

        # store the output and messages
        self.output = Output({"intensity_df": output})
        self.messages = Messages(messages)

        # validate the output
        self.validate_outputs(["intensity_df"])


class Output:
    def __init__(self, output: dict):
        self.output = output

    @property
    def intensity_df(self):
        if "intensity_df" in self.output:
            return self.output["intensity_df"]
        else:
            return None

    @property
    def is_empty(self):
        return len(self.output) == 0 or all(
            value is None for value in self.output.values()
        )


class Messages:
    def __init__(self, messages: list[dict]):
        self.messages = messages


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
