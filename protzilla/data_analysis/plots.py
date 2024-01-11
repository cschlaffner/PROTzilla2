import logging

import dash_bio as dashbio
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.contrib import messages
from scipy import stats
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

from protzilla.constants.colors import PROTZILLA_DISCRETE_COLOR_SEQUENCE
from protzilla.utilities.clustergram import Clustergram
from protzilla.utilities.transform_dfs import is_long_format, long_to_wide


def scatter_plot(
    input_df: pd.DataFrame,
    color_df: pd.DataFrame | None = None,
):
    """
    Function to create a scatter plot from data.

    :param input_df: the dataframe that should be plotted. It should have either 2
        or 3 dimensions
    :type input_df: pd.Dataframe
    :param color_df: the Dataframe with one column according to which the marks should
        be colored. This is an optional parameter
    :type color_df: pd.Dataframe

    :return: returns a list with a plotly figure or a list with a dictionary if an error occurs
    :rtype: list[plotly figure]/dict
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
        fig.update_layout(plot_bgcolor="white")
        fig.update_xaxes(gridcolor="lightgrey", linecolor="lightgrey")
        fig.update_yaxes(gridcolor="lightgrey", linecolor="lightgrey")
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
        return [dict(messages=[dict(level=logging.ERROR, msg=msg, trace=str(e))])]


def create_volcano_plot(
    p_values, log2_fc, fc_threshold, alpha, proteins_of_interest=None
):
    """
    Function to create a volcano plot from p values and log2 fold change with the
    possibility to annotate proteins of interest.

    :param p_values:dataframe with p values
    :type p_values: pd.Dataframe
    :param log2_fc: dataframe with log2 fold change
    :type log2_fc: pd.Dataframe
    :param fc_threshold: the threshold for the fold change to show
    :type fc_threshold: float
    :param alpha: the alpha value for the significance line
    :type alpha: float
    :param proteins_of_interest: the proteins that should be annotated in the plot
    :type proteins_of_interest: list or None

    :return: returns a list with a plotly figure
    :rtype: [plotly figure]
    """

    colors = {
        "plot_bgcolor": "#ffffff",
        "gridcolor": "#F1F1F1",
        "annotation_text_color": "#ffffff",
        "annotation_proteins_of_interest": "#4A536A",
    }

    plot_df = p_values.join(log2_fc.set_index("Protein ID"), on="Protein ID")
    fig = dashbio.VolcanoPlot(
        dataframe=plot_df,
        effect_size="log2_fold_change",
        p="corrected_p_value",
        snp=None,
        gene=None,
        genomewideline_value=-np.log10(alpha),
        effect_size_line=[-fc_threshold, fc_threshold],
        xlabel="log2(fc)",
        ylabel="-log10(p)",
        title="Volcano Plot",
        annotation="Protein ID",
        plot_bgcolor=colors["plot_bgcolor"],
        xaxis_gridcolor=colors["gridcolor"],
        yaxis_gridcolor=colors["gridcolor"],
    )
    if proteins_of_interest is None:
        proteins_of_interest = []
    elif not isinstance(proteins_of_interest, list):
        proteins_of_interest = [proteins_of_interest]

    # annotate the proteins of interest permanently in the plot
    for protein in proteins_of_interest:
        fig.add_annotation(
            x=plot_df.loc[
                plot_df["Protein ID"] == protein,
                "log2_fold_change",
            ].values[0],
            y=-np.log10(
                plot_df.loc[
                    plot_df["Protein ID"] == protein,
                    "corrected_p_value",
                ].values[0]
            ),
            text=protein,
            showarrow=True,
            arrowhead=1,
            font=dict(color=colors["annotation_text_color"]),
            align="center",
            arrowcolor=colors["annotation_proteins_of_interest"],
            bgcolor=colors["annotation_proteins_of_interest"],
            opacity=0.8,
            ax=0,
            ay=-20,
        )

    new_names = {
        "Point(s) of interest": "Significant Proteins",
        "Dataset": "Not Significant Proteins",
    }

    fig.for_each_trace(
        lambda t: t.update(
            name=new_names[t.name],
            legendgroup=new_names[t.name],
        )
    )

    return [fig]


def clustergram_plot(
    input_df: pd.DataFrame, sample_group_df: pd.DataFrame | None, flip_axes: str
):
    """
    Creates a clustergram plot from a dataframe in protzilla wide format. The rows or
    columns of the clustergram are ordered according to the clustering resulting from
    the dendrogram. Optionally, a colorbar representing the different groups present
    in the data can be added and the axes of the heatmap can be inverted

    :param input_df: A dataframe in protzilla wide format, where each row
        represents a sample and each column represents a feature.
    :type input_df: pd.DataFrame
    :param sample_group_df: A dataframe with a column that specifies the group of each
        sample in `input_df`. Each group will be assigned a color, which will be shown
        in the final plot as a colorbar next to the heatmap. This is an optional
        parameter
    :type sample_group_df: pd.DataFrame
    :param flip_axes: If "yes", the rows and columns of the clustergram will be
        swapped. If "no", the default orientation is used.
    :type flip_axes: str

    :return: returns a list with a plotly figure or a list with a dictionary if an error occurs
    :rtype: list[plotly figure]/dict
    """
    try:
        assert isinstance(input_df, pd.DataFrame) and not input_df.empty
        assert isinstance(sample_group_df, pd.DataFrame) or not sample_group_df

        input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df

        if isinstance(sample_group_df, pd.DataFrame):
            assert len(input_df_wide.index.values.tolist()) == len(
                sample_group_df.index.values.tolist()
            )
            assert sorted(input_df_wide.index.values.tolist()) == sorted(
                sample_group_df.index.values.tolist()
            )
            # In the clustergram each row represents a sample that can pertain to a
            # group. In the following code the necessary data structures are created
            # to assign each group to a unique color.
            sample_group_dict = dict(
                zip(sample_group_df.index, sample_group_df[sample_group_df.columns[0]])
            )
            n_groups = len(set(sample_group_dict.values()))
            group_colors = px.colors.sample_colorscale(
                "Turbo",
                0.5 / n_groups + np.linspace(0, 1, n_groups, endpoint=False),
            )
            group_to_color_dict = dict(
                zip(
                    sample_group_df[sample_group_df.columns[0]].drop_duplicates(),
                    group_colors,
                )
            )
            # dictionary that maps each color to a group for the colorbar (legend)
            color_label_dict = {v: k for k, v in group_to_color_dict.items()}
            groups = [sample_group_dict[label] for label in input_df_wide.index.values]
            # maps each row (sample) to the corresponding color
            row_colors = [group_to_color_dict[g] for g in groups]
        else:
            row_colors = None
            color_label_dict = None

        clustergram = Clustergram(
            flip_axes=False if flip_axes == "no" else True,
            data=input_df_wide.values,
            row_labels=input_df_wide.index.values.tolist(),
            row_colors=row_colors,
            row_colors_to_label_dict=color_label_dict,
            column_labels=input_df_wide.columns.values.tolist(),
            color_threshold={"row": 250, "col": 700},
            line_width=2,
            color_map=px.colors.diverging.RdBu,
            hidden_labels=["row", "col"],
        )

        clustergram.update_layout(
            autosize=True,
        )
        return [clustergram]
    except AssertionError as e:
        if not isinstance(input_df, pd.DataFrame):
            msg = (
                'The selected input for "input dataframe" is not a dataframe, '
                'dataframes have the suffix "df"'
            )
        elif not isinstance(sample_group_df, pd.DataFrame):
            msg = (
                'The selected input for "grouping dataframe" is not a dataframe, '
                'dataframes have the suffix "df"'
            )
        elif isinstance(sample_group_df, pd.DataFrame) and len(
            input_df_wide.index.values.tolist()
        ) != len(sample_group_df.index.values.tolist()):
            msg = (
                "There is a dimension mismatch between the input dataframe and the "
                "grouping dataframe, both should have the same number of samples (rows)"
            )
        elif isinstance(sample_group_df, pd.DataFrame) and sorted(
            input_df_wide.index.values.tolist()
        ) != sorted(sample_group_df.index.values.tolist()):
            msg = "The input dataframe and the grouping contain different samples"
        else:
            msg = f"An unknown error occurred: {e}"
        return [dict(messages=[dict(level=logging.ERROR, msg=msg)])]


def prot_quant_plot(
    input_df: pd.DataFrame,
    protein_group: str,
    similarity: float = 1.0,
    similarity_measure: str = "euclidean distance",
):
    """
    A function to create a graph visualising protein quantifications across all samples
    as a line diagram. It's possible to select one proteingroup that will be displayed in orange
    and choose a similarity measurement with a similarity score to get all proteingroups
    that are similar displayed in another color in this line diagram. All other proteingroups
    are displayed in the background as a grey polygon.

    :param input_df: A dataframe in protzilla wide format, where each row
        represents a sample and each column represents a feature.
    :param protein_group: Protein IDs as the columnheader of the dataframe
    :param similarity_measure: method to compare the chosen proteingroup with all others. The two
        methods are "cosine similarity" and "euclidean distance".
    :param similarity: similarity score of the chosen similarity measurement method.
    """
    wide_df = long_to_wide(input_df) if is_long_format(input_df) else input_df

    try:
        if protein_group not in wide_df.columns:
            raise ValueError("Please select a valid protein group.")
        elif similarity_measure == "euclidean distance" and similarity < 0:
            raise ValueError(
                "Similarity for euclidean distance should be greater than or equal to 0."
            )
        elif similarity_measure == "cosine similarity" and (
            similarity < -1 or similarity > 1
        ):
            raise ValueError(
                "Similarity for cosine similarity should be between -1 and 1."
            )
    except ValueError as error:
        return [dict(messages=[dict(level=messages.ERROR, msg=str(error))])]

    fig = go.Figure()

    color_mapping = {
        "A": PROTZILLA_DISCRETE_COLOR_SEQUENCE[0],
        "C": PROTZILLA_DISCRETE_COLOR_SEQUENCE[1],
    }

    lower_upper_x = []
    lower_upper_y = []

    lower_upper_x.append(wide_df.index[0])
    lower_upper_y.append(wide_df.iloc[0].min())

    for index, row in wide_df.iterrows():
        lower_upper_x.append(index)
        lower_upper_y.append(row.max())

    for index, row in reversed(list(wide_df.iterrows())):
        lower_upper_x.append(index)
        lower_upper_y.append(row.min())

    fig.add_trace(
        go.Scatter(
            x=lower_upper_x,
            y=lower_upper_y,
            fill="toself",
            name="Intensity Range",
            line=dict(color="silver"),
        )
    )

    similar_groups = []
    for group_to_compare in wide_df.columns:
        if group_to_compare != protein_group:
            if similarity_measure == "euclidean distance":
                distance = euclidean_distances(
                    stats.zscore(wide_df[protein_group]).values.reshape(1, -1),
                    stats.zscore(wide_df[group_to_compare]).values.reshape(1, -1),
                )[0][0]
            else:
                distance = cosine_similarity(
                    stats.zscore(wide_df[protein_group]).values.reshape(1, -1),
                    stats.zscore(wide_df[group_to_compare]).values.reshape(1, -1),
                )[0][0]
            if similarity_measure == "euclidean distance":
                if distance <= similarity:
                    similar_groups.append(group_to_compare)
            else:
                if distance >= similarity:
                    similar_groups.append(group_to_compare)

    for group in similar_groups:
        fig.add_trace(
            go.Scatter(
                x=wide_df.index,
                y=wide_df[group],
                mode="lines",
                name=group[:15] + "..." if len(group) > 15 else group,
                line=dict(color="rgba(102,51,153,0.5)"),
                showlegend=len(similar_groups) <= 7,
            )
        )

    if len(similar_groups) > 7:
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                marker=dict(color="rgba(102,51,153,0.5)"),
                name="Similar Protein Groups",
            )
        )

    formatted_protein_name = (
        protein_group[:15] + "..." if len(protein_group) > 15 else protein_group
    )
    fig.add_trace(
        go.Scatter(
            x=wide_df.index,
            y=wide_df[protein_group],
            mode="lines",
            name=formatted_protein_name,
            line=dict(color="orangered"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color=color_mapping.get("A")),
            name="Experimental Group",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color=color_mapping.get("C")),
            name="Control Group",
        )
    )

    fig.update_layout(
        title=f"Intensity of {formatted_protein_name} in all samples",
        xaxis_title="Sample",
        yaxis_title="Intensity",
        legend_title="Legend",
        xaxis=dict(
            tickmode="array",
            tickangle=0,
            tickvals=wide_df.index,
            ticktext=[
                f"<span style='font-size: 10px; color:{color_mapping.get(label[0], 'black')}'><b>•</b></span>"
                for label in wide_df.index
            ],
        ),
        autosize=True,
        margin=dict(l=100, r=300, t=100, b=100),
        legend=dict(
            x=1.05,
            y=1,
            bgcolor="rgba(255, 255, 255, 0.5)",
            orientation="v",
        ),
    )

    return [fig]
