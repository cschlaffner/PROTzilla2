from typing import Dict
import plotly.express as px
from plotly.graph_objects import Figure
import plotly.graph_objects as go
from ..constants.constants import PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE, PROTZILLA_DISCRETE_COLOR_SEQUENCE
from plotly.subplots import make_subplots
import pandas as pd


def create_pie_plot(
    names_of_sectors: "list[str]",
    values_of_sectors: "list[int]",
    heading="",
) -> Figure:
    """
    Function to create generic bar or pie graphs from data.
    Especially helpful for visualisation of basic parts of
    a whole.

    :param names_of_sectors: Name of parts (so called sectors) or categories
    :type names_of_sectors: list[str]
    :param values_of_sectors: Corresponding values for sectors
    :type values_of_sectors: list[str]
    :param heading: Header for the graph - for example the topic
    :type heading: str
    :return: returns a pie chart of the data
    :rtype: Figure (plotly object)
    """
    fig = px.pie(
        names=names_of_sectors,
        values=values_of_sectors,
        color_discrete_sequence=PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE,
    )

    fig.update_layout(
        title={
            "text": f"<b>{heading}</b>",
            "font": dict(size=16),
            "y": 0.98,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        font=dict(size=14, family="Arial"),
    )
    return fig


def create_bar_plot(
    names_of_sectors: "list[str]",
    values_of_sectors: "list[int]",
    heading="",
    colour: "list[str]" = PROTZILLA_DISCRETE_COLOR_SEQUENCE,
    y_title="",
    x_title="",
) -> Figure:
    """
    Function to create generic bar or pie graphs from data.
    Especially helpful for visualisation of basic parts of
    a whole.

    :param names_of_sectors: Name of parts (so called sectors) or categories
    :type names_of_sectors: list[str]
    :param values_of_sectors: Corresponding values for sectors
    :type values_of_sectors: list[str]
    :param heading: Header for the graph - for example the topic
    :type heading: str
    :param y_title: Optional y axis title.
    :type y_title: str
    :param x_title: Optional x axis title.
    :type x_title: str
    :return: returns a bar chart of the data
    :rtype: Figure (plotly object)
    """

    fig = px.bar(
        x=names_of_sectors,
        y=values_of_sectors,
        color=colour[: len(values_of_sectors)],
        color_discrete_map="identity",
    )

    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        plot_bgcolor="white",
        yaxis={"gridcolor": "lightgrey", "zerolinecolor": "lightgrey"},
    )

    fig.update_layout(
        title={
            "text": f"<b>{heading}</b>",
            "font": dict(size=16),
            "y": 0.98,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        font=dict(size=14, family="Arial"),
    )
    return fig


def create_box_plots(
    dataframe_a: pd.DataFrame,
    dataframe_b: pd.DataFrame,
    name_a="",
    name_b="",
    heading="",
    y_title="",
    x_title="",
    group_by: str = "None",
) -> Figure:
    """
    A function to create a boxplots and histograms for visualisation
    of distributions. Assumes that you are comparing two dataframes
    (for example before and after filtering/normalisation) and creates
    a visualisation for each one.

    :param dataframe_a: First dataframe in portzilla long format for\
    first boxplot
    :type dataframe_a: pd.DataFrame
    :param dataframe_b: Second dataframe in protzilla long format\
    for second boxplot
    :type dataframe_b: pd.DataFrame
    :param name_a: Name of first boxplot
    :type name_a: str
    :param name_b: Name of second boxplot
    :type name_b: str
    :param heading: Header or title for the graph (optional)
    :type heading: str
    :param graph_type: Defines the type of graph displayed. Can be\
    either "box" (boxplot) or "hist" (histogram). Default is "box"
    :type graph_type: str
    :param colour: Defines the sequence of colours used for the graph.\
    Can be any sequence from px.colors.qualitative or simply a\
    self-designed list containing hex strings for colors. Uses same\
    order as names and values.Default is a sequence that\
    matches protzilla typical colors\
    (PROTZILLA_DISCRETE_COLOR_SEQUENCE).
    :type colour: list[str]
    :param y_title: Optional y axis title for graphs.
    :type y_title: str
    :param x_title: Optional x axis title for graphs.
    :type x_title: str
    :param group_by: Optional argument to create a grouped boxplot\
    graph. Arguments can be either "Sample" to group by sample or\
    "Protein ID" to group by protein. Leave "None" to get ungrouped\
    conventional graphs. If set the function will ignore the\
    graph_type argument. Default is "None".
    :type group_by: str
    **kwargs: Additional parameters passed to go.BoxPlot\
    or histogram functions
    :return: returns a pie or bar chart of the data
    :rtype: Figure (plotly object)
    """
    if group_by not in {"None", "Sample", "Protein ID"}:
        raise ValueError(
            f"""Group_by parameter  must be "None" or
                "Sample" or "Protein ID" but is {group_by}"""
        )
    intensity_name_a = dataframe_a.columns[3]
    intensity_name_b = dataframe_b.columns[3]
    if group_by in {"Sample", "Protein ID"}:
        fig = make_subplots(rows=1, cols=2)
        trace0 = go.Box(
            y=dataframe_a[intensity_name_a],
            x=dataframe_a[group_by],
            marker_color=PROTZILLA_DISCRETE_COLOR_SEQUENCE[0],
            name=name_a,
        )
        trace1 = go.Box(
            y=dataframe_b[intensity_name_b],
            x=dataframe_b[group_by],
            marker_color=PROTZILLA_DISCRETE_COLOR_SEQUENCE[1],
            name=name_b,
        )
        fig.add_trace(trace0, 1, 1)
        fig.add_trace(trace1, 1, 2)
        fig.update_xaxes(showticklabels=False)

    elif group_by == "None":
        fig = make_subplots(rows=1, cols=2)
        trace0 = go.Box(
            y=dataframe_a[intensity_name_a],
            marker_color=PROTZILLA_DISCRETE_COLOR_SEQUENCE[0],
            name=name_a,
        )
        trace1 = go.Box(
            y=dataframe_b[intensity_name_b],
            marker_color=PROTZILLA_DISCRETE_COLOR_SEQUENCE[1],
            name=name_b,
        )
        fig.add_trace(trace0, 1, 1)
        fig.add_trace(trace1, 1, 2)

    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        font=dict(size=14, family="Arial"),
        plot_bgcolor="white",
        yaxis1={"gridcolor": "lightgrey", "zerolinecolor": "lightgrey"},
        yaxis2={"gridcolor": "lightgrey", "zerolinecolor": "lightgrey"},
        title={
            "text": f"<b>{heading}</b>",
            "font": dict(size=16),
            "y": 0.98,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
    )
    fig.update_yaxes(rangemode="tozero")
    return fig


def create_histograms(
    dataframe_a: pd.DataFrame,
    dataframe_b: pd.DataFrame,
    name_a="",
    name_b="",
    heading="",
    y_title="",
    x_title="",
) -> Figure:
    """
    A function to create a boxplots and histograms for visualisation
    of distributions. Assumes that you are comparing two dataframes
    (for example before and after filtering/normalisation) and creates
    a visualisation for each one.

    :param dataframe_a: First dataframe in portzilla long format for\
    first boxplot
    :type dataframe_a: pd.DataFrame
    :param dataframe_b: Second dataframe in protzilla long format\
    for second boxplot
    :type dataframe_b: pd.DataFrame
    :param name_a: Name of first boxplot
    :type name_a: str
    :param name_b: Name of second boxplot
    :type name_b: str
    :param heading: Header or title for the graph (optional)
    :type heading: str
    :param graph_type: Defines the type of graph displayed. Can be\
    either "box" (boxplot) or "hist" (histogram). Default is "box"
    :type graph_type: str
    :param colour: Defines the sequence of colours used for the graph.\
    Can be any sequence from px.colors.qualitative or simply a\
    self-designed list containing hex strings for colors. Uses same\
    order as names and values.Default is a sequence that\
    matches protzilla typical colors\
    (PROTZILLA_DISCRETE_COLOR_SEQUENCE).
    :type colour: list[str]
    :param y_title: Optional y axis title for graphs.
    :type y_title: str
    :param x_title: Optional x axis title for graphs.
    :type x_title: str
    :param group_by: Optional argument to create a grouped boxplot\
    graph. Arguments can be either "Sample" to group by sample or\
    "Protein ID" to group by protein. Leave "None" to get ungrouped\
    conventional graphs. If set the function will ignore the\
    graph_type argument. Default is "None".
    :type group_by: str
    **kwargs: Additional parameters passed to go.BoxPlot\
    or histogram functions
    :return: returns a pie or bar chart of the data
    :rtype: Figure (plotly object)
    """
    intensity_name_a = dataframe_a.columns[3]
    intensity_name_b = dataframe_b.columns[3]
    fig = make_subplots(rows=1, cols=2)
    trace0 = go.Histogram(
        x=dataframe_a[intensity_name_a],
        marker_color=PROTZILLA_DISCRETE_COLOR_SEQUENCE[0],
        name=name_a,
    )
    trace1 = go.Histogram(
        x=dataframe_b[intensity_name_b],
        marker_color=PROTZILLA_DISCRETE_COLOR_SEQUENCE[1],
        name=name_b,
    )
    fig.add_trace(trace0, 1, 1)
    fig.add_trace(trace1, 1, 2)
    fig.update_layout(bargap=0.2)

    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        font=dict(size=14, family="Arial"),
        plot_bgcolor="white",
        yaxis1={"gridcolor": "lightgrey", "zerolinecolor": "lightgrey"},
        yaxis2={"gridcolor": "lightgrey", "zerolinecolor": "lightgrey"},
        title={
            "text": f"<b>{heading}</b>",
            "font": dict(size=16),
            "y": 0.98,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
    )
    fig.update_yaxes(rangemode="tozero")
    return fig
