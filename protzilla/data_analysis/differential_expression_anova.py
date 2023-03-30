import pandas as pd
import numpy as np
from statsmodels.stats.multitest import multipletests
from scipy import stats
import dash_bio as dashbio
from protzilla.constants.colors import PROTZILLA_DISCRETE_COLOR_SEQUENCE
from protzilla.data_analysis.differential_expression import _apply_multiple_testing_correction


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
    print("anova")
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
        protein_df = intensity_df.loc[
            intensity_df["Protein ID"] == protein
            ]
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
    ) = _apply_multiple_testing_correction(
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
    return tested_df, {"corrected_alpha": corrected_alpha}

