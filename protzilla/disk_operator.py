from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

import protzilla.utilities as utilities
from protzilla.constants import paths
from protzilla.steps import Messages, Output, Step, StepManager


class YamlOperator:
    @staticmethod
    def read(file_path: Path):
        with open(file_path, "r") as file:
            return yaml.safe_load(file)

    @staticmethod
    def write(file_path: Path, data: dict):
        if not file_path.exists():
            if not file_path.parent.exists():
                file_path.parent.mkdir(parents=True)
            file_path.touch()
            logging.warning(f"File {file_path} did not exist and was created")
        with open(file_path, "w") as file:
            yaml.dump(data, file)


class JsonOperator:
    @staticmethod
    def read(file_path: Path):
        with open(file_path, "r") as file:
            return json.load(file)


class DataFrameOperator:
    @staticmethod
    def read(file_path: Path):
        return pd.read_csv(file_path)

    @staticmethod
    def write(file_path: Path, dataframe: pd.DataFrame):
        dataframe.to_csv(file_path, index=False)


RUN_FILE = "run.yaml"


@dataclass
class KEYS:
    # We add this here to avoid typos and signal to the developer that accessing the keys should be done through this class only
    CURRENT_STEP_INDEX = "current_step_index"
    STEPS = "steps"
    STEP_OUTPUTS = "output"
    STEP_INPUTS = "inputs"
    STEP_MESSAGES = "messages"
    STEP_PLOTS = "plots"
    STEP_INSTANCE_IDENTIFIER = "instance_identifier"
    STEP_TYPE = "type"


class DiskOperator:
    def __init__(self, run_name: str, workflow_name: str):
        self.run_name = run_name
        self.workflow_name = workflow_name
        self.yaml_operator = YamlOperator()
        self.json_operator = JsonOperator()
        self.dataframe_operator = DataFrameOperator()

    def read_run(self, file: Path = None) -> StepManager:
        run = self.yaml_operator.read(file or self.run_file)
        step_manager = StepManager()
        for step_data in run[KEYS.STEPS]:
            step = self._read_step(step_data)
            step_manager.add_step(step)
        step_manager.current_step_index = run.get(KEYS.CURRENT_STEP_INDEX, 0)
        return step_manager

    def write_run(self, step_manager: StepManager) -> None:
        if not self.run_dir.exists():
            self.run_dir.mkdir(parents=True)
        if not self.dataframe_dir.exists():
            self.dataframe_dir.mkdir(parents=True)
        run = {}
        run[KEYS.CURRENT_STEP_INDEX] = step_manager.current_step_index
        run[KEYS.STEPS] = []
        for step in step_manager.all_steps:
            # we use the name of the class in python, as we decided is removes redundancy has more advantages over a method_id
            run[KEYS.STEPS].append(self._write_step(step))
        self.yaml_operator.write(self.run_file, run)

    def read_workflow(self) -> StepManager:
        # we can completely reuse the read_run, as the structure is the same
        return self.read_run(self.workflow_file)

    def export_workflow(self, step_manager: StepManager, workflow_name: str) -> None:
        self.workflow_name = workflow_name
        workflow = {}
        workflow[KEYS.STEPS] = {}
        for step in step_manager.all_steps:
            step_data = self._write_step(step, workflow_mode=True).copy()
            inputs = step_data.get(KEYS.STEP_INPUTS, {}).items()
            inputs_to_write = {}
            for input_key, input_value in inputs:
                if not isinstance(
                    input_value, pd.DataFrame
                ) and not utilities.check_is_path(input_value):
                    inputs_to_write[input_key] = input_value

            workflow[KEYS.STEPS][step.__class__.__name__] = step_data
            step_data[KEYS.STEP_INPUTS] = inputs_to_write
        self.yaml_operator.write(self.workflow_file, workflow)

    def _read_step(self, step_data: dict) -> Step:
        from protzilla.stepfactory import StepFactory

        step_type = step_data.get(KEYS.STEP_TYPE)
        step = StepFactory.create_step(step_type)
        step.instance_identifier = step_data.get(
            KEYS.STEP_INSTANCE_IDENTIFIER, step_type
        )  # here we default to the class name if no instance identifier is provided TODO
        step.inputs = step_data.get(KEYS.STEP_INPUTS, {})
        step.messages = Messages(step_data.get(KEYS.STEP_MESSAGES, []))
        step.output = self._read_outputs(step_data.get(KEYS.STEP_OUTPUTS, {}))
        step.plots = self._read_plots(
            step_data.get(KEYS.STEP_PLOTS, [])
        )  # TODO is [] the correct default?
        return step

    def _write_step(self, step: Step, workflow_mode: bool = False) -> dict:
        step_data = {}
        step_data[KEYS.STEP_INPUTS] = step.inputs
        step_data[KEYS.STEP_TYPE] = step.__class__.__name__
        step_data[KEYS.STEP_INSTANCE_IDENTIFIER] = step.instance_identifier
        if not workflow_mode:
            step_data[KEYS.STEP_OUTPUTS] = self._write_output(
                step_name=step.__class__.__name__, output=step.output
            )
            step_data[KEYS.STEP_MESSAGES] = step.messages.messages
        return step_data

    def _read_outputs(self, output: dict) -> Output:
        step_output = {}
        for key, value in output.items():
            if isinstance(value, str):
                if Path(value).exists():
                    try:
                        step_output[key] = self.dataframe_operator.read(value)
                    except Exception as e:
                        logging.error(f"Error while reading output {key}: {e}")
                        step_output[key] = value
                else:
                    logging.warning(f"Output file {value} does not exist")
            else:
                output[key] = value
        return Output(step_output)

    def _write_output(self, step_name: str, output: Output) -> dict:
        output_data = {}
        for key, value in output:
            if isinstance(value, pd.DataFrame):
                file_path = self.dataframe_dir / f"{step_name}_{key}.csv"
                self.dataframe_operator.write(file_path, value)
                output_data[key] = str(file_path)
            else:
                output_data[key] = value
        return output_data

    def _read_plots(self, plots: list) -> list:
        if plots:
            raise NotImplementedError  # TODo
        return []

    def _write_plots(self, plots: list) -> dict:
        raise NotImplementedError  # TODO

    @property
    def run_dir(self):
        return paths.RUNS_PATH / self.run_name

    @property
    def run_file(self) -> Path:
        return self.run_dir / RUN_FILE

    @property
    def workflow_file(self) -> Path:
        return paths.WORKFLOWS_PATH / f"{self.workflow_name}.yaml"

    @property
    def dataframe_dir(self) -> Path:
        return self.run_dir / "dataframes"

    @property
    def plot_dir(self) -> Path:
        return self.run_dir / "plots"
