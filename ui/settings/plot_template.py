import plotly.io as pio
import plotly.graph_objects as go
import math

from protzilla.disk_operator import YamlOperator
from protzilla.constants.colors import PLOT_PRIMARY_COLOR, PLOT_SECONDARY_COLOR
from protzilla.constants.paths import SETTINGS_PATH

SCALED_WIDTH = 600

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
    if section_id == "plots" and template:
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

# TO DO: Adjust font size as well
def resize_for_web(
        width: int,
        height: int
) -> dict:
    """
    Scales the input sizes to sizes that can be easily displayed in a webbrowser.
    :param width: Plot width from user input.
    :param height: Plot height from user input.
    :return: Dict containing the scaled sizes.
    """
    ratio = width / height
    scaled_height = SCALED_WIDTH / ratio
    
    return dict(
        width=SCALED_WIDTH,
        height=int(scaled_height)
    )

def adjust_for_export(
        fig: go.Figure,
        params: dict
    ) -> int:
    """
    Calculates the scale factor for downloading the plot in desired size and resolution.
    Adjusts the font sizes in Plotly figure to maintain experienced sizes after scaling.
    :param fig: Plotly figure to be scaled.
    :param params: Dict containing the plot settings.
    :return: Figure with scaled font size and scale factor to scale the whole plot to desired size.
    """
    dpi = 300
    current_width = fig.layout.width or SCALED_WIDTH
    scale_factor = (params["width"] / 24.5 * dpi) / current_width

    pt_to_mm = 1 / 72 * 24.5
    font_ratio = current_width / params["width"]
    fig.update_layout(
        title = {
            "font": {
                "size": int(params["heading_size"] * pt_to_mm * font_ratio)
            }
        },
        font = {
            "size": int(params["text_size"] * pt_to_mm * font_ratio)
        }
    )
    return fig, scale_factor

class PlotTemplate:
    def __init__(self):
        params = load_settings("plots")
        font = determine_font(params)
        sizes = resize_for_web(
            params["width"],
            params["height"]
        )
        self.layout = go.Layout(
            title={
                "font": {
                    "size": params["heading_size"],
                    "family": font
                },
                "y": 0.95,
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
            height=sizes["height"],
            width=sizes["width"],
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
        font = determine_font(params)
        self.layout.title.font.family = font
        self.layout.font.family = font
     
        sizes = resize_for_web(
            params["width"],
            params["height"]
        )
        self.layout.height = sizes["height"]
        self.layout.width = sizes["width"]
        self.layout.title.font.size = params["heading_size"]
        self.layout.font.size = params["text_size"]

    def apply(self):
        """
        Applies the current template as default template.
        """
        pio.templates["plotly_protzilla"] = go.layout.Template(layout=self.layout)

template = PlotTemplate()
template.apply()
pio.templates.default = "plotly_protzilla"