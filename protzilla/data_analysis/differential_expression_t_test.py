import logging

import numpy as np
import pandas as pd
from scipy import stats

from protzilla.utilities import default_intensity_column

from .differential_expression_helper import apply_multiple_testing_correction


def _is_valid(value):
    return value != 0 and not np.isnan(value)


def t_test(
    intensity_df,
    metadata_df,
    grouping,
    group1,
    group2,
    multiple_testing_correction_method,
    alpha,
    fc_threshold,
    log_base=None,
    intensity_name=None,
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
    :param fc_threshold: threshold for the abs(log_2(fold_change)) (vertical line in a volcano plot).
        Only proteins with a larger abs(log_2(fold_change)) than the fc_threshold are seen as differentially expressed
    :type fc_threshold: float
    :param log_base: in case the data was previously log transformed this parameter contains the base (e.g. 2 if the data was log_2 transformed).
    :type log_base: int / None
    :param intensity_name: name of the column containing the protein group intensities
    :type intensity_name: str / None

    :return: a dict containing
        a df corrected_p_values, containing the p_values after application of multiple testing correction,
        a df log2_fold_change, containing the log2 fold changes per protein,
        a float fc_threshold, containing the absolute threshold for the log fold change, above which a protein is considered differentially expressed,
        a float corrected_alpha, containing the alpha value after application of multiple testing correction (depending on the selected multiple testing correction method corrected_alpha may be equal to alpha),
        a df filtered_proteins, containing the filtered out proteins (proteins where the mean of a group was 0),
        a df fold_change_df, containing the fold_changes per protein,
        a df t_statistic_df, containing the t-statistic per protein,
        a df de_proteins_df in typical protzilla long format containing the differentially expressed proteins;
            corrected_p_value, log2_fold_change, fold_change and t_statistic per protein,
        a df significant_proteins_df, containing the proteins where the p-values are smaller than alpha (if fc_threshold = 0, the significant proteins equal the differentially expressed ones)
            corrected_p_value, log2_fold_change, fold_change and t_statistic per protein,
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
    intensity_name = default_intensity_column(intensity_df, intensity_name)

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
    t_statistic = []

    for protein in proteins:
        protein_df = intensity_df.loc[intensity_df["Protein ID"] == protein]

        group1_intensities = protein_df.loc[
            protein_df.loc[:, grouping] == group1, intensity_name
        ].to_numpy()
        group2_intensities = protein_df.loc[
            protein_df.loc[:, grouping] == group2, intensity_name
        ].to_numpy()

        group1_intensities = group1_intensities[~np.isnan(group1_intensities)]
        group2_intensities = group2_intensities[~np.isnan(group2_intensities)]

        # if the intensity of a group for a protein is 0 or NaN (empty group)
        # it should be filtered out
        if not _is_valid(np.mean(group1_intensities)) or not _is_valid(
            np.mean(group2_intensities)
        ):
            filtered_proteins.append(protein)
            continue

        t, p = stats.ttest_ind(group1_intensities, group2_intensities)
        p_values.append(p)
        t_statistic.append(t)
        if log_base is None:
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

    p_values_mask = corrected_p_values < corrected_alpha
    fold_change_mask = np.abs(log2_fold_change) > fc_threshold

    remaining_proteins = [
        protein for protein in proteins if protein not in filtered_proteins
    ]

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

    t_statistic_df = pd.DataFrame(
        list(zip(proteins, t_statistic)),
        columns=["Protein ID", "t_statistic"],
    )

    # add corrected p-values, fold change, log2 fold change and t-statistic to intensity_df
    dataframes = [
        corrected_p_values_df,
        log2_fold_change_df,
        fold_change_df,
        t_statistic_df,
    ]
    for df in dataframes:
        intensity_df = pd.merge(intensity_df, df, on="Protein ID", how="left")

    de_proteins = [
        protein
        for protein, has_p, has_fc in zip(
            remaining_proteins, p_values_mask, fold_change_mask
        )
        if has_p and has_fc
    ]
    de_proteins_df = intensity_df.loc[intensity_df["Protein ID"].isin(de_proteins)]

    significant_proteins = [
        protein for i, protein in enumerate(remaining_proteins) if p_values_mask[i]
    ]
    significant_proteins_df = intensity_df.loc[
        intensity_df["Protein ID"].isin(significant_proteins)
    ]

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
        t_statistic_df=t_statistic_df,
        significant_proteins_df=significant_proteins_df,
        messages=[dict(level=logging.WARNING, msg=proteins_filtered_warning_msg)]
        if proteins_filtered
        else [],
    )
