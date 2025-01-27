import plotly.io as pio
import plotly.graph_objects as go

from protzilla.disk_operator import YamlOperator
from protzilla.constants.colors import PLOT_PRIMARY_COLOR, PLOT_SECONDARY_COLOR
from protzilla.constants.paths import SETTINGS_PATH


def load_settings(section_id: str):
    # TO DO: Muss hier per default das Tenplate geupdated und applied werden?
    op = YamlOperator()
    path = SETTINGS_PATH / (section_id + ".yaml")
    if path.exists():
        settings = op.read(path)
    else:
        default_path = SETTINGS_PATH / (section_id + "_default.yaml")
        settings = op.read(default_path)
        save_settings(settings, section_id)
    return settings

def save_settings(params: dict, section_id: str):
    op = YamlOperator()
    path = SETTINGS_PATH / (section_id + ".yaml")
    op.write(path, params)
    if template:
        template.update(params)
        template.apply()

def determine_font(params: dict):
    """
    This method determines if a custom font was selected or not.
    """
    if(params["font"] == "Custom"):
        font = params["custom_font"]
    else:
        font = params["font"]
    return font

def convert_millimeter_to_pixel(millimeter: int):
    inches = millimeter / 25.4
    dpi = 300
    pixel = inches * dpi
    return pixel

class PlotTemplate:
    def __init__(self):
        params = load_settings("plots")
        font = determine_font(params)
        self.layout = go.Layout(
            title={
                "font": {
                    "size": params["heading_size"],
                    "family": font
                },
                "y": 0.98,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top"
            },
            font={
                "size": params["text_size"],
                "family": font
            },
            colorway=[PLOT_PRIMARY_COLOR, PLOT_SECONDARY_COLOR],
            plot_bgcolor="white",
            yaxis={
                "gridcolor": "lightgrey",
                "zerolinecolor": "lightgrey"
            },
            modebar={
                "remove": ["autoScale2d", "lasso", "lasso2d", "toImage", "select2d"],
            },
            dragmode="pan",
            height=convert_millimeter_to_pixel(params["height"]),
            width=convert_millimeter_to_pixel(params["width"])
        )
    
    def update(self, params: dict):
        """
        Updates the used Plotly template. If the dictionary contains a known key, the value will be accepted and saved.
        :param params: Dictionary containing properties of the Plotly template.
        """
        font = determine_font(params)
        self.layout.title.font.size = params["heading_size"]
        self.layout.title.font.family = font
        self.layout.font.size = params["text_size"]
        self.layout.font.family = font
        self.layout.height = convert_millimeter_to_pixel(params["height"])
        self.layout.width = convert_millimeter_to_pixel(params["width"])

    def apply(self):
        """
        Applies the current template as default template.
        """
        pio.templates["plotly_protzilla"] = go.layout.Template(layout=self.layout)

template = PlotTemplate()
template.apply()
pio.templates.default = "plotly_protzilla"