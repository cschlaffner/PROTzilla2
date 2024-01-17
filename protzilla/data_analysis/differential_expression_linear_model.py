import logging

import numpy as np
import pandas as pd
import statsmodels.api as sm

from protzilla.utilities import default_intensity_column

from .differential_expression_helper import apply_multiple_testing_correction


def linear_model(
    intensity_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    grouping: str,
    group1: str,
    group2: str,
    multiple_testing_correction_method: str,
    alpha: float,
    fc_threshold: float,
    intensity_name=None,
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
    :param fc_threshold: the fold change threshold
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
                "level": logging.INFO,
                "msg": f"Group 1 was invalid. Auto-selected the group {group1} as group 1.",
            }
        )
    if group2 not in unique_groups or group2 == group1:
        group2 = unique_groups[1]
        messages.append(
            {
                "level": logging.INFO,
                "msg": f"Group 2 was invalid. Auto-selected the group {group2} as group 2.",
            }
        )

    intensity_df = pd.merge(
        left=intensity_df,
        right=metadata_df[["Sample", grouping]],
        on="Sample",
        copy=False,
    )
    proteins = intensity_df.loc[:, "Protein ID"].unique()
    p_values = []
    valid_protein_groups = []
    fold_changes = []
    log2_fold_changes = []
    intensity_name = default_intensity_column(intensity_df, intensity_name)
    for protein in proteins:
        # Create temporary protein-group specific df, containing only the two selected groups
        protein_df = intensity_df.loc[intensity_df["Protein ID"] == protein]
        protein_df = protein_df[protein_df[grouping].isin([group1, group2])]
        protein_df[grouping] = protein_df[grouping].replace([group1, group2], [-1, 1])

        # if a protein has a NaN value in a sample, user should remove it
        if not protein_df[intensity_name].isnull().values.any():
            # lm(intensity ~ group + constant)
            Y = protein_df[[intensity_name]]
            X = protein_df[[grouping]]
            X = sm.add_constant(X)
            model = sm.OLS(Y, X)
            results = model.fit()
            group1_avg = protein_df[protein_df[grouping] == -1][intensity_name].mean()
            group2_avg = protein_df[protein_df[grouping] == 1][intensity_name].mean()
            fold_change = group2_avg / group1_avg
            log2_fold_change = np.log2(fold_change)

            valid_protein_groups.append(protein)
            p_values.append(results.pvalues[grouping])
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

    fold_change_df = pd.DataFrame(
        list(zip(valid_protein_groups, fold_changes)),
        columns=["Protein ID", "fold_change"],
    )

    log2_fold_change_df = pd.DataFrame(
        list(zip(valid_protein_groups, log2_fold_changes)),
        columns=["Protein ID", "log2_fold_change"],
    )

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

    filtered_proteins = list(set(proteins) - set(valid_protein_groups))

    return dict(
        differentially_expressed_proteins_df=differentially_expressed_proteins_df,
        corrected_p_values_df=corrected_p_values_df,
        fold_change_df=fold_change_df,
        log2_fold_change_df=log2_fold_change_df,
        fc_threshold=fc_threshold,
        corrected_alpha=corrected_alpha,
        filtered_proteins=filtered_proteins,
        messages=messages,
    )
