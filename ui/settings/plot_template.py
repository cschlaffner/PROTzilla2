import plotly.io as pio
import plotly.graph_objects as go
import math

from protzilla.disk_operator import YamlOperator
from protzilla.constants.colors import PLOT_PRIMARY_COLOR, PLOT_SECONDARY_COLOR
from protzilla.constants.paths import SETTINGS_PATH


SCALED_WIDTH = 600
PT_TO_INCH = 1 / 72
INCH_TO_MM = 25.4
DPI = 300

template = None

def load_settings(section_id: str) -> dict:
    """
    Loads the stored settings for a given settings section.
    :param section_id: The ID of the section that should be loaded.
    :return: Dict containing the loaded settings for given section.
    """
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
    """
    Writes settings into settings section file.
    :param params: Dict with parameter and values from this settings section.
    :param section_id: The ID of the section.
    """
    op = YamlOperator()
    path = SETTINGS_PATH / (section_id + ".yaml")
    op.write(path, params)
    if section_id == "plots" and isinstance(template, PlotTemplate):
        template.update(params)
        template.apply()

def determine_font(params: dict) -> str:
    """
    Returns the selected or a given custom font.
    :param params: Dict with parameter and values from this settings section.
    :return: Selected font.
    """
    if(params["font"] == "Custom"):
        font = params["custom_font"]
    else:
        font = params["font"]
    return font

def resize_for_display(params: dict) -> dict:
    """
    Scales the input sizes to sizes that can be easily displayed in a webbrowser.
    :param params: Dict containing the plot settings.
    :return: Dict containing plot settings with scaled sizes.
    """
    # Figure size
    ratio = params["width"] / params["height"]
    display_height = int(SCALED_WIDTH / ratio)
    
    # Font size
    ratio = SCALED_WIDTH / params["width"]
    display_heading = int(params["heading_size"] * PT_TO_INCH * INCH_TO_MM * ratio)
    display_text = int(params["text_size"] * PT_TO_INCH * INCH_TO_MM * ratio)

    params["display_width"] = SCALED_WIDTH
    params["display_height"] = display_height
    params["display_heading_size"] = display_heading
    params["display_text_size"] = display_text

    return params

def get_scale_factor(
        fig: go.Figure,
        params: dict
    ) -> float:
    """
    Calculates the scale factor for downloading the plot in desired size and resolution.
    :param fig: Plotly figure to be scaled.
    :param params: Dict containing the plot settings.
    :return: Scale factor to scale the whole plot to desired size.
    """
    current_width = fig.layout.width or SCALED_WIDTH
    scale_factor = (params["width"] / INCH_TO_MM * DPI) / current_width

    return scale_factor

class PlotTemplate:
    def __init__(self):
        params = resize_for_display(load_settings("plots"))
        font = determine_font(params)
        self.layout = go.Layout(
            title={
                "font": {
                    "size": params["display_heading_size"],
                    "family": font
                },
                "y": 0.95,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top"
            },
            font={
                "size": params["display_text_size"],
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
            height=params["display_height"],
            width=params["display_width"],
            margin={
                "t": 50,
                "b": 50
            }
        )
    
    def update(self, params: dict):
        """
        Updates all relevant parameters of this Plotly template.
        :param params: Dict containing properties of the Plotly template.
        """
        params = resize_for_display(params)
        font = determine_font(params)
        self.layout.title.font.family = font
        self.layout.font.family = font
     
        self.layout.height = params["display_height"]
        self.layout.width = params["display_width"]
        self.layout.title.font.size = params["display_heading_size"]
        self.layout.font.size = params["display_text_size"]

    def apply(self):
        """
        Applies the current template as default template.
        """
        pio.templates["plotly_protzilla"] = go.layout.Template(layout=self.layout)

template = PlotTemplate()
template.apply()
pio.templates.default = "plotly_protzilla"