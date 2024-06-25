import logging

import numpy as np
import pandas as pd
import statsmodels.api as sm

from protzilla.utilities import default_intensity_column, exists_message

from .differential_expression_helper import (
    INVALID_PROTEINGROUP_DATA_MSG,
    _map_log_base,
    apply_multiple_testing_correction,
)


def linear_model(
    intensity_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    grouping: str,
    group1: str,
    group2: str,
    multiple_testing_correction_method: str,
    alpha: float,
    log_base: str = None,
    intensity_name: str = None,
) -> dict:
    """
    A function to fit a linear model using Ordinary Least Squares for each Protein.
    The linear model fits the protein intensities on Y axis and the grouping on X
    for group1 X=-1 and group2 X=1
    The p-values are corrected for multiple testing.

    :param intensity_df: the dataframe that should be tested in long format
    :param metadata_df: the dataframe that contains the clinical data
    :param grouping: the column name of the grouping variable in the metadata_df
    :param group1: the name of the first group for the linear model
    :param group2: the name of the second group for the linear model
    :param multiple_testing_correction_method: the method for multiple testing correction
    :param alpha: the alpha value for the linear model
    :param log_base: in case the data was previously log transformed this parameter contains the base as a string
    :param intensity_name: name of the column containing the protein group intensities

    :return: a dataframe in typical protzilla long format with the differentially expressed
        proteins and a dict, containing the corrected p-values and the log2 fold change (coefficients), the alpha used
        and the corrected alpha, as well as filtered out proteins.
    """
    assert grouping in metadata_df.columns
    messages = []
    # User input handling
    unique_groups = metadata_df[grouping].unique()
    if group1 not in unique_groups:
        group1 = unique_groups[0]
        messages.append(
            {
                "level": logging.WARNING,
                "msg": f"Group 1 was invalid. Auto-selected the group {group1} as group 1.",
            }
        )
    if group2 not in unique_groups or group2 == group1:
        group2 = unique_groups[1]
        messages.append(
            {
                "level": logging.WARNING,
                "msg": f"Group 2 was invalid. Auto-selected the group {group2} as group 2.",
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

    proteins = intensity_df.loc[:, "Protein ID"].unique()
    p_values = []
    valid_protein_groups = []
    log2_fold_changes = []
    for protein in proteins:
        # Create temporary protein-group specific df, containing only the two selected groups
        protein_df = intensity_df.loc[intensity_df["Protein ID"] == protein]
        protein_df = protein_df[protein_df[grouping].isin([group1, group2])]
        protein_df[grouping] = protein_df[grouping].replace([group1, group2], [-1, 1])
        group1_intensities = protein_df[protein_df[grouping] == -1][
            intensity_name
        ].values
        group2_intensities = protein_df[protein_df[grouping] == 1][
            intensity_name
        ].values

        # if a protein has a NaN value in a sample, user should remove it
        if (
            not np.isnan(group1_intensities).any()
            and not np.isnan(group2_intensities).any()
            and len(group1_intensities) > 0
            and len(group2_intensities) > 0
        ):
            # lm(intensity ~ group + constant)
            Y = protein_df[[intensity_name]]
            X = protein_df[[grouping]]
            X = sm.add_constant(X)
            model = sm.OLS(Y, X)
            results = model.fit()
            log2_fold_change = (
                np.log2(
                    np.power(log_base, group2_intensities).mean()
                    / np.power(log_base, group1_intensities).mean()
                )
                if log_base
                else np.log2(group2_intensities.mean() / group1_intensities.mean())
            )

            if not np.isnan(results.pvalues[grouping]):
                valid_protein_groups.append(protein)
                p_values.append(results.pvalues[grouping])
                log2_fold_changes.append(log2_fold_change)
            elif not exists_message(messages, INVALID_PROTEINGROUP_DATA_MSG):
                messages.append(INVALID_PROTEINGROUP_DATA_MSG)
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
    dataframes = [corrected_p_values_df, log2_fold_change_df]

    for df in dataframes:
        intensity_df = pd.merge(intensity_df, df, on="Protein ID", copy=False)

    differentially_expressed_proteins = [
        protein
        for protein, p, fc in zip(
            valid_protein_groups, corrected_p_values, log2_fold_changes
        )
    ]
    differentially_expressed_proteins_df = intensity_df.loc[
        intensity_df["Protein ID"].isin(differentially_expressed_proteins)
    ]
    significant_proteins_df = differentially_expressed_proteins_df[
        differentially_expressed_proteins_df["corrected_p_value"] <= corrected_alpha
    ]

    filtered_proteins = list(set(proteins) - set(valid_protein_groups))

    return dict(
        differentially_expressed_proteins_df=differentially_expressed_proteins_df,
        significant_proteins_df=significant_proteins_df,
        corrected_p_values_df=corrected_p_values_df,
        log2_fold_change_df=log2_fold_change_df,
        corrected_alpha=corrected_alpha,
        filtered_proteins=filtered_proteins,
        messages=messages,
    )
