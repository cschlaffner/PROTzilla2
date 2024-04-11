from __future__ import annotations

import logging

import pandas as pd

from protzilla.data_preprocessing.imputation import by_min_per_protein
from protzilla.importing.metadata_import import metadata_import_method
from protzilla.importing.ms_data_import import max_quant_import


class Step:
    def __init__(self):
        self.inputs: dict = {}
        self.messages: Messages = Messages([])
        self.output: Output = Output()
        self.plots = []
        self.parameter_names = []
        self.output_names = []

    def __repr__(self):
        return self.__class__.__name__

    def calculate(self, steps: StepManager, inputs: dict = None):
        if inputs is not None:
            self.inputs = inputs

        # validate the inputs for the step
        self.validate_inputs(self.parameter_names)

        # calculate the step
        output_dict = self.method(self.get_input_dataframe(steps), **self.inputs)
        messages = output_dict.pop("messages")
        self.messages = Messages(messages)

        # store the output and messages
        self.handle_outputs(output_dict)

        # validate the output
        self.validate_outputs(self.output_names)

    def method(self, dataframe: pd.DataFrame, **kwargs):
        raise NotImplementedError("This method must be implemented in a subclass.")

    def get_input_dataframe(self, steps: StepManager) -> pd.DataFrame | None:
        return None

    def handle_outputs(self, output_dict: dict):
        self.output = Output(output_dict)

    def validate_inputs(self, required_keys: list[str]):
        for key in required_keys:
            if key not in self.inputs:
                raise ValueError(f"Missing input {key} in inputs")

    def validate_outputs(self, required_keys: list[str]):
        for key in required_keys:
            if key not in self.output.output:
                raise ValueError(f"Missing output {key} in output")


class ImportingStep(Step):
    section = "importing"

    def method(self, dataframe: pd.DataFrame, **kwargs):
        raise NotImplementedError("This method must be implemented in a subclass.")

    def get_input_dataframe(self, steps: StepManager) -> pd.DataFrame | None:
        return None


class DataPreprocessingStep(Step):
    section = "data_preprocessing"

    def get_input_dataframe(self, steps: StepManager):
        return steps.protein_df


class DataAnalysisStep(Step):
    section = "data_analysis"

    def get_input_dataframe(self, steps: StepManager):
        protein_df
        return NotImplementedError("This method must be implemented in a subclass.")


class Output:
    def __iter__(self):
        return iter(self.output.items())

    def __init__(self, output: dict = None):
        if output is None:
            output = {}

        self.output = output

    def __getitem__(self, key):
        return self.output[key]

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
    def __iter__(self):
        return iter(self.messages)

    def __init__(self, messages: list[dict] = None):
        if messages is None:
            messages = []
        self.messages = messages


class MaxQuantImport(ImportingStep):
    name = "MaxQuant"
    section = "importing"
    step = "msdataimport"
    method_id = "max_quant_import"
    method_description = "Import MaxQuant data"

    parameter_names = ["file_path", "map_to_uniprot", "intensity_name"]
    output_names = ["intensity_df"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return max_quant_import(dataframe, **kwargs)

    def get_input_dataframe(self, steps: StepManager):
        return None


class DiannImport(ImportingStep):
    name = "DIA-NN"
    section = "importing"
    step = "msdataimport"
    method = "diann_import"
    method_description = "DIA-NN data import"

    parameter_names = ["file_path", "map_to_uniprot"]
    output_names = ["protein_df"]

    def method(self, dataframe: pd.Dataframe, **kwargs):
        return diann_import(dataframe, **kwargs)

    def get_input_dataframe(self, steps: StepManager):
        return None

    def handle_outputs(self, dataframe: pd.DataFrame, outputs: dict):
        self.output = Output({"protein_df": dataframe} | output_dict)


class MsFraggerImport(ImportingStep):
    name = "MS Fragger"
    section = "importing"
    step = "msdataimport"
    method = "ms_fragger_import"
    method_description = "MS Fragger data import"

    parameter_names = ["file_path", "intensity_name", "map_to_uniprot"]
    output_names = ["protein_df"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return ms_fragger_import(dataframe, **kwargs)

    def get_input_dataframe(self, steps: StepManager):
        return None

    def handle_outputs(self, dataframe: pd.DataFrame, output_dict: dict):
        self.output = Output({"protein_df": dataframe} | output_dict)


class MetadataImport(ImportingStep):
    name = "Metadata import"
    section = "importing"
    step = "metadataimport"
    method_id = "metadata_import_method"
    method_description = "Import metadata"

    parameter_names = ["file_path", "feature_orientation"]
    output_names = ["metadata_df"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return metadata_import_method(dataframe, **kwargs)

    def get_input_dataframe(self, steps: StepManager):
        return steps.intensity_df

    def handle_outputs(self, dataframe: pd.DataFrame, output_dict: dict):
        self.output = Output({"metadata_df": output_dict["metadata"]})


class MetadataImportMethodDiann(ImportingStep):
    name = "Metadata import DIA-NN"
    section = "importing"
    step = "metadataimport"
    method = "metadata_import_method_diann"
    method_description = "Import metadata for run relationships of DIA-NN"

    parameter_names = ["file_path", "groupby_sample"]
    output_names = ["metadata_df"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return metadata_import_method(dataframe, **kwargs)

    def get_input_dataframe(self, steps: StepManager):
        return steps.intensity_df

    def handle_outputs(self, dataframe: pd.DataFrame, output_dict: dict):
        self.output = Output({"metadata_df": output_dict["metadata"]})


class MetadataColumnAssignment(ImportingStep):
    name = "Metadata column assignment"
    section = "importing"
    step = "metadataimport"
    method = "metadata_column_assignment"
    method_description = (
        "Assign columns to metadata categories, repeatable for each category"
    )

    parameter_names = [
        "metadata_df",
        "metadata_required_column",
        "metadata_unknown_column",
    ]
    output_names = [" "]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return meta(dataframe, **kwargs)

    def get_input_dataframe(self, steps: StepManager):
        return steps.intensity_df

    def handle_outputs(self, dataframe: pd.DataFrame, output_dict: dict):
        self.output = Output({"metadata_df": output_dict["metadata"]})


class PeptideImport(Steps):
    name = "Peptide import"
    section = "importing"
    step = "peptide_import"
    method = "peptide_import"
    method_description = "Import peptide data"

    parameter_names = ["file_path", "intensity_name"]
    output_names = ["peptide_df"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return metadata_import_method(dataframe, **kwargs)

    def get_input_dataframe(self, steps: StepManager):
        return steps.intensity_df

    def handle_outputs(self, dataframe: pd.DataFrame, output_dict: dict):
        self.output = Output({"peptide_df": output_dict["peptide"]})


class MetadataImport(Step):
    name = "Metadata import"
    section = "importing"
    step = "metadataimport"
    method = "metadata_import_method"
    method_description = "Import metadata"

    parameter_names = ["file_path", "feature_orientation"]
    output_names = ["metadata_df"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return metadata_import_method(dataframe, **kwargs)

    def get_input_dataframe(self, steps: StepManager):
        return steps.protein_df


class ImputationMinPerProtein(Step):
    name = "Min per dataset"
    section = "data_preprocessing"
    step = "imputation"
    method_id = "by_min_per_protein"
    method_description = "Impute missing values by the minimum per protein"

    parameter_names = ["shrinking_value"]
    output_names = ["intensity_df"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return by_min_per_protein(dataframe, **kwargs)

    def get_input_dataframe(self, steps: StepManager):
        return steps.protein_df


class StepFactory:
    # TODO this could be done with the new mapping class, iterating and checking whether there exists a step with that specific name
    @staticmethod
    def create_step(step_type: str) -> Step:
        if step_type == "MaxQuantImport" or step_type == "max_quant_import":
            return MaxQuantImport()
        elif (
            step_type == "ImputationMinPerProtein" or step_type == "by_min_per_protein"
        ):
            return ImputationMinPerProtein()
        elif step_type == "MetadataImport" or step_type == "metadata_import_method":
            return MetadataImport()
        else:
            raise ValueError(f"Unknown step type {step_type}")


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

    def all_steps_in_section(self, section: str):
        if section == "importing":
            return self.importing
        elif section == "data_preprocessing":
            return self.data_preprocessing
        elif section == "data_analysis":
            return self.data_analysis
        elif section == "data_integration":
            return self.data_integration
        else:
            raise ValueError(f"Unknown section {section}")

    @property
    def previous_steps(self):
        return self.all_steps[: self.current_step_index]

    @property
    def current_step(self) -> Step:
        return self.all_steps[self.current_step_index]

    def current_section(self) -> str:
        return self.current_step.section

    @property
    def protein_df(self):
        # find the last step that has an intensity_df
        for step in reversed(self.all_steps):
            if step.output.protein_df is not None:
                return step.output.protein_df
        logging.warning("No intensity_df found in steps")

    @property
    def metadata_df(self):
        # find the last step that has a metadata_df
        for step in reversed(self.all_steps):
            if hasattr(step.output, "metadata_df"):
                return step.output.metadata_df
        logging.warning("No metadata_df found in steps")

    @property
    def is_at_last_step(self):
        return self.current_step_index == len(self.all_steps) - 1

    def add_step(self, step, index: int | None = None):
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
            step = self.all_steps[step_index]

        for section in [
            self.importing,
            self.data_preprocessing,
            self.data_analysis,
            self.data_integration,
        ]:
            try:
                section.remove(step)
                return
            except ValueError:
                pass

        raise ValueError(f"Step {step} not found in steps")
