import plotly.io as pio
import plotly.graph_objects as go

from protzilla.constants.colors import *


layout = go.Layout(
    title={
        "font": {
            "size": 16,
            "family": "Arial"
        },
        "y": 0.98,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top"
    },
    font={
        "size": 14,
        "family": "Arial"
    },
    colorway=[PROTZILLA_PRIMARY_COLOR, PROTZILLA_SECONDARY_COLOR],
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
pio.templates["plotly_protzilla"] = go.layout.Template(layout=layout)
pio.templates.default = "plotly_protzilla"