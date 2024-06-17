from __future__ import annotations

import base64
import inspect
import logging
import traceback
from enum import Enum
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly
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
    input_keys: list[str] = []
    output_keys: list[str] = []

    def __init__(self, instance_identifier: str | None = None):
        self.form_inputs: dict = {}
        self.inputs: dict = {}
        self.messages: Messages = Messages([])
        self.output: Output = Output()
        self.plots: Plots = Plots()
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

    def calculate(self, steps: StepManager, inputs: dict) -> None:
        """
        Core calculation method for all steps, receives the inputs from the front-end and calculates the output.

        :param steps: The StepManager object that contains all steps
        :param inputs: These inputs will be supplied to the method. Only keys in the input_keys of the method class will actually be supplied to the method
        :return: None
        """
        steps._clear_future_steps()

        if inputs:
            self.inputs = inputs.copy()
        self.form_inputs = self.inputs.copy()

        try:
            self.messages.clear()
            self.insert_dataframes(steps, self.inputs)
            self.validate_inputs()

            output_dict = self.method(self.inputs)
            self.handle_outputs(output_dict)
            self.handle_messages(output_dict)

            self.validate_outputs()
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

    def method(self, **kwargs) -> dict:
        raise NotImplementedError("This method must be implemented in a subclass.")

    def insert_dataframes(self, steps: StepManager, inputs: dict) -> dict:
        return inputs

    def handle_outputs(self, outputs: dict) -> None:
        """
        Handles the dictionary from the calculation method and creates an Output object from it.
        Responsible for checking if the output is a dictionary and if it is empty, and setting the output attribute of the instance.

        :param outputs: A dictionary received after the calculation
        :return: None
        """
        if not isinstance(outputs, dict):
            raise TypeError("Output of calculation is not a dictionary.")
        outputs = {key: value for key, value in outputs.items() if value is not None}
        if not outputs:
            raise ValueError("Output of calculation is empty.")
        self.output = Output(outputs)

    def handle_messages(self, outputs: dict) -> None:
        """
        Handles the messages from the calculation method and creates a Messages object from it.
        Responsible for clearing and setting the messages attribute of the class.
        :param outputs: A dictionary received after the calculation
        :return: None
        """
        messages = outputs.get("messages", [])
        self.messages.extend(messages)

    def plot(self, inputs: dict = None) -> None:
        raise NotImplementedError(
            f"Plotting is not implemented for this step ({self.display_name}). Only preprocessing methods can have additional plots."
        )

    def validate_inputs(self, required_keys: list[str] = None) -> bool:
        """
        Validates the inputs of the step. If required_keys is not specified, the input_keys of the method class are used.
        Will delete unnecessary keys from the inputs dictionary to avoid passing unwanted parameters to the method.
        :param required_keys: The keys that are required in the inputs dictionary (optional)
        :return: True if the inputs are valid, False otherwise
        :raises ValueError: If a required key is missing in the inputs
        """
        if required_keys is None:
            required_keys = self.input_keys
        for key in required_keys:
            if key not in self.inputs:
                raise ValueError(f"Missing input {key} in inputs")

        # Deleting all unnecessary keys as to avoid "too many parameters" error
        for key in self.inputs.copy().keys():
            if key not in required_keys:
                logging.info(
                    f"Removing unnecessary key {key} from inputs. If this is not wanted, add the key to input_keys of the method class."
                )
                self.inputs.pop(key)

        return True

    def validate_outputs(
        self, required_keys: list[str] = None, soft_check: bool = False
    ) -> bool:
        """
        Validates the outputs of the step. If required_keys is not specified, the output_keys of the method class are used.

        :param required_keys: The keys that are required in the outputs dictionary (optional)
        :param soft_check: Whether to raise errors or just return False if the output is invalid
        :return: True if the outputs are valid, False otherwise
        :raises ValueError: If a required key is missing in the outputs
        """
        inspect.signature(self.method).parameters
        if required_keys is None:
            required_keys = self.output_keys
        for key in required_keys:
            if key not in self.output:
                if not soft_check:
                    raise ValueError(
                        f"Output validation failed: missing output {key} in outputs."
                    )
                else:
                    return False
        return True

    @property
    def finished(self) -> bool:
        """
        Return whether the step has valid outputs and is therefore considered finished.
        Plot steps without required outputs are considered finished if they have plots.
        :return: True if the step is finished, False otherwise
        """
        if len(self.output_keys) == 0:
            return not self.plots.empty
        return self.validate_outputs(soft_check=True)


class Output:
    def __init__(self, output: dict = None):
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
        return f"Messages: {[message['message'] for message in self.messages]}"

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

    def export(self, format_):
        exports = []
        for plot in self.plots:
            if isinstance(plot, plotly.graph_objs.Figure):
                if format_ in ["eps", "tiff"]:
                    png_binary = plotly.io.to_image(plot, format="png", scale=4)
                    img = Image.open(BytesIO(png_binary)).convert("RGB")
                    binary = BytesIO()
                    if format_ == "tiff":
                        img.save(binary, format="tiff", compression="tiff_lzw")
                    else:
                        img.save(binary, format=format_)
                    exports.append(binary)
                else:
                    binary_string = plotly.io.to_image(plot, format=format_, scale=4)
                    exports.append(BytesIO(binary_string))
            elif isinstance(plot, dict) and "plot_base64" in plot:
                plot = plot["plot_base64"]

            if isinstance(plot, bytes):  # base64 encoded plots
                if format_ in ["eps", "tiff"]:
                    img = Image.open(BytesIO(base64.b64decode(plot))).convert("RGB")
                    binary = BytesIO()
                    if format_ == "tiff":
                        img.save(binary, format="tiff", compression="tiff_lzw")
                    else:
                        img.save(binary, format=format_)
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
        self, step_type: type[Step], output_key: str = None
    ) -> list[str]:
        instance_identifiers = [
            step.instance_identifier
            for step in self.all_steps
            if isinstance(step, step_type)
            and (output_key is None or output_key in step.output)
        ]
        if not instance_identifiers:
            logging.warning(
                f"No instance identifiers found for {step_type} and output_key {output_key}"
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

    @property
    def previous_steps(self) -> list[Step]:
        return self.all_steps[: self.current_step_index]

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

        df = self.get_step_output(Step, "protein_df")
        return df

    @property
    def metadata_df(self) -> pd.DataFrame | None:
        from protzilla.methods.importing import ImportingStep

        return self.get_step_output(ImportingStep, "metadata_df")
        logging.warning("No metadata_df found in steps")

    @property
    def preprocessed_output(self) -> Output:
        if self.current_section == "importing":
            return None
        if self.current_section == "data_preprocessing":
            return (
                self.current_step.output
                if self.current_step.finished
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
        if new_step_index < self.current_step_index:
            self.current_step_index = new_step_index
        else:
            raise ValueError("Cannot go to a step that is after the current step")

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
