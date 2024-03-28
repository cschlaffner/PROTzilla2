from enum import Enum

from protzilla.RunNew import RunNew

from .base import MethodForm
from .custom_fields import CustomBooleanField, CustomChoiceField, CustomFileField


class IntensityType(Enum):
    IBAQ = "iBaq"
    INTENSITY = "Intensity"
    LFQ_INTENSITY = "LFQ Intensity"


class MaxQuantImportForm(MethodForm):
    file = CustomFileField(label="MaxQuant intensities file")
    intensity_parameter = CustomChoiceField(
        choices=IntensityType, label="Intensity parameter"
    )
    mapping_flag = CustomBooleanField(
        label="Map to Uniprot IDs using Biomart (online)", required=False
    )

    description = "MaxQuant data import"

    def submit(self, run: RunNew):
        run.step_calculate(self.cleaned_data)


class FeatureOrientationType(Enum):
    COLUMNS = "Columns (samples in rows, features in columns)"
    ROWS = "Rows (features in rows, samples in columns)"


class MetadataImportForm(MethodForm):
    file = CustomFileField(label="Metadata file")
    feature_orientation = CustomChoiceField(
        choices=FeatureOrientationType, label="Feature orientation"
    )

    description = "Import metadata"

    def submit(self, run: RunNew):
        run.step_calculate(self.cleaned_data)
