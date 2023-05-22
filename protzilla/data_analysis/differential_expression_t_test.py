import logging

import numpy as np
import pandas as pd
from django.contrib import messages
from scipy import stats

from .differential_expression_helper import apply_multiple_testing_correction


def t_test(
    intensity_df,
    metadata_df,
    grouping,
    group1,
    group2,
    multiple_testing_correction_method,
    alpha,
    fc_threshold,
    log_base,
):
    """
    A function to conduct a two sample t-test between groups defined in the
    clinical data. The t-test is conducted on the level of each protein.
    The p-values are corrected for multiple testing.

    :param intensity_df: the dataframe that should be tested in long
        format
    :type intensity_df: pandas DataFrame
    :param metadata_df: the dataframe that contains the clinical data
    :type grouping: pandas DataFrame
    :param grouping: the column name of the grouping variable in the
        metadata_df
    :type grouping: str
    :param group1: the name of the first group for the t-test
    :type group1: str
    :param group2: the name of the second group for the t-test
    :type group2: str
    :param multiple_testing_correction_method: the method for multiple
        testing correction
    :type multiple_testing_correction_method: str
    :param alpha: the alpha value for the t-test
    :type alpha: float

    :return: a dict containing a dataframe in typical protzilla long format ccontaining the differentially expressed proteins,
    a df corrected_p_values, containing the p_values after application of multiple testing correction,
    a df log2_fold_change, containing the log2 fold changes per protein,
    a float fc_threshold, containing the absolute threshold for the log fold change, above which a protein is considered differentially expressed,
    a float corrected_alpha, containing the alpha value after application of multiple testing correction (depending on the selected multiple testing correction method corrected_alpha may be equal to alpha),
    a df filtered_proteins, containing the filtered out proteins (proteins where the mean of a group was 0),
    a df fold_change_df, containing the fold_changes per protein.
    :rtype: dict
    """
    assert grouping in metadata_df.columns

    if not group1:
        group1 = metadata_df[grouping].unique()[0]
        logging.warning("auto-selected first group in t-test")
    if not group2:
        group2 = metadata_df[grouping].unique()[1]
        logging.warning("auto-selected second group in t-test")

    proteins = intensity_df.loc[:, "Protein ID"].unique().tolist()
    intensity_name = intensity_df.columns.values.tolist()[3]
    intensity_df = pd.merge(
        left=intensity_df,
        right=metadata_df[["Sample", grouping]],
        on="Sample",
        copy=False,
    )
    p_values = []
    fold_change = []
    log2_fold_change = []
    filtered_proteins = []

    for protein in proteins:
        protein_df = intensity_df.loc[intensity_df["Protein ID"] == protein]

        group1_intensities = protein_df.loc[
            protein_df.loc[:, grouping] == group1, intensity_name
        ].to_numpy()
        group2_intensities = protein_df.loc[
            protein_df.loc[:, grouping] == group2, intensity_name
        ].to_numpy()

        # if a protein has a NaN value in a sample, user should remove it
        group1_is_nan = np.isnan(group1_intensities)
        group2_is_nan = np.isnan(group2_intensities)
        if group1_is_nan.any() or group2_is_nan.any():
            msg = "There are Proteins with NaN values present in your data. \
                Please filter them out before running the differential expression analysis."
            return dict(
                de_proteins_df=None,
                corrected_p_values=None,
                log2_fold_change=None,
                fc_threshold=None,
                corrected_alpha=None,
                messages=[dict(level=messages.ERROR, msg=msg)],
            )

        # if the intensity of a group for a protein is 0, it should be filtered out
        if np.mean(group1_intensities) == 0 or np.mean(group2_intensities) == 0:
            filtered_proteins.append(protein)
            continue

        p = stats.ttest_ind(group1_intensities, group2_intensities)[1]
        p_values.append(p)
        if log_base == "":
            fc = np.mean(group2_intensities) / np.mean(group1_intensities)
        else:
            fc = log_base ** (np.mean(group2_intensities) - np.mean(group1_intensities))
        fold_change.append(fc)
        log2_fold_change.append(np.log2(fc))

    (corrected_p_values, corrected_alpha) = apply_multiple_testing_correction(
        p_values=p_values,
        method=multiple_testing_correction_method,
        alpha=alpha,
    )

    p_values_thresh = alpha if corrected_alpha is None else corrected_alpha
    p_values_mask = corrected_p_values < p_values_thresh
    fold_change_mask = np.abs(log2_fold_change) > fc_threshold

    remaining_proteins = [
        protein for protein in proteins if protein not in filtered_proteins
    ]
    de_proteins = [
        protein
        for i, protein in enumerate(remaining_proteins)
        if p_values_mask[i] and fold_change_mask[i]
    ]
    de_proteins_df = intensity_df.loc[intensity_df["Protein ID"].isin(de_proteins)]

    corrected_p_values_df = pd.DataFrame(
        list(zip(proteins, corrected_p_values)),
        columns=["Protein ID", "corrected_p_value"],
    )

    log2_fold_change_df = pd.DataFrame(
        list(zip(proteins, log2_fold_change)),
        columns=["Protein ID", "log2_fold_change"],
    )
    fold_change_df = pd.DataFrame(
        list(zip(proteins, fold_change)),
        columns=["Protein ID", "fold_change"],
    )

    proteins_filtered = len(filtered_proteins) > 0
    proteins_filtered_warning_msg = f"Some proteins were filtered out because they had a mean intensity of 0 in one of the groups."

    return dict(
        de_proteins_df=de_proteins_df,
        corrected_p_values_df=corrected_p_values_df,
        log2_fold_change_df=log2_fold_change_df,
        fc_threshold=fc_threshold,
        corrected_alpha=corrected_alpha,
        filtered_proteins=filtered_proteins,
        fold_change_df=fold_change_df,
        messages=[dict(level=messages.WARNING, msg=proteins_filtered_warning_msg)]
        if proteins_filtered
        else [],
    )
