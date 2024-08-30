from __future__ import annotations

import traceback
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml
from plotly.io import read_json, write_json

import protzilla.utilities as utilities
from protzilla.constants import paths, colors, text
from protzilla.constants.protzilla_logging import logger
from protzilla.steps import Messages, Output, Plots, Step, StepManager

try:
    from django.conf import settings

    DEBUG_MODE = settings.DEBUG
except ImportError:
    DEBUG_MODE = False


class ErrorHandler:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            if issubclass(exc_type, FileNotFoundError):
                logger.error(f"File not found: {exc_val}")
            elif issubclass(exc_type, PermissionError):
                logger.error(f"Permission denied: {exc_val}")
            if DEBUG_MODE:
                traceback.print_exception(exc_type, exc_val, exc_tb)
            return False
        return True


class YamlOperator:
    @staticmethod
    def read(file_path: Path):
        with ErrorHandler():
            with open(file_path, "r") as file:
                logger.info(f"Reading yaml from {file_path}")
                return yaml.safe_load(file)

    @staticmethod
    def write(file_path: Path, data: dict):
        with ErrorHandler():
            if not file_path.exists():
                if not file_path.parent.exists():
                    logger.info(
                        f"Parent directory {file_path.parent} did not exist and was created"
                    )
                    file_path.parent.mkdir(parents=True)
            with open(file_path, "w") as file:
                yaml.dump(data, file)


class DataFrameOperator:
    @staticmethod
    def read(file_path: Path):
        with ErrorHandler():
            logger.info(f"Reading dataframe from {file_path}")
            return pd.read_csv(file_path)

    @staticmethod
    def write(file_path: Path, dataframe: pd.DataFrame):
        with ErrorHandler():
            if file_path.exists():
                logger.warning(
                    f"Skipping writing dataframe to {file_path}, valid file already exists"
                )
                return
            logger.info(f"Writing dataframe to {file_path}")
            dataframe.to_csv(file_path, index=False)


RUN_FILE = "run.yaml"


@dataclass
class KEYS:
    # We add this here to avoid typos and signal to the developer that accessing the keys should be done through this class only
    CURRENT_STEP_INDEX = "current_step_index"
    STEPS = "steps"
    STEP_OUTPUTS = "output"
    STEP_FORM_INPUTS = "form_inputs"
    STEP_INPUTS = "inputs"
    STEP_PLOT_INPUTS = "plot_inputs"
    STEP_MESSAGES = "messages"
    STEP_PLOTS = "plots"
    STEP_INSTANCE_IDENTIFIER = "instance_identifier"
    STEP_TYPE = "type"
    DF_MODE = "df_mode"


def set_color(steps_run):
    color_value = steps_run['form_inputs']['colors']
    if color_value and (color_value != "custom"):
        colors.get_color_sequence(color_value)
    elif color_value == "custom":
        custom_color_str = steps_run['form_inputs']['custom_colors']
        colors.set_custom_sequence(custom_color_str)


def set_text_parameters(steps_run):
    enhanced_reading = steps_run['form_inputs']['enhanced_reading']
    if enhanced_reading:
        text.get_text_parameters(enhanced_reading)


class DiskOperator:
    def __init__(self, run_name: str, workflow_name: str):
        self.run_name = run_name
        self.workflow_name = workflow_name
        self.yaml_operator = YamlOperator()
        self.dataframe_operator = DataFrameOperator()

    def read_run(self, file: Path | None = None) -> StepManager:
        with ErrorHandler():
            run = self.yaml_operator.read(file or self.run_file)
            step_manager = StepManager()
            step_manager.df_mode = run.get(KEYS.DF_MODE, "disk")
            for step_data in run[KEYS.STEPS]:
                try:
                    if 'form_inputs' in step_data and 'colors' in step_data['form_inputs']:
                        set_color(step_data)
                    if 'form_inputs' in step_data and 'enhanced_reading' in step_data['form_inputs']:
                        set_text_parameters(step_data)
                    step = self._read_step(step_data, step_manager)
                except Exception as e:
                    logger.error(f"Error reading step: {e}")
                    continue
                step_manager.add_step(step)

            # this expression ensures that the current step index is within the bounds of the steps list, and at least 0
            step_manager.current_step_index = max(
                0,
                min(
                    run.get(KEYS.CURRENT_STEP_INDEX, 0), len(step_manager.all_steps) - 1
                ),
            )
            return step_manager

    def write_run(self, step_manager: StepManager) -> None:
        with ErrorHandler():
            if not self.run_dir.exists():
                self.run_dir.mkdir(parents=True, exist_ok=True)
            if not self.dataframe_dir.exists():
                self.dataframe_dir.mkdir(parents=True, exist_ok=True)
            self.clean_dataframes_dir(step_manager)
            run = {}
            run[KEYS.CURRENT_STEP_INDEX] = step_manager.current_step_index
            run[KEYS.DF_MODE] = step_manager.df_mode
            run[KEYS.STEPS] = []
            for step in step_manager.all_steps:
                run[KEYS.STEPS].append(self._write_step(step))
            self.yaml_operator.write(self.run_file, run)

    def read_workflow(self) -> StepManager:
        return self.read_run(self.workflow_file)

    def export_workflow(self, step_manager: StepManager, workflow_name: str) -> None:
        self.workflow_name = workflow_name
        workflow = {}
        workflow[KEYS.STEPS] = []
        workflow[KEYS.DF_MODE] = step_manager.df_mode
        with ErrorHandler():
            for step in step_manager.all_steps:
                step_data = self._write_step(step, workflow_mode=True).copy()
                inputs = step_data.get(KEYS.STEP_INPUTS, {}).items()
                inputs_to_write = {}
                for input_key, input_value in inputs:
                    if not (
                            isinstance(input_value, pd.DataFrame)
                            or utilities.check_is_path(input_value)
                    ):
                        inputs_to_write[input_key] = input_value

                step_data[KEYS.STEP_INPUTS] = inputs_to_write
                workflow[KEYS.STEPS].append(step_data)
            self.yaml_operator.write(self.workflow_file, workflow)

    def check_file_validity(self, file: Path, steps: StepManager) -> bool:
        """
        Check if the file is still valid, i.e. if it is still needed or if it can be deleted.
        :param file: The file to check
        :param steps: the current StepManager object
        :return: whether the file is valid
        """
        # if we are writing the run, chances are the outputs of the current step
        # have recently been (re)calculcated, therefore invalidating the existing file
        if steps.current_step.instance_identifier in file.name:
            return False
        return any(
            step.instance_identifier in file.name and step.finished
            for step in steps.all_steps
        )

    def clean_dataframes_dir(self, steps: StepManager) -> None:
        with ErrorHandler():
            for file in self.dataframe_dir.iterdir():
                if not self.check_file_validity(file, steps):
                    logger.warning(f"Deleting dataframe {file}")
                    file.unlink()

    def clear_upload_dir(self) -> None:
        # TODO in general our way of handling file uploads is kind of non-straightforward, maybe we should switch
        # to directly using the FileUpload provided by Django instead of the work-around with the path of the upload as a str
        if not paths.UPLOAD_PATH.exists():
            return
        with ErrorHandler():
            upload_dir = paths.UPLOAD_PATH
            for file in upload_dir.iterdir():
                file.unlink()

    def _read_step(self, step_data: dict, steps: StepManager) -> Step:
        from protzilla.stepfactory import StepFactory

        with ErrorHandler():
            step = StepFactory.create_step(
                step_type=step_data.get(KEYS.STEP_TYPE),
                steps=steps,
                instance_identifier=step_data.get(KEYS.STEP_INSTANCE_IDENTIFIER),
            )
            step.inputs = step_data.get(KEYS.STEP_INPUTS, {})
            if step.section == "data_preprocessing":
                step.plot_inputs = step_data.get(KEYS.STEP_PLOT_INPUTS, {})
            step.messages = Messages(step_data.get(KEYS.STEP_MESSAGES, []))
            step.output = self._read_outputs(step_data.get(KEYS.STEP_OUTPUTS, {}))
            step.plots = self._read_plots(step_data.get(KEYS.STEP_PLOTS, []))
            step.form_inputs = step_data.get(KEYS.STEP_FORM_INPUTS, {})
            return step

    def _write_step(self, step: Step, workflow_mode: bool = False) -> dict:
        with ErrorHandler():
            step_data = {}
            if step.section == "data_preprocessing":
                step_data[KEYS.STEP_PLOT_INPUTS] = sanitize_inputs(step.plot_inputs)
            step_data[KEYS.STEP_TYPE] = step.__class__.__name__
            step_data[KEYS.STEP_INSTANCE_IDENTIFIER] = step.instance_identifier
            step_data[KEYS.STEP_FORM_INPUTS] = sanitize_inputs(step.form_inputs)
            if not workflow_mode:
                step_data[KEYS.STEP_INPUTS] = sanitize_inputs(step.inputs)
                step_data[KEYS.STEP_PLOTS] = self._write_plots(
                    step.instance_identifier, step.plots
                )
                step_data[KEYS.STEP_OUTPUTS] = self._write_output(
                    instance_identifier=step.instance_identifier, output=step.output
                )
                step_data[KEYS.STEP_MESSAGES] = step.messages.messages
            return step_data

    def _read_outputs(self, output: dict) -> Output:
        with ErrorHandler():
            step_output = {}
            for key, value in output.items():
                if isinstance(value, str) and Path(value).exists():
                    step_output[key] = self.dataframe_operator.read(value)
                else:
                    step_output[key] = value
            return Output(step_output)

    def _write_output(self, instance_identifier: str, output: Output) -> dict:
        with ErrorHandler():
            output_data = {}
            for key, value in output:
                if isinstance(value, pd.DataFrame):
                    file_path = self.dataframe_dir / f"{instance_identifier}_{key}.csv"
                    self.dataframe_operator.write(file_path, value)
                    output_data[key] = str(file_path)
                else:
                    output_data[key] = value
            return output_data

    def _read_plots(self, plots: dict) -> Plots:
        if plots:
            figures = []
            for plot in plots.values():
                figures.append(read_json(plot))
            return Plots(figures)
        return Plots([])

    def _write_plots(self, instance_identifier: str, plots: Plots) -> dict:
        with ErrorHandler():
            plots_data = {}
            for i, plot in enumerate(plots):
                file_path = self.plot_dir / f"{instance_identifier}_plot{i}.json"
                self.plot_dir.mkdir(parents=True, exist_ok=True)
                if not isinstance(
                        plot, bytes
                ):  # TODO the data integration plots are of type byte, and therefore cannot be written using this methodology
                    write_json(plot, file_path)
                    plot.write_image(str(file_path).replace(".json", ".png"))
                    plots_data[i] = str(file_path)
            return plots_data

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


def sanitize_inputs(inputs: dict) -> dict:
    """
    Remove dataframes and paths from inputs.

    :param inputs: The inputs to sanitize
    :return: The sanitized inputs
    """
    return {
        key: value
        for key, value in inputs.items()
        if type(value) != pd.DataFrame and not utilities.check_is_path(value)
    }
