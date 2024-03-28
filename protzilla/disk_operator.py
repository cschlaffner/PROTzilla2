from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from protzilla.constants import paths
from protzilla.steps import Messages, Output, Step, StepFactory, StepManager


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

    def _read_step(self, step_type: str, step_data: dict, base_dir: Path) -> Step:
        try:
            step = StepFactory.create_step(step_type)
            step.inputs = step_data[self.KEYS.STEP_INPUTS]
            step.messages = Messages(step_data[self.KEYS.STEP_MESSAGES])

            if step_data[self.KEYS.STEP_OUTPUTS]:
                step.output = self._read_outputs(step_data[self.KEYS.STEP_OUTPUTS])
            return step
        except Exception as e:
            logging.error(f"Error while reading step {step_type}: {e}")
            raise

    def _read_outputs(self, output: dict) -> Output:
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
                step = self._read_step(step_type, step_data, base_dir)
                steps[step_index] = step
            return StepManager(steps)

    def write_run(self, run):
        run_data = {
            self.KEYS.RUN_NAME: run.run_name,
            self.KEYS.CURRENT_STEP_INDEX: run.steps.current_step_index,
            self.KEYS.STEPS: {
                step.__class__.__name__: self.prepare_step_data(
                    step, index, run.run_disk_path
                )
                for index, step in enumerate(run.steps.all_steps)
            },
        }
        run_file = run.run_disk_path / "run.yaml"
        with open(run_file, "w") as file:
            yaml.dump(run_data, file)
        logging.info(f"Run {run.run_name} saved to {run_file}")

    def prepare_step_data(self, step: Step, step_index: int, base_dir: Path) -> dict:
        self.step_dictionary = {
            self.KEYS.STEP_INDEX: step_index,
            self.KEYS.STEP_INPUTS: {},
            self.KEYS.STEP_OUTPUTS: {},
            self.KEYS.STEP_MESSAGES: {},
        }
        if not step.output.is_empty:
            self._write_outputs(step, base_dir)

        if step.inputs:
            self._write_inputs(step)
        return self.step_dictionary

    def _write_outputs(self, step: Step, base_dir: Path):
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

    def _write_inputs(self, step: Step):
        for key, value in step.inputs.items():
            self.step_dictionary[self.KEYS.STEP_INPUTS][key] = value

    def _write_messages(self, step: Step):
        for message in step.messages:
            self.step_dictionary[self.KEYS.STEP_MESSAGES].append(message)

    @staticmethod
    def get_available_runs():
        return [path.name for path in paths.RUNS_PATH.iterdir()]

    @staticmethod
    def get_available_workflows():
        return [path.name for path in paths.WORKFLOWS_PATH.iterdir()]
