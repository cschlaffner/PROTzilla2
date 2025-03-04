from __future__ import annotations

import base64
import inspect
import logging
import traceback
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Literal

import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go
from PIL import Image

from protzilla.utilities import format_trace


class Section(Enum):
    IMPORTING = "importing"
    DATA_PREPROCESSING = "data_preprocessing"
    DATA_ANALYSIS = "data_analysis"
    DATA_INTEGRATION = "data_integration"


class Step:
    section: str = None
    display_name: str = None
    operation: str = None
    method_description: str = None
    output_keys: list[str] = []
    calculation_status: Literal["complete", "outdated", "incomplete", "failed"] = "incomplete"

    def __init__(self, instance_identifier: str | None = None):
        self.form_inputs: dict = {}
        self.inputs: dict = {}
        self.output: Output = Output()
        self.filtered_datatable: dict = {}
        self.plots: Plots = Plots()
        self.messages: Messages = Messages([])
        self.instance_identifier = instance_identifier

        if self.instance_identifier is None:
            logging.warning(
                f"No instance identifier provided for step {self.__class__.__name__}, defaulting to class name."
            )
            self.instance_identifier = self.__class__.__name__

    def __repr__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__
            and self.instance_identifier == other.instance_identifier
            and self.output == other.output
        )

    def updateInputs(self, inputs: dict) -> None:
        if inputs:
            self.inputs = inputs.copy()

    def calculate(self, steps: StepManager, inputs: dict) -> bool:
        """
        Core calculation method for all steps, receives the inputs from the front-end and calculates the output.

        :param steps: The StepManager object that contains all steps
        :param inputs: These inputs will be supplied to the method. Only keys in the input_keys of the method class will actually be supplied to the method
        :return: None
        """
        stepIndex = steps.all_steps.index(self)
        previousStep = steps.all_steps[stepIndex-1]
        
        if (previousStep.calculation_status == "outdated" ):
            if not previousStep.calculate(steps,inputs):
                return False

        if (steps.current_step_index == stepIndex):
            self.updateInputs(inputs)
        self.messages.clear()
        

        try:
            self.insert_dataframes(steps, self.inputs)
            if self.calc_method:
                calc_output = self.calc_method(**self.calculation_input)
                self.handle_calc_outputs(calc_output)
                self.validate_outputs()

            self.calculation_status = "complete"
            if (steps.failed_step_index == stepIndex):
                steps.failed_step_index = -1
            
            if self.plot_method:
                plot_output = self.plot_method(**self.plot_input)
                self.handle_plot_outputs(plot_output)

        except NotImplementedError as e:
            self.messages.append(
                dict(
                    level=logging.ERROR,
                    msg=f"Method not implemented: {e}. Please contact the developer.",
                    trace=format_trace(traceback.format_exception(e)),
                )
            )
        except ValueError as e:
            self.messages.append(
                dict(
                    level=logging.ERROR,
                    msg=f"An error occured while validating inputs or outputs: {e}. Please check your parameters.",
                    trace=format_trace(traceback.format_exception(e)),
                )
            )
        except TypeError as e:
            self.messages.append(
                dict(
                    level=logging.ERROR,
                    msg=f"Please check the implementation of this steps method class (especially the input_keys): {e}.",
                    trace=format_trace(traceback.format_exception(e)),
                )
            )
        except Exception as e:
            self.messages.append(
                dict(
                    level=logging.ERROR,
                    msg=(
                        f"An error occurred while calculating this step: {e.__class__.__name__} {e} "
                        f"Please check your parameters or report a potential programming issue."
                    ),
                    trace=format_trace(traceback.format_exception(e)),
                )
            )
        
        if self.calculation_status != "complete":
            self.calculation_status = "failed"
            steps.failed_step_index = stepIndex

        return self.calculation_status == "complete"

    def insert_dataframes(self, steps: StepManager, inputs: dict) -> dict:
        return inputs

    def handle_calc_outputs(self, outputs: dict) -> None:
        """
        Handles the dictionary from the calculation method and creates an Output object from it.
        Responsible for checking that the output is a dictonary and not empty, and setting the output attribute of the instance.

        :param outputs: A dictionary received after the calculation
        :return: None
        """
        if not isinstance(outputs, dict):
            raise TypeError("Output of calculation is not a dictionary.")
        outputs = {key: value for key, value in outputs.items() if value is not None}
        if not outputs:
            raise ValueError("Output of calculation is empty.")
        self.output = Output(outputs)

        self.handle_messages(outputs)

    def handle_plot_outputs(self, outputs: dict|list) -> None:
        """
        Handles the dictionary from the plot method and creates a Plots object from it.
        Responsible for clearing and setting the plots attribute of the class.
        :param outputs: A dictionary or a list received after the plot method
        :return: None
        """

        if not isinstance(outputs, dict) and not isinstance(outputs, list):
            raise TypeError("Output of plot method is not a dictionary or a list.")
        
        if isinstance(outputs, dict):
            plots = outputs.pop("plots", [])
            self.output.output.update(outputs)
            self.handle_messages(outputs)
        else:
            plots = outputs
        
        self.plots = Plots(plots)

    def handle_messages(self, outputs: dict) -> None:
        """
        Handles the messages from the calculation method and creates a Messages object from it.
        Responsible for clearing and setting the messages attribute of the class.
        :param outputs: A dictionary received after the calculation
        :return: None
        """
        messages = outputs.get("messages", [])
        self.messages.extend(messages)

    calc_method = None
    plot_method = None # if the plot method uses the output of the calculation method, it should be prefixed with "output_"

    @property
    def calculation_input(self) -> dict:
        input_parameters = inspect.signature(self.calc_method).parameters
        required_keys = [
            key
            for key, param in input_parameters.items()
            if param.default == inspect.Parameter.empty
        ]
        for key in required_keys:
            if key not in self.inputs:
                raise ValueError(
                    f"Missing required input '{key}' for the calulation method"
                )

        return {
            key: self.inputs[key]
            for key in input_parameters.keys()
            if key in self.inputs
        }

    @property
    def plot_input(self) -> dict:
        # if the plot method uses the output of the calculation method, it should be prefixed with "output_"
        prefixed_output = {
            "output_" + key: value for key, value in self.output.output.items()
        }
        plot_input = self.inputs | prefixed_output

        input_parameters = inspect.signature(self.plot_method).parameters
        required_keys = [
            key
            for key, param in input_parameters.items()
            if param.default == inspect.Parameter.empty
        ]
        for key in required_keys:
            if key not in plot_input:
                raise ValueError(f"Missing required input '{key}' for the plot method")

        return {
            key: plot_input[key] for key in input_parameters.keys() if key in plot_input
        }

    def validate_outputs(self, soft_check: bool = False) -> bool:
        """
        Validates the outputs of the step. Uses the output_keys attribute to check if all required keys are present in the output dictionary.
        :param soft_check: Whether to raise errors or just return False if the output is invalid
        :return: True if the outputs are valid, False otherwise
        :raises ValueError: If a required key is missing in the outputs
        """
        
        print("Val0.0")
        for key in self.output_keys:
            print("Val0.5")
            if key not in self.output or self.output[key] is None:
                print("Val0.7")
                if not soft_check:
                    
                    print("val1.0")
                    raise ValueError(
                        f"Output validation failed: missing output {key} in outputs."
                    )
                else:
                    return False
        return True


class Output:

    def __init__(self, output: dict = {}):
        if output is None:
            output = {}

        self.output = output

    def __iter__(self):
        return iter(self.output.items())

    def __getitem__(self, key):
        return self.output[key]

    def __repr__(self):
        return f"Output: {self.output}"

    def __contains__(self, key):
        return key in self.output

    @property
    def is_empty(self) -> bool:
        return len(self.output) == 0 or all(
            value is None for value in self.output.values()
        )


class Messages:
    def __init__(self, messages: list[dict] = None):
        if messages is None:
            messages = []
        self.messages = messages

    def __iter__(self):
        return iter(self.messages)

    def __getitem__(self, key):
        return self.messages[key]

    def __repr__(self):
        return f"Messages: {[message['msg'] for message in self.messages]}"

    def append(self, param):
        self.messages.append(param)

    def extend(self, messages):
        self.messages.extend(messages)

    def clear(self):
        self.messages = []


class Plots:
    def __init__(self, plots: list | None = None):
        if plots is None:
            plots: list = []
        self.plots = plots

    def __iter__(self):
        return iter(self.plots)

    def __repr__(self):
        return f"Plots: {len(self.plots)}"

    @property
    def empty(self) -> bool:
        return len(self.plots) == 0

    def export(self, settings: dict) -> list:
        """
        Converts all plots from this step to files according to the format and size in the Plotly template.
        An exported plot is represented as BytesIO object containing binary image data.
        :param settings: Dict containing the plot settings.
        :return: List of all exported plots.
        """
        from ui.settings.plot_template import get_scale_factor
        exports = []
        format_ = settings["file_format"]
        
        for plot in self.plots:
            scale_factor = get_scale_factor(plot, settings)
            # For Plotly GO Figure
            if isinstance(plot, go.Figure):
                if format_ in ["tiff", "eps"]:
                    binary_png = pio.to_image(plot, format="png", scale=scale_factor)
                    img = Image.open(BytesIO(binary_png)).convert("RGB")
                    binary = BytesIO()
                    if format_ == "tiff":
                        img.save(binary, format="tiff", compression="tiff_lzw")
                    elif format_ == "eps":
                        img.save(binary, format=format_)
                    binary.seek(0)
                    exports.append(binary)
                else:
                    binary_png = pio.to_image(plot, format=format_, scale=scale_factor)
                    exports.append(BytesIO(binary_png))
            elif isinstance(plot, dict) and "plot_base64" in plot:
                plot = plot["plot_base64"]

            # TO DO: Include scale_factor here
            # For base64 encoded plot
            if isinstance(plot, bytes):
                if format_ in ["tiff", "eps"]:
                    img = Image.open(BytesIO(base64.b64decode(plot))).convert("RGB")
                    binary = BytesIO()
                    if format_ == "tiff":
                        img.save(binary, format="tiff", compression="tiff_lzw")
                    elif format_ == "eps":
                        img.save(binary, format="eps")
                    binary.seek(0)
                    exports.append(binary)
                elif format_ in ["png", "jpg"]:
                    exports.append(BytesIO(base64.b64decode(plot)))
        return exports


class StepManager:
    def __repr__(self):
        return f"IMP: {self.importing} PRE: {self.data_preprocessing} ANA: {self.data_analysis} INT: {self.data_integration}"

    def __init__(
        self,
        steps: list[Step] = None,
        df_mode: str = "disk",
        disk_operator: DiskOperator = None,
    ):
        self.df_mode = df_mode
        self.disk_operator = disk_operator
        self.current_step_index = 0
        self.failed_step_index = -1
        self.importing = []
        self.data_preprocessing = []
        self.data_analysis = []
        self.data_integration = []
        self.sections = {
            "importing": self.importing,
            "data_preprocessing": self.data_preprocessing,
            "data_analysis": self.data_analysis,
            "data_integration": self.data_integration,
        }

        if steps is not None:
            for step in steps:
                self.add_step(step)

    @property
    def all_steps(self) -> list[Step]:
        """
        This is read-only, meaning the changes made to this list will not persist.
        :return: a list of all the steps in the current StepManager
        """
        return (
            self.importing
            + self.data_preprocessing
            + self.data_analysis
            + self.data_integration
        )

    def get_instance_identifiers(
        self, step_type: type[Step], output_key: str | list[str] = None
    ) -> list[str]:
        if isinstance(output_key, str):
            output_key = [output_key]

        instance_identifiers = [
            step.instance_identifier
            for step in self.all_steps
            if isinstance(step, step_type)
            and (output_key is None or all(k in step.output for k in output_key))
        ]
        if not instance_identifiers:
            logging.warning(
                f"No instance identifiers found with step type {step_type} and output_key{'s' if len(output_key) > 1 else ''} {output_key}"
            )
        return instance_identifiers

    def get_step_output(
        self,
        step_type: type[Step],
        output_key: str,
        instance_identifier: str | None = None,
        include_current_step: bool = False,
    ) -> pd.DataFrame | Any | None:
        """
        Get the specific output of the outputs of a specific step type. The step type can also a parent class of the
        step type, in which case the output of the most recent step of the specific type is returned.

        :param step_type: The type of the step as a class object
        :param output_key: The key of the desired output in the output dictionary of the step
        :param instance_identifier: The instance identifier of the step to get the output from
        :param include_current_step: Whether to include the current step in the search
        :return: The value of the output of the step or None
        """

        def check_instance_identifier(step):
            return (
                step.instance_identifier == instance_identifier
                if instance_identifier is not None
                else True
            )

        if include_current_step:
            steps_to_search = self.all_steps
        else:
            steps_to_search = self.previous_steps

        for step in reversed(steps_to_search):
            if (
                isinstance(step, step_type)
                and check_instance_identifier(step)
                and output_key in step.output
            ):
                val = step.output[output_key]
                if val is None:
                    continue
                if isinstance(val, str) and Path(val).exists():
                    if Path(val).suffix == ".csv":
                        from protzilla.disk_operator import DataFrameOperator

                        df_operator = DataFrameOperator()
                        df = df_operator.read(val)
                        if df.empty:
                            logging.warning(
                                f"Could not read DataFrame from {val}, continuing"
                            )
                            continue
                        return df
                    else:
                        raise ValueError(f"Unsupported file format {Path(str).suffix}")
                return val
        return None

    def get_step_input(
        self,
        step_type: type[Step] | list[type[Step]],
        input_key: str,
        instance_identifier: str | None = None,
    ):
        """
        Get the specific input of the inputs of a specific step type. The step type can also a parent class of the
        step type, in which case the input of the most recent step of the specific type is returned.
        :param step_type: The type of the step as a class object
        :param input_key: The key of the desired input in the input dictionary of the step
        :return: The value of the input of the step or None
        """

        def check_instance_identifier(step):
            return (
                step.instance_identifier == instance_identifier
                if instance_identifier is not None
                else True
            )

        step_type = [step_type] if not isinstance(step_type, list) else step_type
        for step in reversed(self.previous_steps):
            if (
                any(isinstance(step, st) for st in step_type)
                and check_instance_identifier(step)
                and input_key in step.inputs
            ):
                return step.inputs[input_key]
        return None

    def all_steps_in_section(self, section: str) -> list[Step]:
        """
        Get all steps in a specific section via the section name
        :param section: The section name
        :return: A list of steps in the section
        """
        if section in self.sections:
            return self.sections[section]
        else:
            raise ValueError(f"Unknown section {section}")
    
    def set_steps_outdated(self, offset: int) -> None:
        count = 0
        for step in self.following_steps[offset:]:
            if (step.calculation_status == "complete"):
                step.calculation_status = "outdated"
                count+=1
        return count

    @property
    def previous_steps(self) -> list[Step]:
        return self.all_steps[: self.current_step_index]
    
    @property
    def following_steps(self) -> list[Step]:
        return self.all_steps[self.current_step_index :]

    @property
    def current_step(self) -> Step:
        if self.current_step_index >= len(self.all_steps):
            return None
        return self.all_steps[self.current_step_index]

    @property
    def current_operation(self) -> str:
        return self.current_step.operation

    @property
    def current_section(self) -> str:
        return self.current_step.section

    @property
    def current_location(self) -> tuple[str, str, str]:
        return (
            self.current_section,
            self.current_operation,
            self.current_step.instance_identifier,
        )

    @property
    def protein_df(self) -> pd.DataFrame:
        from protzilla.steps import Step

        return self.get_step_output(Step, "protein_df")

    @property
    def metadata_df(self) -> pd.DataFrame | None:
        from protzilla.methods.importing import ImportingStep

        return self.get_step_output(ImportingStep, "metadata_df")

    @property
    def preprocessed_output(self) -> Output:
        if self.current_section == "importing":
            return None
        if self.current_section == "data_preprocessing":
            return (
                self.current_step.output
                if self.current_step.calculation_status!="incomplete"
                else self.previous_steps[-1].output
            )
        return self.data_preprocessing[-1].output

    @property
    def is_at_last_step(self) -> bool:
        return self.current_step_index == len(self.all_steps) - 1

    def add_step(self, step) -> None:
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

    def remove_step(
        self, step: Step, step_index: int = None, section: str = None
    ) -> None:
        """
        Removes a step. Either the step must be passed or both section and step_index in the specific section.
        :param step: the step instance object
        :param step_index: the step index in the section
        :param section: the section as a string
        """
        if step is None and (step_index is None or section is None):
            raise ValueError("Either step or step_index and section must be provided")
        if step is None:
            if section not in self.sections:
                raise ValueError(f"Unknown section {section}")
            if step_index >= len(self.sections[section]):
                raise ValueError(
                    f"Step index {step_index} out of bounds for section {section}"
                )

            step = self.all_steps_in_section(section)[step_index]

        global_step_index = self.all_steps.index(step)
        self._clear_future_steps(global_step_index)
        if global_step_index < self.current_step_index:
            self.current_step_index -= 1
        self.sections[step.section].remove(step)

    def next_step(self) -> None:
        """
        Go to the next step in the workflow. Depending on the df_mode, the dataframes of the previous output are
        replaced with the respective paths on the disk where they are saved to save memory.

        :return: None
        """
        if not self.is_at_last_step:
            self.disk_operator.clear_upload_dir()  # TODO this could be a problem when using protzilla for multiple users
            if self.df_mode == "disk":
                # TODO maybe this doesnt really need to be written to disk anymore,
                # as it is preceeded by a calculation, after which everything is written to
                # disk anyway. Better would be if it would just replace the dfs with their respective paths
                self.current_step.output = Output(
                    self.disk_operator._write_output(
                        instance_identifier=self.current_step.instance_identifier,
                        output=self.current_step.output,
                    )
                )
            self.current_step_index += 1
        else:
            raise ValueError("Cannot go to the next step from the last step")

    def previous_step(self) -> None:
        """
        Go to the previous step in the workflow. If the previous step is in disk mode, the respective dataframes are
        loaded from disk and replaced in the output dictionary of the step.

        :return: None
        """
        if self.current_step_index > 0:
            self.current_step_index -= 1
        else:
            raise ValueError("Cannot go back from the first step")

    @property
    def future_steps(self) -> list[Step]:
        """
        Get all steps that are after the current step in the workflow.
        :return: A list of steps that are after the current step
        """
        if self.is_at_last_step:
            return []
        return self.all_steps[self.current_step_index + 1 :]

    def goto_step(self, step_index: int, section: str) -> None:
        """
        Go to a specific step in the workflow.
        :param step_index: The index of the step in the respective section
        :param section: The section of the step to go to
        :return:
        """
        if section not in self.sections:
            raise ValueError(f"Unknown section {section}")
        if step_index < 0 or step_index >= len(self.sections[section]):
            raise ValueError(
                f"Step index {step_index} out of bounds for section {section}"
            )

        step = self.all_steps_in_section(section)[step_index]
        new_step_index = self.all_steps.index(step)
        self.current_step_index = new_step_index

    def name_current_step_instance(self, new_instance_identifier: str) -> None:
        """
        Change the instance identifier of the current step
        :return: None
        :param new_instance_identifier: the new instance identifier
        """
        self.current_step.instance_identifier = new_instance_identifier

    def change_method(self, new_method: str) -> None:
        """
        Change the method of the current step,
        :param new_method: the new method, the name of the method class (accessible via __class__.__name__)
        :return: None
        :raises ValueError: if the section of the current step is unknown
        """
        from protzilla.stepfactory import StepFactory

        new_step = StepFactory.create_step(new_method, self)

        try:
            current_index = self.all_steps_in_section(self.current_section).index(
                self.current_step
            )
            self.all_steps_in_section(self.current_section)[current_index] = new_step
            self._clear_future_steps()
        except ValueError:
            raise ValueError(f"Unknown section {self.current_section}")
        except Exception as e:
            logging.error(f"Error while changing method: {e}")

    def _clear_future_steps(self, index: int | None = None) -> None:
        if index == None:
            index = self.current_step_index
        if index == len(self.all_steps) - 1:
            return
        for step in self.all_steps[index + 1 :]:
            step.output = Output()
            step.messages = Messages()
            step.plots = Plots()
