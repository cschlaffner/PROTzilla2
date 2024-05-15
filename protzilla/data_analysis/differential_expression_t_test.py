import logging

import numpy as np
import pandas as pd
from scipy import stats

from protzilla.utilities import default_intensity_column, exists_message

from .differential_expression_helper import (
    INVALID_PROTEINGROUP_DATA_MSG,
    _map_log_base,
    apply_multiple_testing_correction,
)


def _is_valid(value):
    return value != 0 and not np.isnan(value)


def t_test(
    intensity_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    ttest_type: str,
    grouping: str,
    group1: str,
    group2: str,
    multiple_testing_correction_method: str,
    alpha: float,
    log_base: str = None,
    intensity_name: str = None,
) -> dict:
    """
    A function to conduct a two sample t-test between groups defined in the
    clinical data. The t-test is conducted on the level of each protein.
    The p-values are corrected for multiple testing.
    :param ttest_type: the type of t-test to be used. Either "Student's t-Test" or "Welch's t-Test"
    :param intensity_df: the dataframe that should be tested in long format
    :param metadata_df: the dataframe that contains the clinical data
    :param grouping: the column name of the grouping variable in the metadata_df
    :param group1: the name of the first group for the t-test
    :param group2: the name of the second group for the t-test
    :param multiple_testing_correction_method: the method for multiple testing correction
    :param alpha: the p-value cut-off before multiple testing correction
    :param log_base: in case the data was previously log transformed this parameter contains the base as a string
    :param intensity_name: name of the column containing the protein group intensities

    :return: a dict containing
        - a df differentially_expressed_proteins_df in typical protzilla long format containing the t-test results
        - a df significant_proteins_df, containing the proteins that are significant after multiple testing correction
        - a df corrected_p_values, containing the p_values after application of multiple testing correction,
        - a df log2_fold_change, containing the log2 fold changes per protein,
        - a df t_statistic_df, containing the t-statistic per protein,
        - a float corrected_alpha, containing the alpha value after application of multiple testing correction (depending on the selected multiple testing correction method corrected_alpha may be equal to alpha),
        - a list messages, containing messages for the user
    """

    assert grouping in metadata_df.columns
    messages = []
    # User input handling
    unique_groups = metadata_df[grouping].unique()
    # Check if group1 is in unique_groups, if not assign the first unique group
    if group1 not in unique_groups:
        group1 = unique_groups[0]
        messages.append(
            {
                "level": logging.WARNING,
                "msg": f"Group 1 was invalid. Auto-selected {group1} as group1.",
            }
        )

    # Check if group2 is in unique_groups and not the same as group1, if not assign the next unique group
    if group2 not in unique_groups or group1 == group2:
        for group in unique_groups:
            if group != group1:
                group2 = group
                break
        messages.append(
            {
                "level": logging.WARNING,
                "msg": f"Group 2 was invalid. Auto-selected {group2} as group 2.",
            }
        )

    intensity_df = pd.merge(
        left=intensity_df,
        right=metadata_df[["Sample", grouping]],
        on="Sample",
        copy=False,
    )

    intensity_name = default_intensity_column(intensity_df, intensity_name)

    log_base = _map_log_base(log_base)  # now log_base in [2, 10, None]

    proteins = intensity_df["Protein ID"].unique()
    p_values = []
    valid_protein_groups = []
    log2_fold_changes = []
    t_statistic = []
    for protein in proteins:
        protein_df = intensity_df[intensity_df["Protein ID"] == protein]
        group1_intensities = protein_df[protein_df[grouping] == group1][intensity_name]
        group2_intensities = protein_df[protein_df[grouping] == group2][intensity_name]
        t, p = stats.ttest_ind(
            group1_intensities,
            group2_intensities,
            equal_var=not (ttest_type == "Student's t-Test"),
        )

        if not np.isnan(p):
            log2_fold_change = (
                np.log2(
                    np.power(log_base, group2_intensities).mean()
                    / np.power(log_base, group1_intensities).mean()
                )
                if log_base
                else np.log2(group2_intensities.mean() / group1_intensities.mean())
            )

            valid_protein_groups.append(protein)
            p_values.append(p)
            t_statistic.append(t)
            log2_fold_changes.append(log2_fold_change)
        elif not exists_message(messages, INVALID_PROTEINGROUP_DATA_MSG):
            messages.append(INVALID_PROTEINGROUP_DATA_MSG)
        else:
            # if the protein has a NaN value in a sample, we just skip it
            pass

    (corrected_p_values, corrected_alpha) = apply_multiple_testing_correction(
        p_values=p_values,
        method=multiple_testing_correction_method,
        alpha=alpha,
    )

    corrected_p_values_df = pd.DataFrame(
        list(zip(valid_protein_groups, corrected_p_values)),
        columns=["Protein ID", "corrected_p_value"],
    )
    log2_fold_change_df = pd.DataFrame(
        list(zip(valid_protein_groups, log2_fold_changes)),
        columns=["Protein ID", "log2_fold_change"],
    )
    t_statistic_df = pd.DataFrame(
        list(zip(valid_protein_groups, t_statistic)),
        columns=["Protein ID", "t_statistic"],
    )

    dataframes = [
        corrected_p_values_df,
        log2_fold_change_df,
        t_statistic_df,
    ]

    for df in dataframes:
        intensity_df = pd.merge(intensity_df, df, on="Protein ID", how="left")

    differentially_expressed_proteins = [
        protein for protein, p in zip(valid_protein_groups, corrected_p_values)
    ]

    differentially_expressed_proteins_df = intensity_df.loc[
        intensity_df["Protein ID"].isin(differentially_expressed_proteins)
    ]

    significant_proteins_df = differentially_expressed_proteins_df[
        differentially_expressed_proteins_df["corrected_p_value"] <= corrected_alpha
    ]

    # filtered_proteins = list(set(proteins) - set(valid_protein_groups))

    return dict(
        differentially_expressed_proteins_df=differentially_expressed_proteins_df,
        significant_proteins_df=significant_proteins_df,
        corrected_p_values_df=corrected_p_values_df,
        t_statistic_df=t_statistic_df,
        log2_fold_change_df=log2_fold_change_df,
        corrected_alpha=corrected_alpha,
        # filtered_proteins=filtered_proteins,
        messages=messages,
        group1=group1,
        group2=group2,
    )
