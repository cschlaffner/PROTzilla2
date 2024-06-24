from enum import Enum

from protzilla.methods.importing import ImportingStep
from protzilla.run import Run

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


class AggregationMethods(Enum):
    sum = "Sum"
    median = "Median"
    mean = "Mean"


class MaxQuantImportForm(MethodForm):
    file_path = CustomFileField(label="MaxQuant intensities file")
    intensity_name = CustomChoiceField(
        choices=IntensityType, label="Intensity parameter"
    )
    map_to_uniprot = CustomBooleanField(
        label="Map to Uniprot IDs using Biomart (online)", required=False
    )
    aggregation_method = CustomChoiceField(
        choices=AggregationMethods, label="Aggregation method", initial="Sum"
    )


class DiannImportForm(MethodForm):
    file_path = CustomFileField(label="DIA-NN intensities file:")
    map_to_uniprot = CustomBooleanField(
        label="Map to Uniprot IDs using Biomart (online)", required=False
    )
    aggregation_method = CustomChoiceField(
        choices=AggregationMethods, label="Aggregation method", initial="Sum"
    )


class MSFraggerImportForm(MethodForm):
    file_path = CustomFileField(label="MSFragger intensities file")
    intensity_name = CustomChoiceField(
        choices=IntensityNameType, label="intensity name"
    )
    map_to_uniprot = CustomBooleanField(
        label="Map to Uniprot IDs using Biomart (online)", required=False
    )
    aggregation_method = CustomChoiceField(
        choices=AggregationMethods, label="Aggregation method", initial="Sum"
    )


class MetadataImportForm(MethodForm):
    file_path = CustomFileField(label="Metadata file")
    feature_orientation = CustomChoiceField(
        choices=FeatureOrientationType, label="Feature orientation"
    )


class MetadataImportMethodDiannForm(MethodForm):
    file_path = CustomFileField(label="Run-Relationship metadata file:")
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
        print("Calling fill_form")
        metadata = run.steps.get_step_output(
            ImportingStep, "metadata_df", include_current_step=True
        )

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

            unknown_columns = list(
                metadata.columns[
                    ~metadata.columns.isin(["Sample", "Group", "Batch"])
                ].unique()
            )

            self.fields["metadata_unknown_column"].choices = [
                (col, col) for col in unknown_columns
            ]
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
    map_to_uniprot = CustomBooleanField(
        label="Map to Uniprot IDs using Biomart (online)", required=False
    )

    def fill_form(self, run: Run) -> None:
        from protzilla.methods.importing import (
            DiannImport,
            MaxQuantImport,
            MsFraggerImport,
        )

        self.fields["intensity_name"].initial = run.steps.get_step_input(
            [MaxQuantImport, MsFraggerImport, DiannImport], "intensity_name"
        )

        self.fields["map_to_uniprot"].initial = run.steps.get_step_input(
            [MaxQuantImport, MsFraggerImport, DiannImport], "map_to_uniprot"
        )


class EvidenceImportForm(MethodForm):
    file_path = CustomFileField(label="Evidence file")
    intensity_name = CustomChoiceField(
        choices=IntensityType, label="Intensity parameter"
    )
    map_to_uniprot = CustomBooleanField(
        label="Map to Uniprot IDs using Biomart (online)", required=False
    )

    def fill_form(self, run: Run) -> None:
        from protzilla.methods.importing import (
            DiannImport,
            MaxQuantImport,
            MsFraggerImport,
        )

        self.fields["intensity_name"].initial = run.steps.get_step_input(
            [MaxQuantImport, MsFraggerImport, DiannImport], "intensity_name"
        )

        self.fields["map_to_uniprot"].initial = run.steps.get_step_input(
            [MaxQuantImport, MsFraggerImport, DiannImport], "map_to_uniprot"
        )
