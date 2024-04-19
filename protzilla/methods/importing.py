from __future__ import annotations

from protzilla.importing.metadata_import import (
    metadata_column_assignment,
    metadata_import_method,
    metadata_import_method_diann,
)
from protzilla.importing.ms_data_import import (
    diann_import,
    max_quant_import,
    ms_fragger_import,
)
from protzilla.importing.peptide_import import peptide_import
from protzilla.steps import Step, StepManager


class ImportingStep(Step):
    section = "importing"

    def method(self, inputs):
        raise NotImplementedError("This method must be implemented in a subclass.")

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs


class MaxQuantImport(ImportingStep):
    display_name = "MaxQuant"
    operation = "msdataimport"
    method_description = "Import MaxQuant data"

    input_keys = ["file_path", "map_to_uniprot", "intensity_name"]
    output_keys = ["protein_df"]

    def method(self, inputs):
        return max_quant_import(**inputs)


class DiannImport(ImportingStep):
    display_name = "DIA-NN"
    operation = "msdataimport"
    method = "diann_import"
    method_description = "DIA-NN data import"

    input_keys = ["file_path", "map_to_uniprot"]
    output_keys = ["protein_df"]

    def method(self, inputs):
        return diann_import(**inputs)


class MsFraggerImport(ImportingStep):
    display_name = "MS Fragger"
    operation = "msdataimport"
    method = "ms_fragger_import"
    method_description = "MS Fragger data import"

    input_keys = ["file_path", "intensity_name", "map_to_uniprot"]
    output_keys = ["protein_df"]

    def method(self, inputs):
        return ms_fragger_import(**inputs)


class MetadataImport(ImportingStep):
    display_name = "Metadata import"
    operation = "metadataimport"
    method_description = "Import metadata"

    input_keys = ["file_path", "feature_orientation"]
    output_keys = ["metadata_df"]

    def method(self, inputs):
        return metadata_import_method(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = steps.get_step_output(ImportingStep, "protein_df")
        return inputs


class MetadataImportMethodDiann(ImportingStep):
    display_name = "Metadata import DIA-NN"
    operation = "metadataimport"
    method = "metadata_import_method_diann"
    method_description = "Import metadata for run relationships of DIA-NN"

    input_keys = ["file_path", "groupby_sample"]
    output_keys = ["metadata_df"]

    def method(self, inputs):
        return metadata_import_method_diann(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = None
        return inputs


class MetadataColumnAssignment(ImportingStep):
    display_name = "Metadata column assignment"
    operation = "metadataimport"
    method = "metadata_column_assignment"
    method_description = (
        "Assign columns to metadata categories, repeatable for each category"
    )

    input_keys = [
        "metadata_required_column",
        "metadata_unknown_column",
    ]
    output_keys = ["metadata_df"]

    def method(self, inputs):
        return metadata_column_assignment(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs: dict) -> dict:
        inputs["protein_df"] = steps.get_step_output(ImportingStep, "protein_df")
        inputs["metadata_df"] = steps.get_step_output(MetadataImport, "metadata_df")
        return inputs


class PeptideImport(ImportingStep):
    display_name = "Peptide import"
    operation = "peptide_import"
    method = "peptide_import"
    method_description = "Import peptide data"

    input_keys = ["file_path", "intensity_name"]
    output_keys = ["peptide_df"]

    def method(self, inputs):
        return peptide_import(**inputs)
