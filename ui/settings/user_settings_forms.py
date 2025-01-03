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
    # Currently available fonts for Plotly https://plotly.com/python-api-reference/generated/plotly.graph_objects.layout.title.html?highlight=layout%20title#plotly.graph_objects.layout.title.Font.family
    arial = "Arial"
    balto = "Balto"
    courier_new = "Courier New"
    droid_sans = "Droid Sans"
    droid_serif = "Droid Serif"
    droid_sans_mono = "Droid Sans Mono"
    gravitas_one = "Gravitas One"
    old_standard_tt = "Old Standard TT"
    open_sans = "Open Sans"
    overpass = "Overpass"
    pt_sans_narrow = "PT Sans Narrow"
    raleway = "Raleway"
    sans_serif = "Sans Serif"
    times_new_roman = "Times New Roman"
    verdana = "Verdana"

class ExportingPlotsSettingsForm(Form):
    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial', {})
        super().__init__(*args, **kwargs)
        for field_name, value in initial.items():
            if field_name in self.fields:
                self.fields[field_name].initial = value

    file_format = CustomChoiceField(
        label="Download file format",
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
    heading_size = CustomNumberField(
        label="Heading size",
        min_value=1,
        max_value=100
    )
    text_size = CustomNumberField(
        label="Text size",
        min_value=1,
        max_value=100
    )