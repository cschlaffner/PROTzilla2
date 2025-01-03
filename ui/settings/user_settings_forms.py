from enum import Enum
from django.forms import Form
from ui.runs.forms.custom_fields import CustomChoiceField, CustomNumberField

class FileFormat(Enum):
    png = "png"
    tiff = "tiff"
    svg = "svg"
    pdf = "pdf"
    eps = "eps"
    jpg = "jpg"

class Font(Enum):
    arial = "Arial"
    sans_serif = "Sans Serif"

class ExportingPlotsSettingsForm(Form):
    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial', {})
        super().__init__(*args, **kwargs)
        for field_name, value in initial.items():
            if field_name in self.fields:
                self.fields[field_name].initial = value

    file_format = CustomChoiceField(
        label="File format",
        choices=FileFormat
    )
    width = CustomNumberField(
        label="Width (in mm)",
        min_value=10,
        max_value=1000
    )
    height = CustomNumberField(
        label="Height (in mm)",
        min_value=10,
        max_value=1000
    )
    font = CustomChoiceField(
        label="Font",
        choices=Font
    )
    font_size = CustomNumberField(
        label="Font size",
        min_value=1,
        max_value=100
    )