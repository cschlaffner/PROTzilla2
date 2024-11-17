import plotly.io as pio
import plotly.graph_objects as go

from protzilla.constants.colors import PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE


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
    colorway= PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE,
    plot_bgcolor="white",
    yaxis={
        "gridcolor": "lightgrey",
        "zerolinecolor": "lightgrey"
    }
)
pio.templates["plotly_protzilla"] = go.layout.Template(layout=layout)
pio.templates.default = "plotly_protzilla"