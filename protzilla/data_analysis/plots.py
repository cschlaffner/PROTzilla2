import dash_bio as dashbio
import pandas as pd
from scipy import stats
import numpy as np
import plotly.express as px
from plotly.graph_objects import Figure
from protzilla.utilities.clustergram import Clustergram
from django.contrib import messages

from protzilla.utilities.transform_dfs import is_long_format, long_to_wide


def scatter_plot(
    input_df: pd.DataFrame,
    color_df: pd.DataFrame | None = None,
):
    """
    Function to create a scatter plot from data. 
    
    :param input_df: the dataframe that should be plotted. It should have either 2 \
    or 3 dimension
    :type input_df: pd.Dataframe
    :param color_df: the Dataframe with one column according to which the marks should \
    be colored. This is an optional parameter
    :type color_df: pd.Dataframe
    """
    intensity_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    try:
        color_df = (
            pd.DataFrame() if not isinstance(color_df, pd.DataFrame) else color_df
        )

        if color_df.shape[1] > 1:
            raise ValueError("The color dataframe should have 1 dimension only")

        if intensity_df_wide.shape[1] == 2:
            intensity_df_wide = pd.concat([intensity_df_wide, color_df], axis=1)
            x_name, y_name = intensity_df_wide.columns[:2]
            color_name = color_df.columns[0] if not color_df.empty else None
            fig = px.scatter(intensity_df_wide, x=x_name, y=y_name, color=color_name)
        elif intensity_df_wide.shape[1] == 3:
            intensity_df_wide = pd.concat([intensity_df_wide, color_df], axis=1)
            x_name, y_name, z_name = intensity_df_wide.columns[:3]
            color_name = color_df.columns[0] if not color_df.empty else None
            fig = px.scatter_3d(
                intensity_df_wide, x=x_name, y=y_name, z=z_name, color=color_name
            )
        else:
            raise ValueError(
                "The dimensions of the DataFrame are either too high or too low."
            )

        return [fig]
    except ValueError as e:
        msg = ""
        if intensity_df_wide.shape[1] < 2:
            msg = (
                f"The input dataframe has {intensity_df_wide.shape[1]} feature. "
                f"Consider using another plot to visualize your data"
            )
        elif intensity_df_wide.shape[1] > 3:
            msg = (
                f"The input dataframe has {intensity_df_wide.shape[1]} features. "
                f"Consider reducing the dimensionality of your data"
            )
        elif color_df.shape[1] != 1:
            msg = "The color dataframe should have 1 dimension only"
        return [dict(messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))])]


def create_volcano_plot(p_values, log2_fc, fc_threshold, alpha):
    plot_df = p_values.join(log2_fc.set_index("Protein ID"), on="Protein ID")
    fig = dashbio.VolcanoPlot(
        dataframe=plot_df,
        effect_size="log2_fold_change",
        p="corrected_p_value",
        snp=None,
        gene=None,
        genomewideline_value=alpha,
        effect_size_line=[-fc_threshold, fc_threshold],
        xlabel="log2(fc)",
        ylabel="-log10(p)",
        title="Volcano Plot",
        annotation="Protein ID",
    )
    return [fig]


def heatmap(tested_df, grouping: str, alpha, corrected_alpha):
    """
    A function to create a heatmap with an integrated dendrogram
    (clustergram) from the ANOVA Test results. The clustergram shows in a
    matrix form the intensities for a protein and a sample. Only the values
    for the proteins with a significance level less than the corrected
    alpha value are shown. The samples and proteins are ordered according
    to the clustering resulting from the dendrogram. Regarding the
    customisation of the graph, it is possible to invert the axes and
    also colorbar representing the different groups present in the data
    can be added.

    :param grouping: the column name of the grouping variable in the
        metadata_df
    :type grouping: str
    """
    intensity_name = tested_df.columns[3]

    if corrected_alpha is None:
        alpha = alpha
    else:
        alpha = corrected_alpha

    df_filtered = tested_df.loc[tested_df["p_value"] < alpha]

    matrix = df_filtered.pivot(
        index="Sample", columns="Protein ID", values=intensity_name
    )

    sample_group_df = df_filtered[["Sample", grouping]].drop_duplicates()
    sample_group_dict = dict(
        zip(
            sample_group_df["Sample"].tolist(),
            sample_group_df[grouping].tolist(),
        )
    )

    n_groups = len(set(sample_group_dict.values()))

    group_colors = px.colors.sample_colorscale(
        "Turbo",
        0.5 / n_groups + np.linspace(0, 1, n_groups, endpoint=False),
    )
    group_color_dict = dict(
        zip(df_filtered[grouping].drop_duplicates().tolist(), group_colors)
    )
    color_label_dict = {v: k for k, v in group_color_dict.items()}
    groups = [sample_group_dict[label] for label in matrix.index.values]
    row_colors = [group_color_dict[g] for g in groups]

    # TODO: logic for seting column_colors and column_colors_to_label_dict

    clustergram = Clustergram(
        flip_axes=False,
        data=matrix.values,
        row_labels=matrix.index.values.tolist(),
        row_colors=row_colors,
        row_colors_to_label_dict=color_label_dict,
        column_labels=matrix.columns.values.tolist(),
        color_threshold={"row": 250, "col": 700},
        line_width=2,
        color_map=px.colors.diverging.RdBu,
        hidden_labels=["row", "col"],
    )

    clustergram.update_layout(
        autosize=True,
    )

    return [clustergram]
