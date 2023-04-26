import logging

import pandas as pd
from scipy import stats

from .differential_expression_helper import apply_multiple_testing_correction


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
    :param selected_groups: groups to test against each other
    :type selected_groups: list, if None or empty: first two groups will be selected
    :param multiple_testing_correction_method: the method for multiple
        testing correction
    :type multiple_testing_correction_method: str
    :param alpha: the alpha value for anova
    :type alpha: float
    :return: a dataframe with the intensity_df and the corrected p-values
        and a dict containing corrected_p_values and corrected_alphas
    :rtype: pandas DataFrame, dict

    :return: a dataframe in typical protzilla long format
    with the differentially expressed proteins and a dict, containing
    the corrected p-values and the log2 fold change, the alpha used
    and the corrected alpha, as well as filtered out proteins.
    """
    assert grouping in metadata_df.columns

    if selected_groups is None or selected_groups == []:
        selected_groups = metadata_df["Group"].unique()[:2]
        logging.warning("auto-selected first two groups in anova")

    proteins = intensity_df.loc[:, "Protein ID"].unique().tolist()
    intensity_name = intensity_df.columns[3]
    print(metadata_df)
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

    return {
        "p_values_df": tested_df,
        "corrected_p_values": corrected_p_values,
        "corrected_alpha": corrected_alpha,
    }
