import pandas as pd
import numpy as np
from statsmodels.stats.multitest import multipletests
from scipy import stats
import dash_bio as dashbio
from protzilla.constants.colors import PROTZILLA_DISCRETE_COLOR_SEQUENCE
from protzilla.data_analysis.differential_expression_helper import (
    apply_multiple_testing_correction,
)
import plotly.express as px
from plotly.graph_objects import Figure
from protzilla.utilities.clustergram import Clustergram


def anova(
    intensity_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    grouping: str,
    selected_groups: list,
    multiple_testing_correction_method: str,
    alpha: float,
):
    """
    A function that uses ANOVA to test the difference between two or more
    groups defined in the clinical data. The ANOVA test is conducted on
    the level of each protein. The p-values are corrected for multiple
    testing.

    :param intensity_df: the dataframe that should be tested in long
        format
    :type intensity_df: pandas DataFrame
    :param metadata_df: the dataframe that contains the clinical data
    :type metadata_df: pandas DataFrame
    :param grouping: the column name of the grouping variable in the
        metadata_df
    :type grouping: str
    :param multiple_testing_correction_method: the method for multiple
        testing correction
    :type multiple_testing_correction_method: str
    :param alpha: the alpha value for the t-test
    :type alpha: float
    :return: a dataframe with the corrected p-values and the fold change
        between the two groups and an empty dict
    :rtype: pandas DataFrame, dict
    """
    proteins = intensity_df.loc[:, "Protein ID"].unique().tolist()
    intensity_name = intensity_df.columns[3]
    intensity_df = pd.merge(
        left=intensity_df,
        right=metadata_df[["Sample", grouping]],
        on="Sample",
        copy=False,
    )
    p_values = []
    for protein in proteins:
        protein_df = intensity_df.loc[intensity_df["Protein ID"] == protein]
        all_group_intensities = []
        for group in selected_groups:
            group_intensities = protein_df.loc[
                protein_df.loc[:, grouping] == group, intensity_name
            ].to_numpy()

            all_group_intensities.append(group_intensities)
        p = stats.f_oneway(*all_group_intensities)[1]
        p_values.append(p)
    (
        corrected_p_values,
        corrected_alpha,
    ) = apply_multiple_testing_correction(
        p_values, multiple_testing_correction_method, alpha
    )

    p_values_df = pd.DataFrame(
        list(zip(proteins, corrected_p_values)),
        columns=["Protein ID", "p_value"],
    )

    tested_df = pd.merge(
        left=intensity_df,
        right=p_values_df,
        on="Protein ID",
        copy=False,
    )

    if corrected_alpha is None:
        corrected_alpha = alpha

    return tested_df, {"p_values": p_values, "corrected_alpha": corrected_alpha}


def anova_heatmap(tested_df: pd.DataFrame, grouping: str, alpha: float) -> Figure:
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


    :param tested_df: a dataframe with the corrected p-values and the fold change
        between the two groups
    :param grouping: the column name of the grouping variable in the
        metadata_df
    :param alpha: the corrected alpha value from anova

    """
    intensity_name = tested_df.columns[3]

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

    # TODO: logic for setting column_colors and column_colors_to_label_dict

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

    return clustergram
