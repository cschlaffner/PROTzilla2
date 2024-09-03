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
from protzilla.importing.peptide_import import peptide_import, evidence_import
from protzilla.steps import Step, StepManager


class ImportingStep(Step):
    section = "importing"

    def method(self, inputs):
        raise NotImplementedError("This method must be implemented in a subclass.")

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs


class MaxQuantImport(ImportingStep):
    display_name = "MaxQuant Protein Groups Import"
    operation = "Protein Data Import"
    method_description = "Import the protein groups file form output of MaxQuant"

    input_keys = ["file_path", "map_to_uniprot", "intensity_name", "aggregation_method"]
    output_keys = ["protein_df"]

    def method(self, inputs):
        return max_quant_import(**inputs)


class DiannImport(ImportingStep):
    display_name = "DIA-NN Import"
    operation = "Protein Data Import"
    method_description = "DIA-NN data import"

    input_keys = ["file_path", "map_to_uniprot", "aggregation_method"]
    output_keys = ["protein_df"]

    def method(self, inputs):
        return diann_import(**inputs)


class MsFraggerImport(ImportingStep):
    display_name = "MS Fragger Combined Protein Import"
    operation = "Protein Data Import"
    method_description = "Import the combined_protein.tsv file form output of MS Fragger"

    input_keys = ["file_path", "intensity_name", "map_to_uniprot", "aggregation_method"]
    output_keys = ["protein_df"]

    def method(self, inputs):
        return ms_fragger_import(**inputs)


class MetadataImport(ImportingStep):
    display_name = "Metadata import"
    operation = "metadataimport"
    method_description = "Import metadata"

    input_keys = ["file_path", "feature_orientation", "protein_df"]
    output_keys = ["metadata_df"]

    def method(self, inputs):
        return metadata_import_method(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = steps.get_step_output(ImportingStep, "protein_df")
        return inputs


class MetadataImportMethodDiann(ImportingStep):
    display_name = "Metadata import DIA-NN"
    operation = "metadataimport"
    method_description = "Import metadata for run relationships of DIA-NN"

    input_keys = ["file_path", "groupby_sample", "protein_df"]
    output_keys = ["metadata_df", "protein_df"]

    def method(self, inputs):
        return metadata_import_method_diann(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = steps.get_step_output(DiannImport, "protein_df")
        return inputs


class MetadataColumnAssignment(ImportingStep):
    display_name = "Metadata column assignment"
    operation = "metadataimport"
    method_description = (
        "Assign columns to metadata categories, repeatable for each category"
    )

    input_keys = [
        "metadata_required_column",
        "metadata_unknown_column",
        "protein_df",
        "metadata_df",
    ]
    output_keys = ["metadata_df", "protein_df"]

    def method(self, inputs):
        return metadata_column_assignment(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs: dict) -> dict:
        inputs["protein_df"] = steps.get_step_output(ImportingStep, "protein_df")
        inputs["metadata_df"] = steps.get_step_output(
            ImportingStep, "metadata_df", include_current_step=True
        )
        return inputs


class PeptideImport(ImportingStep):
    display_name = "MaxQuant Peptide Import"
    operation = "peptide_import"
    method_description = "Import peptide data"

    input_keys = ["file_path", "intensity_name", "map_to_uniprot"]
    output_keys = ["peptide_df"]

    def method(self, inputs):
        return peptide_import(**inputs)


class EvidenceImport(ImportingStep):
    display_name = "MaxQuant Evidence Import"
    operation = "peptide_import"
    method_description = "Import an evidence file"

    input_keys = ["file_path", "intensity_name", "map_to_uniprot"]
    output_keys = ["peptide_df"]

    def method(self, inputs):
        return evidence_import(**inputs)