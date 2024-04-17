from __future__ import annotations

import pandas as pd

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

    def method(self, **kwargs):
        raise NotImplementedError("This method must be implemented in a subclass.")

    def get_input_dataframe(self, steps: StepManager, kwargs) -> pd.DataFrame | None:
        return kwargs


class MaxQuantImport(ImportingStep):
    name = "MaxQuant"
    step = "msdataimport"
    method_id = "max_quant_import"
    method_description = "Import MaxQuant data"

    parameter_names = ["file_path", "map_to_uniprot", "intensity_name"]
    output_names = ["protein_df"]

    def method(self, **kwargs):
        return max_quant_import(**kwargs)


class DiannImport(ImportingStep):
    name = "DIA-NN"
    step = "msdataimport"
    method = "diann_import"
    method_description = "DIA-NN data import"

    parameter_names = ["file_path", "map_to_uniprot"]
    output_names = ["protein_df"]

    def method(self, **kwargs):
        return diann_import(**kwargs)


class MsFraggerImport(ImportingStep):
    name = "MS Fragger"
    step = "msdataimport"
    method = "ms_fragger_import"
    method_description = "MS Fragger data import"

    parameter_names = ["file_path", "intensity_name", "map_to_uniprot"]
    output_names = ["protein_df"]

    def method(self, **kwargs):
        return ms_fragger_import(**kwargs)


class MetadataImport(ImportingStep):
    name = "Metadata import"
    step = "metadataimport"
    method_id = "metadata_import_method"
    method_description = "Import metadata"

    parameter_names = ["file_path", "feature_orientation"]
    output_names = ["metadata_df"]

    def method(self, **kwargs):
        return metadata_import_method(**kwargs)

    def get_input_dataframe(self, steps: StepManager, kwargs) -> pd.DataFrame | None:
        kwargs["protein_df"] = steps.get_step_output(ImportingStep, "protein_df")
        return kwargs


class MetadataImportMethodDiann(ImportingStep):
    name = "Metadata import DIA-NN"
    step = "metadataimport"
    method = "metadata_import_method_diann"
    method_description = "Import metadata for run relationships of DIA-NN"

    parameter_names = ["file_path", "groupby_sample"]
    output_names = ["metadata_df"]

    def method(self, **kwargs):
        return metadata_import_method_diann(**kwargs)

    def get_input_dataframe(self, steps: StepManager, kwargs) -> pd.DataFrame | None:
        kwargs["protein_df"] = None
        return kwargs


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

    def method(self, **kwargs):
        return metadata_column_assignment(**kwargs)

    def get_input_dataframe(self, steps: StepManager, inputs: dict) -> dict:
        inputs["protein_df"] = steps.get_step_output(ImportingStep, "protein_df")
        inputs["metadata_df"] = steps.get_step_output(MetadataImport, "metadata")
        return inputs


class PeptideImport(ImportingStep):
    name = "Peptide import"
    step = "peptide_import"
    method = "peptide_import"
    method_description = "Import peptide data"

    parameter_names = ["file_path", "intensity_name"]
    output_names = ["peptide_df"]

    def method(self, **kwargs):
        return peptide_import(**kwargs)
