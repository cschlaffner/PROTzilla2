import logging

import numpy as np
import pandas as pd
from scipy import stats

from protzilla.utilities import default_intensity_column

from .differential_expression_helper import apply_multiple_testing_correction


def _is_valid(value):
    return value != 0 and not np.isnan(value)


def t_test(
    intensity_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    grouping: str,
    group1: str,
    group2: str,
    multiple_testing_correction_method: str,
    alpha: float,
    fc_threshold: float,
    log_base: int = None,
    intensity_name: str = None,
) -> dict:
    """
    A function to conduct a two sample t-test between groups defined in the
    clinical data. The t-test is conducted on the level of each protein.
    The p-values are corrected for multiple testing.

    :param intensity_df: the dataframe that should be tested in long
        format
    :param metadata_df: the dataframe that contains the clinical data
    :param grouping: the column name of the grouping variable in the
        metadata_df
    :param group1: the name of the first group for the t-test
    :param group2: the name of the second group for the t-test
    :param multiple_testing_correction_method: the method for multiple
        testing correction
    :param alpha: the alpha value for the t-test
    :param fc_threshold: threshold for the abs(log_2(fold_change)) (vertical line in a volcano plot).
        Only proteins with a larger abs(log_2(fold_change)) than the fc_threshold are seen as differentially expressed
    :param log_base: in case the data was previously log transformed this parameter contains the base (e.g. 2 if the data was log_2 transformed).
    :param intensity_name: name of the column containing the protein group intensities

    :return: a dict containing
        a df corrected_p_values, containing the p_values after application of multiple testing correction,
        a df log2_fold_change, containing the log2 fold changes per protein,
        a float fc_threshold, containing the absolute threshold for the log fold change, above which a protein is considered differentially expressed,
        a float corrected_alpha, containing the alpha value after application of multiple testing correction (depending on the selected multiple testing correction method corrected_alpha may be equal to alpha),
        a df filtered_proteins, containing the filtered out proteins (proteins where the mean of a group was 0),
        a df fold_change_df, containing the fold_changes per protein,
        a df t_statistic_df, containing the t-statistic per protein,
        a df differentially_expressed_proteins_df in typical protzilla long format containing the differentially expressed proteins;
            corrected_p_value, log2_fold_change, fold_change and t_statistic per protein,
        a df significant_proteins_df, containing the proteins where the p-values are smaller than alpha (if fc_threshold = 0, the significant proteins equal the differentially expressed ones)
            corrected_p_value, log2_fold_change, fold_change and t_statistic per protein,
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
                "level": logging.INFO,
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
                "level": logging.INFO,
                "msg": f"Group 2 was invalid. Auto-selected {group2} as group 2.",
            }
        )
    # somehow the frontend sucks at returning None instead of empty string
    if log_base == "":
        log_base = None

    intensity_df = pd.merge(
        left=intensity_df,
        right=metadata_df[["Sample", grouping]],
        on="Sample",
        copy=False,
    )
    proteins = intensity_df["Protein ID"].unique()
    p_values = []
    valid_protein_groups = []
    fold_changes = []
    log2_fold_changes = []
    t_statistic = []
    intensity_name = default_intensity_column(intensity_df, intensity_name)
    for protein in proteins:
        protein_df = intensity_df[intensity_df["Protein ID"] == protein]
        group1_intensities = protein_df[protein_df[grouping] == group1][
            intensity_name
        ].to_numpy()
        group2_intensities = protein_df[protein_df[grouping] == group2][
            intensity_name
        ].to_numpy()
        t, p = stats.ttest_ind(group1_intensities, group2_intensities)

        if not np.isnan(p):
            fold_change = (
                np.mean(group2_intensities) / np.mean(group1_intensities)
                if log_base is None
                else log_base
                ** (np.mean(group2_intensities) - np.mean(group1_intensities))
            )
            log2_fold_change = np.log2(fold_change)

            valid_protein_groups.append(protein)
            p_values.append(p)
            t_statistic.append(t)
            fold_changes.append(fold_change)
            log2_fold_changes.append(log2_fold_change)
        elif not any(message["level"] == logging.WARNING for message in messages):
            messages.append(
                {
                    "level": logging.WARNING,
                    "msg": "Due do missing or identical values, the p-values for some protein groups could not be calculated. These groups were omitted from the analysis. "
                    "To prevent this, please add filtering and imputation steps to your workflow before running the analysis.",
                }
            )
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
    fold_change_df = pd.DataFrame(
        list(zip(valid_protein_groups, fold_changes)),
        columns=["Protein ID", "fold_change"],
    )
    t_statistic_df = pd.DataFrame(
        list(zip(valid_protein_groups, t_statistic)),
        columns=["Protein ID", "t_statistic"],
    )

    dataframes = [
        corrected_p_values_df,
        log2_fold_change_df,
        fold_change_df,
        t_statistic_df,
    ]

    for df in dataframes:
        intensity_df = pd.merge(intensity_df, df, on="Protein ID", how="left")

    differentially_expressed_proteins = [
        protein
        for protein, p, fc in zip(
            valid_protein_groups, corrected_p_values, log2_fold_changes
        )
        if p < corrected_alpha and abs(fc) > fc_threshold
    ]
    differentially_expressed_proteins_df = intensity_df.loc[
        intensity_df["Protein ID"].isin(differentially_expressed_proteins)
    ]
    significant_proteins = [
        protein for i, protein in enumerate(valid_protein_groups) if p_values[i] < alpha
    ]
    significant_proteins_df = intensity_df.loc[
        intensity_df["Protein ID"].isin(significant_proteins)
    ]
    filtered_proteins = list(set(proteins) - set(valid_protein_groups))

    return dict(
        differentially_expressed_proteins_df=differentially_expressed_proteins_df,
        corrected_p_values_df=corrected_p_values_df,
        log2_fold_change_df=log2_fold_change_df,
        fc_threshold=fc_threshold,
        corrected_alpha=corrected_alpha,
        filtered_proteins=filtered_proteins,
        fold_change_df=fold_change_df,
        t_statistic_df=t_statistic_df,
        significant_proteins_df=significant_proteins_df,
        messages=messages,
    )
