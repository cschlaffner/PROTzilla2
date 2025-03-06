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

    def calc_method(self):
        raise NotImplementedError("This method must be implemented in a subclass.")

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs


class MaxQuantImport(ImportingStep):
    display_name = "MaxQuant Protein Groups Import"
    operation = "Protein Data Import"
    method_description = "Import the protein groups file form output of MaxQuant"

    output_keys = ["protein_df"]

    calc_method = staticmethod(max_quant_import)


class DiannImport(ImportingStep):
    display_name = "DIA-NN Import"
    operation = "Protein Data Import"
    method_description = "DIA-NN data import"

    output_keys = ["protein_df"]

    calc_method = staticmethod(diann_import)


class MsFraggerImport(ImportingStep):
    display_name = "MS Fragger Combined Protein Import"
    operation = "Protein Data Import"
    method_description = "Import the combined_protein.tsv file form output of MS Fragger"

    output_keys = ["protein_df"]

    calc_method = staticmethod(ms_fragger_import)


class MetadataImport(ImportingStep):
    display_name = "Metadata Import"
    operation = "metadataimport"
    method_description = "Import metadata"

    output_keys = ["metadata_df"]

    calc_method = staticmethod(metadata_import_method)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = steps.get_step_output(ImportingStep, "protein_df")
        return inputs


class MetadataImportMethodDiann(ImportingStep):
    display_name = "DIA-NN Metadata Import"
    operation = "metadataimport"
    method_description = "Import metadata for run relationships of DIA-NN"

    output_keys = ["metadata_df", "protein_df"]

    calc_method = staticmethod(metadata_import_method_diann)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = steps.get_step_output(DiannImport, "protein_df")
        return inputs


class MetadataColumnAssignment(ImportingStep):
    display_name = "Metadata column assignment"
    operation = "metadataimport"
    method_description = (
        "Assign columns to metadata categories, repeatable for each category"
    )

    output_keys = ["metadata_df", "protein_df"]

    calc_method = staticmethod(metadata_column_assignment)

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

    output_keys = ["peptide_df"]

    calc_method = staticmethod(peptide_import)


class EvidenceImport(ImportingStep):
    display_name = "MaxQuant Evidence Import"
    operation = "peptide_import"
    method_description = "Import an evidence file"

    output_keys = ["peptide_df"]

    calc_method = staticmethod(evidence_import)