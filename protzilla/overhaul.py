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
        self.run_name = run_name
        self.steps: list[Step] = []
        self.current_step_index = 0
        self.disk_operator = DiskOperator()

    def run_write(self):
        self.disk_operator.write_run(self)

    def run_read(self, run_name: str = None):
        if run_name is None:
            run_name = self.run_name
        else:
            self.run_name = run_name

        self.steps = self.disk_operator.read_steps(self.run_disk_path)
        self.current_step_index = self.disk_operator.read_step_index(self.run_disk_path)

    def step_add(self, step: Step, step_index: int = None):
        if step_index is not None:
            self.steps.insert(step_index, step)
        else:
            self.steps.append(step)

    def step_remove(self, step_index: int = None):
        self.steps.pop(step_index)

    def step_calculate(self, inputs: dict = None):
        assert self.current_step_index < len(self.steps)
        self.current_step.calculate(self.previous_steps, inputs)
        self.current_step_index += 1

    def step_next(self):
        self.current_step_index += 1

    def step_previous(self):
        if self.current_step_index > 0:
            self.current_step_index -= 1
        else:
            logging.warning("Cannot go back from the first step")

    @property
    def run_disk_path(self):
        assert self.run_name is not None
        return RUNS_PATH / self.run_name

    @property
    def current_step(self):
        return self.steps[self.current_step_index]

    @property
    def previous_steps(self):
        return self.steps[: self.current_step_index]


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
        step = StepFactory.create_step(step_type)
        step.inputs = step_data[self.KEYS.STEP_INPUTS]
        step.messages = Messages(step_data[self.KEYS.STEP_MESSAGES])

        if step_data[self.KEYS.STEP_OUTPUTS]:
            step.output = self.read_outputs(step_data[self.KEYS.STEP_OUTPUTS])
        return step

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
                output[key] = value
        return Output(step_output)

    def read_steps(self, base_dir: Path) -> list[Step]:
        run_file = base_dir / "run.yaml"
        with open(run_file, "r") as file:
            data = yaml.safe_load(file)
            steps = [None] * len(data[self.KEYS.STEPS])
            for step_type, step_data in data[self.KEYS.STEPS].items():
                step_index = step_data[self.KEYS.STEP_INDEX]
                step = self.read_step(step_type, step_data, base_dir)
                steps[step_index] = step
            return steps

    def write_run(self, run: RunNew):
        run_data = {
            self.KEYS.RUN_NAME: run.run_name,
            self.KEYS.CURRENT_STEP_INDEX: run.current_step_index,
            self.KEYS.STEPS: {
                step.__class__.__name__: self.save(step, index, run.run_disk_path)
                for index, step in enumerate(run.steps)
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

    def calculate(self):
        raise NotImplementedError


class MaxQuantImport(Step):
    def calculate(self, previous_steps: list[Step], inputs: dict = None):
        if inputs is not None:
            self.inputs = inputs

        # prepare the inputs for the step

        # calculate the step
        output, messages = max_quant_import(None, **self.inputs)

        # store the output and messages
        self.output = Output({"intensity_df": output})
        self.messages = Messages(messages)
        self.messages = Messages(messages)


class ImputationMinPerProtein(Step):
    def calculate(self, previous_steps: list[Step], inputs: dict = None):
        if inputs is not None:
            self.inputs = inputs

        # prepare the inputs for the step
        intensity_df = previous_steps[-1].output.intensity_df

        # calculate the step
        output, messages = by_min_per_protein(intensity_df, **self.inputs)

        # store the output and messages
        self.output = Output({"intensity_df": output})
        self.messages = Messages(messages)


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
        return len(self.output) == 0


class Messages:
    def __init__(self, messages: list[dict]):
        self.messages = messages


if __name__ == "__main__":
    run = RunNew()
    # run.step_add(MaxQuantImport())
    # run.step_add(ImputationMinPerProtein())
    # run.step_calculate({"file_path": "/home/henning/BP2023BR1/PROTzilla2/example/MaxQuant_data/proteinGroups_small.txt",
    #                    "map_to_uniprot": True, "intensity_name": "Intensity"})
    # run.step_calculate({"shrinking_value": 0.5})
    # run.run_write()
    run.run_read("OVERHAUL")
    run.step_previous()
    run.step_previous()
    run.step_calculate()
    run.step_calculate()

    print("done")
