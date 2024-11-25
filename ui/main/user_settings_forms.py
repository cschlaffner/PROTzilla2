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

class ExportingPlotsSettingsForm(Form):
    file_format = CustomChoiceField(
        label="File format",
        choices=FileFormat,
        initial=FileFormat.svg
    )
    width = CustomNumberField(
        label="Width (in mm)",
        min_value=10,
        max_value=1000,
        initial=100
    )
    height = CustomNumberField(
        label="Height (in mm)",
        min_value=10,
        max_value=1000,
        initial=80
    )
    font = CustomChoiceField(
        label="Font",
        choices=Font,
        initial=Font.arial
    )
    font_size = CustomNumberField(
        label="Font size",
        min_value=1,
        max_value=100,
        initial=11
    )