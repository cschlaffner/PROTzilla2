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
    name = "MaxQuant"
    step = "msdataimport"
    method_description = "Import MaxQuant data"

    parameter_names = ["file_path", "map_to_uniprot", "intensity_name"]
    output_names = ["protein_df"]

    def method(self, inputs):
        return max_quant_import(**inputs)


class DiannImport(ImportingStep):
    name = "DIA-NN"
    step = "msdataimport"
    method = "diann_import"
    method_description = "DIA-NN data import"

    parameter_names = ["file_path", "map_to_uniprot"]
    output_names = ["protein_df"]

    def method(self, inputs):
        return diann_import(**inputs)


class MsFraggerImport(ImportingStep):
    name = "MS Fragger"
    step = "msdataimport"
    method = "ms_fragger_import"
    method_description = "MS Fragger data import"

    parameter_names = ["file_path", "intensity_name", "map_to_uniprot"]
    output_names = ["protein_df"]

    def method(self, inputs):
        return ms_fragger_import(**inputs)


class MetadataImport(ImportingStep):
    name = "Metadata import"
    step = "metadataimport"
    method_description = "Import metadata"

    parameter_names = ["file_path", "feature_orientation"]
    output_names = ["metadata_df"]

    def method(self, inputs):
        return metadata_import_method(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = steps.get_step_output(ImportingStep, "protein_df")
        return inputs


class MetadataImportMethodDiann(ImportingStep):
    name = "Metadata import DIA-NN"
    step = "metadataimport"
    method = "metadata_import_method_diann"
    method_description = "Import metadata for run relationships of DIA-NN"

    parameter_names = ["file_path", "groupby_sample"]
    output_names = ["metadata_df"]

    def method(self, inputs):
        return metadata_import_method_diann(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = None
        return inputs


class MetadataColumnAssignment(ImportingStep):
    name = "Metadata column assignment"
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
    output_names = ["metadata_df"]

    def method(self, inputs):
        return metadata_column_assignment(**inputs)


class PeptideImport(ImportingStep):
    name = "Peptide import"
    step = "peptide_import"
    method = "peptide_import"
    method_description = "Import peptide data"

    parameter_names = ["file_path", "intensity_name"]
    output_names = ["peptide_df"]

    def method(self, inputs):
        return peptide_import(**inputs)
