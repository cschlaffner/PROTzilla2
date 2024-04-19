from enum import Enum

from protzilla.methods.importing import MetadataImport
from protzilla.run_v2 import Run

from .base import MethodForm
from .custom_fields import CustomBooleanField, CustomChoiceField, CustomFileField


class IntensityType(Enum):
    IBAQ = "iBAQ"
    INTENSITY = "Intensity"
    LFQ_INTENSITY = "LFQ intensity"


class IntensityNameType(Enum):
    INTENSITY = "Intensity"
    MAXLFQ_TOTAL_iNTENSITY = "MaxLFQ Total Intensity"
    MAXLFQ_INTENSITY = "MaxLFQ Intensity"
    TOTAL_INTENSITY = "Total Intensity"
    MAXLFQ_UNIQUE_INTENSITY = "MaxLFQ Unique Intensity"
    UNIQUE_SPECTRAL_COUNT = "Unique Spectral Count"
    UNIQUE_INTENSITY = "Unique Intensity"
    SPECTRAL_COUNT = "Spectral Count"
    TOTAL_SPECTRAL_COUNT = "Total Spectral Count"


class FeatureOrientationType(Enum):
    COLUMNS = "Columns (samples in rows, features in columns)"
    ROWS = "Rows (features in rows, samples in columns)"


class EmptyEnum(Enum):
    pass


class MaxQuantImportForm(MethodForm):
    file_path = CustomFileField(label="MaxQuant intensities file")
    intensity_name = CustomChoiceField(
        choices=IntensityType, label="Intensity parameter"
    )
    map_to_uniprot = CustomBooleanField(
        label="Map to Uniprot IDs using Biomart (online)", required=False
    )


class DiannImportForm(MethodForm):
    file_path = CustomFileField(label="DIA-NN intensities file:")
    map_to_uniprot = CustomBooleanField(
        label="Map to Uniprot IDs using Biomart (online)", required=False
    )


class MSFraggerImportForm(MethodForm):
    file_path = CustomFileField(label="MSFragger intensities file")
    intensity_name = CustomChoiceField(
        choices=IntensityNameType, label="intensity name"
    )
    map_to_uniprot = CustomBooleanField(
        label="Map to Uniprot IDs using Biomart (online)", required=False
    )


class MetadataImportForm(MethodForm):
    file_path = CustomFileField(label="Metadata file")
    feature_orientation = CustomChoiceField(
        choices=FeatureOrientationType, label="Feature orientation"
    )


class MetadataImportMethodDiannForm(MethodForm):
    filepath = CustomFileField(label="Run-Relationship metadata file:")
    groupby_sample = CustomBooleanField(
        label="Group replicate runs by sample using median", required=False
    )


class MetadataColumnAssignmentForm(MethodForm):
    metadata_required_column = CustomChoiceField(
        choices=EmptyEnum,
        label="Missing, but required metadata columns",
        required=False,
    )
    metadata_unknown_column = CustomChoiceField(
        choices=EmptyEnum,
        label="Existing, but unknown metadata columns",
        required=False,
    )

    def fill_form(self, run: Run) -> None:
        metadata = run.steps.get_step_output(MetadataImport, "metadata_df")

        if metadata is not None:
            self.fields["metadata_required_column"].choices = [
                (col, col)
                for col in ["Sample", "Group", "Batch"]
                if col not in metadata.columns
            ]
            if len(self.fields["metadata_required_column"].choices) == 0:
                self.fields["metadata_required_column"].choices = [
                    (None, "No required columns missing")
                ]
                self.fields["metadata_required_column"].disabled = True

            self.fields["metadata_unknown_column"].choices = metadata.columns[
                ~metadata.columns.isin(["Sample", "Group", "Batch"])
            ].unique()
            if len(self.fields["metadata_unknown_column"].choices) == 0:
                self.fields["metadata_unknown_column"].choices = [
                    (None, "No unknown columns")
                ]
                self.fields["metadata_unknown_column"].disabled = True


class PeptideImportForm(MethodForm):
    file_path = CustomFileField(label="Peptide file")
    intensity_name = CustomChoiceField(
        choices=IntensityType, label="Intensity parameter (same as MS-Data)"
    )
