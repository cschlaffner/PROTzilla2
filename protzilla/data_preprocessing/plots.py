import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots

from protzilla.data_preprocessing.plots_helper import generate_tics, style_text, add_spacing, get_text_parameters, get_enhanced_reading_value
from protzilla.utilities import default_intensity_column
import protzilla.constants.colors as colorscheme


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
    enhanced_reading = get_enhanced_reading_value()
    add_font_size, add_letter_spacing, add_word_spacing = get_text_parameters()

    if any(i < 0 for i in values_of_sectors):
        raise ValueError

    if enhanced_reading:
        names_of_sectors = [style_text(name, add_letter_spacing, add_word_spacing) for name in names_of_sectors]

    fig = px.pie(
        names=names_of_sectors,
        values=values_of_sectors,
        color_discrete_sequence=colorscheme.PROTZILLA_DISCRETE_COLOR_SEQUENCE
    )

    fig.update_layout(
        title={
            "text": style_text(f"<b>{heading}</b>", add_letter_spacing, add_word_spacing),
            "font": dict(size=16 + add_font_size, family="Arial"),
            "y": 0.98,
            "x": 0.2,
            "xanchor": "center",
            "yanchor": "top",
        },
        font=dict(size=14 + add_font_size, family="Arial"),
        legend=dict(
            font=dict(
                size=14 + add_font_size,
                family="Arial",
            )
        )
    )
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

    :param names_of_sectors: Name of parts (so-called sectors) or categories
    :param values_of_sectors: Corresponding values for sectors
    :param heading: Header for the graph - for example the topic
    :param y_title: Optional y-axis title.
    :param x_title: Optional x-axis title.
    :return: returns a bar chart of the data
    """
    colors = colorscheme.PROTZILLA_DISCRETE_COLOR_SEQUENCE
    patterns = ['/', '\\', 'x']
    fig = Figure()

    add_font_size, add_letter_spacing, add_word_spacing = get_text_parameters()

    for i, (value, label) in enumerate(zip(values_of_sectors, names_of_sectors)):
        marker = {
            'color': colors[i % len(colors)]
        }
        if colors[1] in colorscheme.MONOCHROMATIC_DISCRETE_COLOR_SEQUENCE:
            marker['pattern'] = {'shape': patterns[i % len(patterns)]}

        legend_label = style_text(label, add_letter_spacing, add_word_spacing)

        fig.add_trace(go.Bar(
            x=[label],
            y=[value],
            marker=marker,
            name=legend_label
        ))

    fig.update_layout(
        xaxis_title=style_text(x_title, add_letter_spacing, add_word_spacing),
        yaxis_title=style_text(y_title, add_letter_spacing, add_word_spacing),
        plot_bgcolor="white",
        yaxis={"gridcolor": "lightgrey", "zerolinecolor": "lightgrey"},
    )

    fig.update_layout(
        title={
            "text": style_text(f"<b>{heading}</b>", add_letter_spacing, add_word_spacing),
            "font": dict(size=16 + add_font_size, family="Arial"),
            "y": 0.98,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        font=dict(size=14 + add_font_size, family="Arial"),
    )

    fig.update_xaxes(ticktext=[
        style_text(label, add_letter_spacing, add_word_spacing) for
        label in names_of_sectors],
        tickvals=names_of_sectors)
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
        visual_transformation: str = "linear"
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
    colors = colorscheme.PROTZILLA_DISCRETE_COLOR_SEQUENCE

    if group_by not in {"None", "Sample", "Protein ID"}:
        raise ValueError(
            f"""Group_by parameter  must be "None" or
                "Sample" or "Protein ID" but is {group_by}"""
        )
    intensity_name_a = default_intensity_column(dataframe_a)
    intensity_name_b = default_intensity_column(dataframe_b)

    add_font_size, add_letter_spacing, add_word_spacing = get_text_parameters()


    if group_by in {"Sample", "Protein ID"}:
        fig = make_subplots(rows=1, cols=2)
        trace0 = go.Box(
            y=dataframe_a[intensity_name_a],
            x=dataframe_a[group_by],
            marker_color=colors[0],
            name=style_text(name_a, add_letter_spacing, add_word_spacing),
        )
        trace1 = go.Box(
            y=dataframe_b[intensity_name_b],
            x=dataframe_b[group_by],
            marker_color=colors[1],
            name=style_text(name_b, add_letter_spacing, add_word_spacing),
        )
        fig.add_trace(trace0, 1, 1)
        fig.add_trace(trace1, 1, 2)
        fig.update_xaxes(showticklabels=False)

    elif group_by == "None":
        fig = make_subplots(rows=1, cols=2)
        trace0 = go.Box(
            y=dataframe_a[intensity_name_a],
            marker_color=colors[0],
            name=style_text(name_a, add_letter_spacing, add_word_spacing),
        )
        trace1 = go.Box(
            y=dataframe_b[intensity_name_b],
            marker_color=colors[1],
            name=style_text(name_b, add_letter_spacing, add_word_spacing),
        )
        fig.add_trace(trace0, 1, 1)
        fig.add_trace(trace1, 1, 2)

    fig.update_layout(
        xaxis_title=style_text(x_title, add_letter_spacing, add_word_spacing),
        yaxis_title=style_text(y_title, add_letter_spacing, add_word_spacing),
        xaxis2_title=style_text(x_title, add_letter_spacing, add_word_spacing),
        yaxis2_title=style_text(y_title, add_letter_spacing, add_word_spacing),
        font=dict(size=14 + add_font_size, family="Arial"),
        plot_bgcolor="white",
        yaxis1={"gridcolor": "lightgrey", "zerolinecolor": "lightgrey"},
        yaxis2={"gridcolor": "lightgrey", "zerolinecolor": "lightgrey"},
        title={
            "text": style_text(f"<b>{heading}</b>", add_letter_spacing, add_word_spacing),
            "font": dict(size=16 + add_font_size),
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
    :param y_title: Optional y-axis title for graphs.
    :param x_title: Optional x-axis title for graphs.
    :param overlay: Specifies whether to draw one Histogram with overlay or two separate histograms
    :param visual_transformation: Visual transformation of the y-axis data.
    :return: returns a plotly Figure object
    """
    colors = colorscheme.PROTZILLA_DISCRETE_COLOR_SEQUENCE

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
    binsize_a = (intensities_a.max(skipna=True) - intensities_a.min(skipna=True)) / number_of_bins
    binsize_b = (intensities_b.max(skipna=True) - intensities_b.min(skipna=True)) / number_of_bins

    if overlay:
        binsize_a = binsize_b = max(binsize_a, binsize_b)

    enhanced_reading = get_enhanced_reading_value()
    add_font_size, add_letter_spacing, add_word_spacing = get_text_parameters()

    if enhanced_reading:
        name_a = style_text(name_a, add_letter_spacing, add_word_spacing)
        name_b = style_text(name_b, add_letter_spacing, add_word_spacing)

    trace0 = go.Histogram(
        x=intensities_a,
        marker_color=colors[0],
        name=name_a,
        xbins=dict(start=min_value, end=max_value, size=binsize_a),
    )
    trace1 = go.Histogram(
        x=intensities_b,
        marker_color=colors[1],
        name=name_b,
        xbins=dict(start=min_value, end=max_value, size=binsize_b),
    )

    if not overlay:
        fig = make_subplots(rows=1, cols=2)
        fig.add_trace(trace0, 1, 1)
        fig.add_trace(trace1, 1, 2)
        fig.update_layout(
            xaxis2_title=style_text(x_title, add_letter_spacing, add_word_spacing),
            yaxis2_title=style_text(y_title, add_letter_spacing, add_word_spacing),
        )
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

    fig.update_layout(
        xaxis_title=style_text(x_title, add_letter_spacing, add_word_spacing),
        yaxis_title=style_text(y_title, add_letter_spacing, add_word_spacing),
        font=dict(size=14 + add_font_size, family="Arial"),
        plot_bgcolor="white",
        yaxis=dict(gridcolor="lightgrey", zerolinecolor="lightgrey"),
        yaxis2=dict(gridcolor="lightgrey", zerolinecolor="lightgrey"),
        title={
            "text": style_text(f"<b>{heading}</b>", add_letter_spacing, add_word_spacing),
            "font": dict(size=16 + add_font_size, family="Arial"),
            "y": 0.98,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
    )
    fig.update_yaxes(rangemode="tozero")
    return fig


def create_anomaly_score_bar_plot(
        anomaly_df: pd.DataFrame,
        colour_outlier: str = None,
        colour_non_outlier: str = None,
) -> Figure:
    """
    This function creates a graph visualising the outlier
    and non-outlier samples using the anomaly score.

    :param anomaly_df: pandas Dataframe that contains the anomaly score for each\
    sample, including outliers and on-outliers samples
    :param colour_outlier: hex code for colour depicting the outliers.
    Default: PROTZILLA_DISCRETE_COLOR_SEQUENCE outlier colour
    :param colour_non_outlier: hex code for colour depicting the
    non-outliers. Default: PROTZILLA_DISCRETE_COLOR_SEQUENCE
    non-outlier colour
    :return: returns a plotly Figure object
    """
    colors = colorscheme.PROTZILLA_DISCRETE_COLOR_SEQUENCE

    if colour_outlier is None:
        colour_outlier = colors[1]

    if colour_non_outlier is None:
        colour_non_outlier = colors[0]

    enhanced_reading = get_enhanced_reading_value()
    add_font_size, add_letter_spacing, add_word_spacing = get_text_parameters()

    outlier_label = "True"
    non_outlier_label = "False"
    if enhanced_reading:
        outlier_label = style_text(outlier_label, add_letter_spacing, add_word_spacing)
        non_outlier_label = style_text(non_outlier_label, add_letter_spacing, add_word_spacing)

    anomaly_df["Outlier Label"] = anomaly_df["Outlier"].replace({
        True: outlier_label,
        False: non_outlier_label
    })

    fig = px.bar(
        anomaly_df,
        x=anomaly_df.index,
        y="Anomaly Score",
        hover_name=anomaly_df.index,
        hover_data={
            "Anomaly Score": True,
            "Outlier Label": True,
        },
        color="Outlier Label",
        color_discrete_map={
            outlier_label: colour_outlier,
            non_outlier_label: colour_non_outlier,
        },
        labels={
            "Sample": style_text("Sample", add_letter_spacing, add_word_spacing),
            "Anomaly Score": style_text("Anomaly Score", add_letter_spacing, add_word_spacing),
            "Outlier Label": style_text("Outlier", add_letter_spacing, add_word_spacing),
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
        font=dict(size=14 + add_font_size, family="Arial"),
        plot_bgcolor="white",
        title={
            "text": style_text("Anomaly Score Bar Plot", add_letter_spacing, add_word_spacing),
            "font": dict(size=16 + add_font_size, family="Arial"),
            "y": 0.98,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }
    )

    return fig


def create_pca_2d_scatter_plot(
        pca_df: pd.DataFrame,
        explained_variance_ratio: list,
        colour_outlier: str = None,
        colour_non_outlier: str = None,
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
    Default: PROTZILLA_DISCRETE_COLOR_SEQUENCE outlier colour
    :param colour_non_outlier: hex code for colour depicting the
    non-outliers. Default: PROTZILLA_DISCRETE_COLOR_SEQUENCE
    non-outlier colour
    :param enhanced_reading: Boolean to determine if the font size and spacing should be increased.

    :return: returns a plotly Figure object
    """
    colors = colorscheme.PROTZILLA_DISCRETE_COLOR_SEQUENCE

    if colour_outlier is None:
        colour_outlier = colors[1]

    if colour_non_outlier is None:
        colour_non_outlier = colors[0]

    enhanced_reading = get_enhanced_reading_value()
    add_font_size, add_letter_spacing, add_word_spacing = get_text_parameters()

    outlier_label = "Outlier"
    non_outlier_label = "Non-Outlier"
    if enhanced_reading:
        outlier_label = style_text(outlier_label, add_letter_spacing, add_word_spacing)
        non_outlier_label = style_text(non_outlier_label, add_letter_spacing, add_word_spacing)

    pca_df["Outlier Label"] = pca_df["Outlier"].replace({
        True: outlier_label,
        False: non_outlier_label
    })

    fig = go.Figure(
        data=go.Scatter(
            x=pca_df["Component 1"],
            y=pca_df["Component 2"],
            mode="markers",
            marker=dict(color=pca_df["Outlier Label"].map({
                outlier_label: colour_outlier,
                non_outlier_label: colour_non_outlier
            })),
            text=pca_df.index.values,
            hovertemplate="%{text} <br>Outlier: %{marker.color}",
        )
    )

    e_variance_0 = round(explained_variance_ratio[0], 4) * 100
    e_variance_1 = round(explained_variance_ratio[1], 4) * 100

    fig.update_layout(
        xaxis_title=style_text(f"Principal Component 1 ({e_variance_0:.2f} %)", add_letter_spacing, add_word_spacing),
        yaxis_title=style_text(f"Principal Component 2 ({e_variance_1:.2f} %)", add_letter_spacing, add_word_spacing),
        font=dict(size=14 + add_font_size, family="Arial"),
        plot_bgcolor="white",
        yaxis={"gridcolor": "lightgrey", "zerolinecolor": "lightgrey"},
        xaxis={"gridcolor": "lightgrey", "zerolinecolor": "lightgrey"},
        legend=dict(
            title="Legend",
            itemsizing="constant",
        ),
    )

    return fig


def create_pca_3d_scatter_plot(
        pca_df: pd.DataFrame,
        explained_variance_ratio: list,
        colour_outlier: str = None,
        colour_non_outlier: str = None,
) -> Figure:
    """
    This function creates a graph visualising the outlier
    and non-outlier points by showing the principal components. It
    returns a plotly Figure object.

    :param pca_df: a DataFrame that contains the projection of\
    the intensity_df on first principal components
    :param explained_variance_ratio: a list that contains the\
    explained variation for each component
    :param colour_outlier: hex code for colour depicting the outliers.
    Default: PROTZILLA_DISCRETE_COLOR_SEQUENCE outlier colour
    :param colour_non_outlier: hex code for colour depicting the
    non-outliers. Default: PROTZILLA_DISCRETE_COLOR_SEQUENCE
    non-outlier colour
    :param enhanced_reading: Boolean to determine if the font size and spacing should be increased.
    :return: returns a plotly Figure object
    """
    colors = colorscheme.PROTZILLA_DISCRETE_COLOR_SEQUENCE

    if colour_outlier is None:
        colour_outlier = colors[1]

    if colour_non_outlier is None:
        colour_non_outlier = colors[0]

    enhanced_reading = get_enhanced_reading_value()
    add_font_size, add_letter_spacing, add_word_spacing = get_text_parameters()

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

    xaxis_title = f"Principal Component 1 ({x_percent:.2f} %)"
    yaxis_title = f"Principal Component 2 ({y_percent:.2f} %)"
    zaxis_title = f"Principal Component 3 ({z_percent:.2f} %)"

    if enhanced_reading:
        xaxis_title = add_spacing(xaxis_title, add_letter_spacing, add_word_spacing)
        yaxis_title = add_spacing(yaxis_title, add_letter_spacing, add_word_spacing)
        zaxis_title = add_spacing(zaxis_title, add_letter_spacing, add_word_spacing)

    fig.update_layout(
        scene=dict(
            xaxis=dict(title=dict(text=xaxis_title, font=dict(size=14 + add_font_size))),
            yaxis=dict(title=dict(text=yaxis_title, font=dict(size=14 + add_font_size))),
            zaxis=dict(title=dict(text=zaxis_title, font=dict(size=14 + add_font_size))),
            xaxis_showticklabels=False,
            yaxis_showticklabels=False,
            zaxis_showticklabels=False,
        ),
        font=dict(size=14 + add_font_size, family="Arial"),
        plot_bgcolor="white",
    )

    return fig
# todo: this plot doesnt work with bigger spacing because the axes are not fully readable
