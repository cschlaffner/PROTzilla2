import logging
import math

import numpy as np
import pandas as pd

from statsmodels.stats.multitest import multipletests


def apply_multiple_testing_correction(
        p_values: list, method: str, alpha: float
) -> tuple:
    """
    Applies a multiple testing correction method to a list of p-values
    using a given alpha.
    :param p_values: list of p-values to be corrected
    :param method: the multiple testing correction method to be used.\
        Can be either "Bonferroni" or "Benjamini-Hochberg"
    :param alpha: the alpha value to be used for the correction
    :return: a tuple containing the corrected p-values and (depending on the correction method)\
          either the input alpha value or the corrected alpha value
    """
    assert method in [
        "Bonferroni",
        "Benjamini-Hochberg",
    ], "Invalid multiple testing correction method"
    assert all(
        isinstance(i, (int, float)) and not math.isnan(i) and i is not None
        for i in p_values
    ), "List contains non-number or NaN values"
    assert 0 <= alpha <= 1, "Alpha value must be between 0 and 1"

    to_param = {"Bonferroni": "bonferroni", "Benjamini-Hochberg": "fdr_bh"}
    correction = multipletests(pvals=p_values, alpha=alpha, method=to_param[method])
    assert all(
        isinstance(i, (int, float)) and not math.isnan(i) and i is not None
        for i in correction[1]
    ), "Corrected p-Values contain non-number or NaN values, indicating an unfiltered\
     dataset / incorrect imputation"
    # for Bonferroni: alpha values are changed, p-values stay the same
    # for Benjamin-Hochberg: alpha values stay the same, p-values are changed
    if method == "Bonferroni":
        return p_values, correction[3]
    return correction[1], alpha


def _map_log_base(log_base: str) -> int | None:
    log_base_mapping = {"log2": 2, "log10": 10, "None": None}
    return log_base_mapping.get(log_base, None)


def preprocess_grouping(
        metadata_df: pd.DataFrame, grouping: str, selected_groups: list | str
) -> tuple[list, list[dict]]:
    """
    Preprocesses the grouping column in the metadata_df and checks if the selected groups are present.
    :param metadata_df: the metadata dataframe
    :param grouping: the column name in the metadata_df that contains the grouping information
    :param selected_groups: the groups that should be compared
    :return: a tuple containing the selected groups and a list of messages
    """
    assert grouping in metadata_df.columns, f"{grouping} not found in metadata_df"
    messages = []

    # Check if the selected groups are present in the metadata_df
    removed_groups = []
    for group in selected_groups:
        if group not in metadata_df[grouping].unique():
            selected_groups.remove(group)
            removed_groups.append(group)
    if removed_groups:
        messages.append(
            {
                "level": logging.WARNING,
                "msg": f"Group{'s' if len(removed_groups) > 1 else ''} "
                       f"{str(removed_groups)[1:-1]} were not found in metadata_df and thus removed.",
            }
        )

    # Select all groups if none or less than two were selected
    if not selected_groups or isinstance(selected_groups, str) or len(selected_groups) < 2:
        selected_groups = metadata_df[grouping].unique()
        selected_groups_str = "".join(["\'" + str(group) + "\', " for group in selected_groups])[0:-2]
        messages.append(
            {
                "level": logging.WARNING,
                "msg": f"Auto-selected the groups {selected_groups_str} for comparison, "
                       f"because none or only one {'valid ' if removed_groups else ''}group was selected.",
            }
        )

    return selected_groups, messages


def calculate_log2_fold_change(
        group1_data: pd.Series, group2_data: pd.Series, log_base: int
) -> float:
    return (
        np.log2(
            np.power(log_base, group2_data).mean()
            / np.power(log_base, group1_data).mean()
        )
        if log_base
        else np.log2(group2_data.mean() / group1_data.mean())
    )


def merge_differential_expression_and_significant_df(
        intensity_df: pd.DataFrame, diff_exp_df: pd.DataFrame, sig_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    differentially_expressed_proteins_df = pd.merge(intensity_df, diff_exp_df, on="Protein ID", how="left")
    differentially_expressed_proteins_df = differentially_expressed_proteins_df.loc[
        differentially_expressed_proteins_df["Protein ID"].isin(diff_exp_df["Protein ID"])
    ]
    significant_proteins_df = pd.merge(intensity_df, sig_df, on="Protein ID", how="left")
    significant_proteins_df = significant_proteins_df.loc[
        significant_proteins_df["Protein ID"].isin(sig_df["Protein ID"])
    ]

    return differentially_expressed_proteins_df, significant_proteins_df


def normalize_ptm_df(ptm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes the PTM data frame by dividing the PTM values by the amount of peptides.
    :param ptm_df: the PTM data frame
    :return: the normalized PTM data frame
    """
    ptm_df_without_sample = ptm_df.drop("Sample", axis=1)

    normalized_ptm_df = ptm_df_without_sample.div(ptm_df["Total Amount of Peptides"], axis=0)

    normalized_ptm_df = normalized_ptm_df.drop("Total Amount of Peptides", axis=1)
    normalized_ptm_df.insert(0, "Sample", ptm_df["Sample"])

    return normalized_ptm_df


INVALID_PROTEINGROUP_DATA_MSG = {
    "level": logging.WARNING,
    "msg": "Due to missing or identical values, the p-values for some protein groups could not be calculated. "
           "These groups were omitted from the analysis. "
           "To prevent this, please add filtering and imputation steps to your workflow before running the analysis.",
}
