import logging

import numpy as np
import pandas as pd
from scipy import stats

from protzilla.utilities import default_intensity_column, exists_message

from .differential_expression_helper import (
    INVALID_PROTEINGROUP_DATA_MSG,
    _map_log_base,
    apply_multiple_testing_correction, preprocess_grouping,
)


def anova(
    intensity_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    multiple_testing_correction_method: str,
    alpha: float,
    grouping: str,
    log_base: str = None,
    selected_groups: list = None,
    intensity_name: str = None,
) -> dict:
    """
        return dict(
            differentially_expressed_proteins_df=differentially_expressed_proteins_df,
            significant_proteins_df=significant_proteins_df,
            corrected_p_values_df=corrected_p_values_df,
            sample_group_df=sample_group_df,
            corrected_alpha=corrected_alpha,
            filtered_proteins=filtered_proteins,
            messages=messages,
        )
        A function that uses ANOVA to test the difference between two or more
        groups defined in the clinical data. The ANOVA test is conducted on
        the level of each protein. The p-values are corrected for multiple
        testing.

        :param intensity_df: the dataframe that should be tested in long format
        :param metadata_df: the dataframe that contains the clinical data
        :param grouping: the column name of the grouping variable in the metadata_df
        :param selected_groups: groups to test against each other
        :param multiple_testing_correction_method: the method for multiple testing correction
        :param alpha: the alpha value for anova
        :param log_base: in case the data was previously log transformed this parameter contains the base as a string
        :param intensity_name: name of the column containing the protein group intensities
        :return: a dict containing
    - a df differentially_expressed_proteins_df in typical protzilla long format containing the anova results
                corrected_p_value per non-filtered protein
            - a df corrected_p_values, containing the p_values after application of multiple testing correction,
            - a df fold_change_df, containing the fold_changes per protein,
            - a df log2_fold_change, containing the log2 fold changes per protein,
            - a df t_statistic_df, containing the t-statistic per protein,
            - a float corrected_alpha, containing the alpha value after application of multiple testing correction (depending on the selected multiple testing correction method corrected_alpha may be equal to alpha),
            - a df filtered_proteins, containing the filtered out proteins (due to missing values or identical values),
    """

    selected_groups, messages = preprocess_grouping(metadata_df, grouping, selected_groups)

    # Merge the intensity and metadata dataframes in order to assign to each Sample
    # their corresponding group
    intensity_df = pd.merge(
        left=intensity_df,
        right=metadata_df[["Sample", grouping]],
        on="Sample",
        copy=False,
    )
    intensity_name = default_intensity_column(intensity_df, intensity_name)

    log_base = _map_log_base(log_base)  # now log_base in [2, 10, None]

    # Perform ANOVA and calculate p-values for each protein
    proteins = intensity_df["Protein ID"].unique()
    p_values = []
    valid_protein_groups = []
    for protein in proteins:
        protein_df = intensity_df[intensity_df["Protein ID"] == protein]
        all_group_intensities = []
        for group in selected_groups:
            all_group_intensities.append(
                protein_df[protein_df[grouping] == group][intensity_name].to_numpy()
            )
        p = stats.f_oneway(*all_group_intensities)[1]
        if not np.isnan(p):
            p_values.append(p)
            valid_protein_groups.append(protein)
        elif not exists_message(messages, INVALID_PROTEINGROUP_DATA_MSG):
            messages.append(INVALID_PROTEINGROUP_DATA_MSG)

    # Apply multiple testing correction and create a dataframe with corrected p-values
    corrected_p_values, corrected_alpha = apply_multiple_testing_correction(
        p_values, multiple_testing_correction_method, alpha
    )
    corrected_p_values_df = pd.DataFrame(
        list(zip(valid_protein_groups, corrected_p_values)),
        columns=["Protein ID", "corrected_p_values"],
    )
    if corrected_alpha is None:
        corrected_alpha = alpha

    dataframes = [corrected_p_values_df]

    # add the calculated information to the dataframe
    for df in dataframes:
        intensity_df = pd.merge(intensity_df, df, on="Protein ID", copy=False)

    differentially_expressed_proteins = [
        protein for protein, p in zip(valid_protein_groups, corrected_p_values)
    ]
    differentially_expressed_proteins_df = intensity_df[
        intensity_df["Protein ID"].isin(differentially_expressed_proteins)
    ]

    significant_proteins_df = differentially_expressed_proteins_df[
        differentially_expressed_proteins_df["corrected_p_values"] < corrected_alpha
    ]

    # Create mapping from sample to group
    sample_group_df = differentially_expressed_proteins_df[
        ["Sample", grouping]
    ].drop_duplicates()
    filtered_proteins = list(set(proteins) - set(valid_protein_groups))
    return dict(
        differentially_expressed_proteins_df=differentially_expressed_proteins_df,
        significant_proteins_df=significant_proteins_df,
        corrected_p_values_df=corrected_p_values_df,
        sample_group_df=sample_group_df,
        corrected_alpha=corrected_alpha,
        filtered_proteins=filtered_proteins,
        messages=messages,
    )
