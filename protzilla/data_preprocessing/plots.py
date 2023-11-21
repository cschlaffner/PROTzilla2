import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots

from protzilla.data_preprocessing.plots_helper import (
    generate_log_tics,
    generate_lin_tics,
)

from ..constants.colors import (
    PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE,
    PROTZILLA_DISCRETE_COLOR_SEQUENCE,
)


def create_pie_plot(
    names_of_sectors: "list[str]",
    values_of_sectors: "list[int]",
    heading="",
) -> Figure:
    """
    Function to create generic pie graph from data.
    Especially helpful for visualisation of basic parts of
    a whole.

    :param names_of_sectors: Name of parts (so-called sectors) or categories
    :type names_of_sectors: list[str]
    :param values_of_sectors: Corresponding values for sectors
    :type values_of_sectors: list[str]
    :param heading: Header for the graph - for example the topic
    :type heading: str
    :return: returns a pie chart of the data
    :rtype: Figure (plotly object)
    """
    if any(i < 0 for i in values_of_sectors):
        raise ValueError

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
    Function to create generic bar graph from data.
    Especially helpful for visualisation of basic parts of
    a whole.

    :param names_of_sectors: Name of parts (so called sectors) or categories
    :type names_of_sectors: list[str]
    :param values_of_sectors: Corresponding values for sectors
    :type values_of_sectors: list[str]
    :param heading: Header for the graph - for example the topic
    :type heading: str
    :param y_title: Optional y-axis title.
    :type y_title: str
    :param x_title: Optional x-axis title.
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
    visual_transformation="linear",
) -> Figure:
    """
    A function to create a boxplot for visualisation
    of distributions. Assumes that you are comparing two dataframes
    (for example before and after filtering/normalisation) and creates
    a visualisation for each one.

    :param dataframe_a: First dataframe in protzilla long format for\
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
    :param y_title: Optional y-axis title for graphs.
    :type y_title: str
    :param x_title: Optional x-axis title for graphs.
    :type x_title: str
    :param group_by: Optional argument to create a grouped boxplot\
    graph. Arguments can be either "Sample" to group by sample or\
    "Protein ID" to group by protein. Leave "None" to get ungrouped\
    conventional graphs. If set the function will ignore the\
    graph_type argument. Default is "None".
    :type group_by: str
    :return: returns a boxplot of the data
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
    if visual_transformation == "log10":
        fig.update_yaxes(type="log")
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
    visual_transformation="linear",
    overlay=False,
) -> Figure:
    """
    A function to create a histogram for visualisation
    of distributions. Assumes that you are comparing two dataframes
    (for example before and after filtering/normalisation) and creates
    a visualisation for each one.

    :param dataframe_a: First dataframe in protzilla long format for\
    first histogram
    :type dataframe_a: pd.DataFrame
    :param dataframe_b: Second dataframe in protzilla long format\
    for second histogram
    :type dataframe_b: pd.DataFrame
    :param name_a: Name of first histogram
    :type name_a: str
    :param name_b: Name of second histogram
    :type name_b: str
    :param heading: Header or title for the graph (optional)
    :type heading: str
    :param y_title: Optional y axis title for graphs.
    :type y_title: str
    :param x_title: Optional x axis title for graphs.
    :type x_title: str
    :param overlay: Specifies whether to draw one Histogram with overlay or two separate histograms
    :type overlay: bool
    :param visual_transformation: Visual transformation of the y-axis data.
    :type visual_transformation: str
    :return: returns a pie or bar chart of the data
    :rtype: Figure (plotly object)
    """
    intensity_name_a = dataframe_a.columns[3]
    intensity_name_b = dataframe_b.columns[3]

    intensities_a = dataframe_a[intensity_name_a]
    intensities_b = dataframe_b[intensity_name_b]

    if visual_transformation == "log10":
        intensities_a = intensities_a.apply(np.log10)
        intensities_b = intensities_b.apply(np.log10)

    min_value = min(min(intensities_a), min(intensities_b))
    max_value = max(max(intensities_a), max(intensities_b))

    binsize_factor = 0.0005 if visual_transformation == "linear" else 0.02

    trace0 = go.Histogram(
        x=intensities_a,
        marker_color=PROTZILLA_DISCRETE_COLOR_SEQUENCE[0],
        name=name_a,
        xbins=dict(
            start=min_value,
            end=max_value,
            size=(max_value-min_value)*binsize_factor,
        ),
    )
    trace1 = go.Histogram(
        x=intensities_b,
        marker_color=PROTZILLA_DISCRETE_COLOR_SEQUENCE[1],
        name=name_b,
        xbins=dict(
            start=min_value,
            end=max_value,
            size=(max_value-min_value)*binsize_factor,
        ),
    )
    if not overlay:
        fig = make_subplots(rows=1, cols=2)
        fig.add_trace(trace0, 1, 1)
        fig.add_trace(trace1, 1, 2)
        if visual_transformation == "log10":
            fig.update_layout(
                xaxis=generate_log_tics(0, max_value),
                xaxis2=generate_log_tics(0, max_value)
            )
    else:
        fig = go.Figure()
        fig.add_trace(trace0)
        fig.add_trace(trace1)
        fig.update_layout(barmode='overlay')
        fig.update_traces(opacity=0.75)
        if visual_transformation == "log10":
            fig.update_layout(
                xaxis=generate_log_tics(0, max_value)
            )

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

def create_anomaly_score_bar_plot(
    anomaly_df,
    colour_outlier=PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE[1],
    colour_non_outlier=PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE[0],
) -> Figure:
    """
    This function creates a graph visualising the outlier
    and non-outlier samples using the anomaly score.

    :param anomaly_df: pandas Dataframe that contains the anomaly score for each\
    sample, including outliers and on-outliers samples
    :type anomaly_df: pd.DataFrame
    :param colour_outlier: hex code for colour depicting the outliers.
    Default: PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE outlier colour
    :type colour_outlier: str
    :param colour_non_outlier: hex code for colour depicting the
    non-outliers. Default: PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE
    non-outlier colour
    :type colour_non_outlier: str
    :return: returns a plotly Figure object
    :rtype: Figure (plotly object)
    """

    fig = px.bar(
        anomaly_df,
        x=anomaly_df.index,
        y="Anomaly Score",
        hover_name=anomaly_df.index,
        hover_data={
            "Anomaly Score": True,
            "Outlier": True,
        },
        color="Outlier",
        color_discrete_map={
            False: colour_non_outlier,
            True: colour_outlier,
        },
        labels={
            "Sample": "Sample ",
            "Anomaly Score": "Anomaly Score ",
            "Outlier": "Outlier ",
        },
    )
    fig.update_coloraxes(showscale=False)
    fig.update_layout(xaxis={"categoryorder": "category ascending"})
    fig.update_layout(
        yaxis={
            "visible": True,
            "showticklabels": True,
            "gridcolor": "lightgrey",
        },
        xaxis={"visible": False, "showticklabels": False},
        font=dict(size=18, family="Arial"),
        plot_bgcolor="white",
    )

    return fig


def create_pca_2d_scatter_plot(
    pca_df,
    explained_variance_ratio,
    colour_outlier=PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE[1],
    colour_non_outlier=PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE[0],
) -> Figure:
    """
    This function creates a graph visualising the outlier
    and non-outlier points by showing the principal components. It
    returns a ploty Figure object.

    :param pca_df: a DataFrame that contains the projection of\
    the intensity_df on first principal components
    :type pca_df: pd.DataFrame
    :param explained_variance_ratio: a list that contains the\
    explained variation for each component
    :type explained_variance_ratio: list
    :param colour_outlier: hex code for colour depicting the outliers.
    Default: PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE outlier colour
    :type colour_outlier: str
    :param colour_non_outlier: hex code for colour depicting the
    non-outliers. Default: PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE
    non-outlier colour
    :type colour_non_outlier: str
    :return: returns a plotly Figure object
    :rtype: Figure (plotly object)
    """
    fig = go.Figure(
        data=go.Scatter(
            x=pca_df["Component 1"],
            y=pca_df["Component 2"],
            mode="markers",
            marker_color=pca_df["Outlier"].map(
                {True: colour_outlier, False: colour_non_outlier}
            ),
            text=pca_df.index.values,
        )
    )
    e_variance_0 = round(explained_variance_ratio[0], 4) * 100
    e_variance_1 = round(explained_variance_ratio[1], 4) * 100
    fig.update_layout(
        xaxis_title=f"Principal Component 1 ({e_variance_0:.2f} %)",
        yaxis_title=f"Principal Component 2 ({e_variance_1:.2f} %)",
        font=dict(size=14, family="Arial"),
        plot_bgcolor="white",
        yaxis={"gridcolor": "lightgrey", "zerolinecolor": "lightgrey"},
        xaxis={"gridcolor": "lightgrey", "zerolinecolor": "lightgrey"},
    )
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    return fig


def create_pca_3d_scatter_plot(
    pca_df,
    explained_variance_ratio,
    colour_outlier=PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE[1],
    colour_non_outlier=PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE[0],
) -> Figure:
    """
    This function creates a graph visualising the outlier
    and non-outlier points by showing the principal components. It
    returns a ploty Figure object.

    :param pca_df: a DataFrame that contains the projection of\
    the intensity_df on first principal components
    :type pca_df: pd.DataFrame
    :param explained_variance_ratio: a list that contains the\
    explained variation for each component
    :type explained_variance_ratio: list
    :param colour_outlier: hex code for colour depicting the outliers.
    Default: PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE outlier colour
    :type colour_outlier: str
    :param colour_non_outlier: hex code for colour depicting the
    non-outliers. Default: PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE
    non-outlier colour
    :type colour_non_outlier: str
    :return: returns a plotly Figure object
    :rtype: Figure (plotly object)
    """
    fig = go.Figure(
        data=go.Scatter3d(
            x=pca_df["Component 1"],
            y=pca_df["Component 2"],
            z=pca_df["Component 3"],
            mode="markers",
            marker_color=pca_df["Outlier"].map(
                {True: colour_outlier, False: colour_non_outlier}
            ),
            text=pca_df.index.values,
        )
    )
    x_percent = round(explained_variance_ratio[0], 4) * 100
    y_percent = round(explained_variance_ratio[1], 4) * 100
    z_percent = round(explained_variance_ratio[2], 4) * 100

    fig.update_layout(
        scene=dict(
            xaxis_title=(f"Principal Component 1 ({x_percent:.2f} %)"),
            yaxis_title=(f"Principal Component 2 ({y_percent:.2f} %)"),
            zaxis_title=(f"Principal Component 3 ({z_percent:.2f} %)"),
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False),
            zaxis=dict(showticklabels=False),
        ),
        font=dict(size=14, family="Arial"),
        plot_bgcolor="white",
    )

    return fig
