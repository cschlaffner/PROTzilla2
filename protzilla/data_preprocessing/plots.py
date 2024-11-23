import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots

from protzilla.data_preprocessing.plots_helper import generate_tics
from protzilla.utilities import default_intensity_column
from protzilla.utilities.plot_template import *
from protzilla.constants.colors import *

def create_pie_plot(
    names_of_sectors: "list[str]",
    values_of_sectors: "list[int]",
    heading: str = "",
) -> Figure:
    """
    Function to create generic pie graph from data.
    Especially helpful for visualisation of basic parts of
    a whole.

    :param names_of_sectors: Name of parts (so-called sectors) or categories
    :param values_of_sectors: Corresponding values for sectors
    :param heading: Header for the graph - for example the topic
    :return: returns a pie chart of the data
    """
    if any(i < 0 for i in values_of_sectors):
        raise ValueError

    fig = px.pie(
        names=names_of_sectors,
        values=values_of_sectors
    )

    fig.update_layout(title={"text": f"<b>{heading}</b>"})
    fig.update_traces(hovertemplate="%{label} <br>Amount: %{value}")
    return fig


def create_bar_plot(
    names_of_sectors: "list[str]",
    values_of_sectors: "list[int]",
    heading: str = "",
    y_title: str = "",
    x_title: str = "",
) -> Figure:
    """
    Function to create generic bar graph from data.
    Especially helpful for visualisation of basic parts of
    a whole.

    :param names_of_sectors: Name of parts (so called sectors) or categories
    :param values_of_sectors: Corresponding values for sectors
    :param heading: Header for the graph - for example the topic
    :param y_title: Optional y-axis title.
    :param x_title: Optional x-axis title.
    :return: returns a bar chart of the data
    """

    fig = px.bar(
        x=names_of_sectors,
        y=values_of_sectors,
        color=[PLOT_PRIMARY_COLOR, PLOT_SECONDARY_COLOR],
        color_discrete_map="identity"
    )

    fig.update_layout(title={"text": f"<b>{heading}</b>"})
    fig.update_xaxes(title=x_title)
    fig.update_yaxes(title=y_title)
    return fig


def create_box_plots(
    dataframe_a: pd.DataFrame,
    dataframe_b: pd.DataFrame,
    name_a: str = "",
    name_b: str = "",
    heading: str = "",
    y_title: str = "",
    x_title: str = "",
    group_by: str = "None",
    visual_transformation: str = "linear",
) -> Figure:
    """
    A function to create a boxplot for visualisation
    of distributions. Assumes that you are comparing two dataframes
    (for example before and after filtering/normalisation) and creates
    a visualisation for each one.

    :param dataframe_a: First dataframe in protzilla long format for\
    first boxplot
    :param dataframe_b: Second dataframe in protzilla long format\
    for second boxplot

    :param name_a: Name of first boxplot
    :param name_b: Name of second boxplot
    :param heading: Header or title for the graph (optional)
    :param y_title: Optional y-axis title for graphs.
    :param x_title: Optional x-axis title for graphs.
    :param group_by: Optional argument to create a grouped boxplot\
    :param visual_transformation: Visual transformation of the y-axis data.
    graph. Arguments can be either "Sample" to group by sample or\
    "Protein ID" to group by protein. Leave "None" to get ungrouped\
    conventional graphs. If set the function will ignore the\
    graph_type argument. Default is "None".
    :return: returns a boxplot of the data
    """
    if group_by not in {"None", "Sample", "Protein ID"}:
        raise ValueError(
            f"""Group_by parameter  must be "None" or
                "Sample" or "Protein ID" but is {group_by}"""
        )
    intensity_name_a = default_intensity_column(dataframe_a)
    intensity_name_b = default_intensity_column(dataframe_b)
    if group_by in {"Sample", "Protein ID"}:
        fig = make_subplots(rows=1, cols=2)
        trace0 = go.Box(
            y=dataframe_a[intensity_name_a],
            x=dataframe_a[group_by],
            marker_color=PLOT_PRIMARY_COLOR,
            name=name_a
        )
        trace1 = go.Box(
            y=dataframe_b[intensity_name_b],
            x=dataframe_b[group_by],
            marker_color=PLOT_SECONDARY_COLOR,
            name=name_b
        )
        fig.add_trace(trace0, 1, 1)
        fig.add_trace(trace1, 1, 2)
        fig.update_xaxes(showticklabels=False)

    elif group_by == "None":
        fig = make_subplots(rows=1, cols=2)
        trace0 = go.Box(
            y=dataframe_a[intensity_name_a],
            marker_color=PLOT_PRIMARY_COLOR,
            name=name_a
        )
        trace1 = go.Box(
            y=dataframe_b[intensity_name_b],
            marker_color=PLOT_SECONDARY_COLOR,
            name=name_b
        )
        fig.add_trace(trace0, 1, 1)
        fig.add_trace(trace1, 1, 2)

    fig.update_layout(title={"text": f"<b>{heading}</b>"})
    fig.update_xaxes(title=x_title)
    fig.update_yaxes(
        title=y_title,
        rangemode="tozero"
    )
    if visual_transformation == "log10":
        fig.update_yaxes(type="log")
    return fig


def create_histograms(
    dataframe_a: pd.DataFrame,
    dataframe_b: pd.DataFrame,
    name_a: str = "",
    name_b: str = "",
    heading: str = "",
    y_title: str = "",
    x_title: str = "",
    visual_transformation: str = "linear",
    overlay: bool = False,
) -> Figure:
    """
    A function to create a histogram for visualisation
    of distributions. Assumes that you are comparing two dataframes
    (for example before and after filtering/normalisation) and creates
    a visualisation for each one.

    :param dataframe_a: First dataframe in protzilla long format for\
    first histogram
    :param dataframe_b: Second dataframe in protzilla long format\
    for second histogram

    :param name_a: Name of first histogram
    :param name_b: Name of second histogram
    :param heading: Header or title for the graph (optional)
    :param y_title: Optional y axis title for graphs.
    :param x_title: Optional x axis title for graphs.
    :param overlay: Specifies whether to draw one Histogram with overlay or two separate histograms
    :param visual_transformation: Visual transformation of the y-axis data.

    :return: returns a pie or bar chart of the data
    """
    if visual_transformation not in {"linear", "log10"}:
        raise ValueError(
            f"""visual_transformation parameter  must be "linear" or
                "log10" but is {visual_transformation}"""
        )

    intensity_name_a = default_intensity_column(dataframe_a)
    intensity_name_b = default_intensity_column(dataframe_b)

    intensities_a = dataframe_a[intensity_name_a]
    intensities_b = dataframe_b[intensity_name_b]

    if visual_transformation == "log10":
        intensities_a = intensities_a.apply(np.log10)
        intensities_b = intensities_b.apply(np.log10)

    min_value = min(intensities_a.min(skipna=True), intensities_b.min(skipna=True))
    max_value = max(intensities_a.max(skipna=True), intensities_b.max(skipna=True))

    number_of_bins = 100
    binsize_a = (
        intensities_a.max(skipna=True) - intensities_a.min(skipna=True)
    ) / number_of_bins
    binsize_b = (
        intensities_b.max(skipna=True) - intensities_b.min(skipna=True)
    ) / number_of_bins

    if overlay:
        binsize_a = binsize_b = max(binsize_a, binsize_b)

    trace0 = go.Histogram(
        x=intensities_a,
        marker_color=PLOT_PRIMARY_COLOR,
        name=name_a,
        xbins=dict(start=min_value, end=max_value, size=binsize_a),
    )
    trace1 = go.Histogram(
        x=intensities_b,
        marker_color=PLOT_SECONDARY_COLOR,
        name=name_b,
        xbins=dict(start=min_value, end=max_value, size=binsize_b),
    )
    if not overlay:
        fig = make_subplots(rows=1, cols=2)
        fig.add_trace(trace0, 1, 1)
        fig.add_trace(trace1, 1, 2)
        if visual_transformation == "log10":
            fig.update_layout(
                xaxis=generate_tics(0, max_value, True),
                xaxis2=generate_tics(0, max_value, True),
            )
    else:
        fig = go.Figure()
        fig.add_trace(trace0)
        fig.add_trace(trace1)
        fig.update_layout(barmode="overlay")
        fig.update_traces(opacity=0.75)
        if visual_transformation == "log10":
            fig.update_layout(xaxis=generate_tics(0, max_value, True))

    fig.update_layout(title={"text": f"<b>{heading}</b>"})
    fig.update_xaxes(title=x_title)
    fig.update_yaxes(
        title=y_title,
        rangemode="tozero"
    )
    return fig


def create_anomaly_score_bar_plot(
    anomaly_df: pd.DataFrame,
    colour_outlier: str = PLOT_SECONDARY_COLOR,
    colour_non_outlier: str = PLOT_PRIMARY_COLOR,
) -> Figure:
    """
    This function creates a graph visualising the outlier
    and non-outlier samples using the anomaly score.

    :param anomaly_df: pandas Dataframe that contains the anomaly score for each\
    sample, including outliers and on-outliers samples
    :param colour_outlier: hex code for colour depicting the outliers.
    Default: PROTZILLA_SECONDARY_COLOR
    :param colour_non_outlier: hex code for colour depicting the
    non-outliers. Default: PROTZILLA_PRIMARY_COLOR
    :return: returns a plotly Figure object
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
    fig.update_xaxes(
        categoryorder="category ascending",
        visible=False,
        showticklabels=False
    )
    fig.update_yaxes(
        visible=True,
        showticklabels=True
    )
    return fig


def create_pca_2d_scatter_plot(
    pca_df: pd.DataFrame,
    explained_variance_ratio: list,
    colour_outlier: str = PLOT_SECONDARY_COLOR,
    colour_non_outlier: str = PLOT_PRIMARY_COLOR,
) -> Figure:
    """
    This function creates a graph visualising the outlier
    and non-outlier points by showing the principal components. It
    returns a ploty Figure object.

    :param pca_df: a DataFrame that contains the projection of\
    the intensity_df on first principal components
    :param explained_variance_ratio: a list that contains the\
    explained variation for each component
    :param colour_outlier: hex code for colour depicting the outliers.
    Default: PROTZILLA_SECONDARY_COLOR
    :param colour_non_outlier: hex code for colour depicting the
    non-outliers. Default: PROTZILLA_PRIMARY_COLOR

    :return: returns a plotly Figure object
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
    fig.update_xaxes(
        showticklabels=False,
        title=f"Principal Component 1 ({e_variance_0:.2f} %)"
    )
    fig.update_yaxes(
        showticklabels=False,
        title=f"Principal Component 2 ({e_variance_1:.2f} %)"
    )
    return fig


def create_pca_3d_scatter_plot(
    pca_df: pd.DataFrame,
    explained_variance_ratio: list,
    colour_outlier: str = PLOT_SECONDARY_COLOR,
    colour_non_outlier: str = PLOT_PRIMARY_COLOR,
) -> Figure:
    """
    This function creates a graph visualising the outlier
    and non-outlier points by showing the principal components. It
    returns a ploty Figure object.

    :param pca_df: a DataFrame that contains the projection of\
    the intensity_df on first principal components
    :param explained_variance_ratio: a list that contains the\
    explained variation for each component
    :param colour_outlier: hex code for colour depicting the outliers.
    Default: PROTZILLA_SECONDARY_COLOR
    :param colour_non_outlier: hex code for colour depicting the
    non-outliers. Default: PROTZILLA_PRIMARY_COLOR

    :return: returns a plotly Figure object
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
        scene={
            "xaxis": {
                "title": f"Principal Component 1 ({x_percent:.2f} %)",
                "showticklabels": False
            },
            "yaxis": {
                "title": f"Principal Component 2 ({y_percent:.2f} %)",
                "showticklabels": False
            },
            "zaxis": {
                "title": f"Principal Component 3 ({z_percent:.2f} %)",
                "showticklabels": False
            }
        }
    )
    return fig