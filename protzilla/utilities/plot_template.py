import plotly.io as pio
import plotly.graph_objects as go


from protzilla.disk_operator import YamlOperator
from protzilla.constants.colors import PLOT_PRIMARY_COLOR, PLOT_SECONDARY_COLOR
from protzilla.constants.paths import SETTINGS_PATH

def get_settings(section_id: str):
    op = YamlOperator()
    path = SETTINGS_PATH / (section_id + ".yaml")
    settings = op.read(path)
    return settings

class PlotTemplate:
    def __init__(self):
        params = get_settings("plots")
        self.layout = go.Layout(
            title={
                "font": {
                    "size": params["heading_size"],
                    "family": params["font"]
                },
                "y": 0.98,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top"
            },
            font={
                "size": params["text_size"],
                "family": params["font"]
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
            dragmode="pan"
        )
    
    def update(self, params: dict):
        """
        Updates the used Plotly template. If the dictionary contains a known key, the value will be accepted and saved.
        :param params: Dictionary containing properties of the Plotly template.
        """
        self.layout.title.font.size = params["heading_size"]
        self.layout.title.font.family = params["font"]
        self.layout.font.size = params["text_size"]
        self.layout.font.family = params["font"]
        self.apply()

    def apply(self):
        """
        Applies the current template as default template.
        """
        pio.templates["plotly_protzilla"] = go.layout.Template(layout=self.layout)

template = PlotTemplate()
template.apply()
pio.templates.default = "plotly_protzilla"