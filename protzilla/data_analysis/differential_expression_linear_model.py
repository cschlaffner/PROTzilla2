import logging
import multiprocessing

import numpy as np
import pandas as pd
import statsmodels.api as sm
from django.contrib import messages
import concurrent.futures

from .differential_expression_helper import apply_multiple_testing_correction
from ..utilities import chunks


def linear_model(
        intensity_df,
        metadata_df,
        grouping,
        group1,
        group2,
        multiple_testing_correction_method,
        alpha,
        fc_threshold,
):
    """
    A function to fit a linear model using Ordinary Least Squares for each Protein.
    The linear model fits the protein intensities on Y axis and the grouping on X
    for group1 X=-1 and group2 X=1
    The p-values are corrected for multiple testing.

    :param intensity_df: the dataframe that should be tested in long format
    :type intensity_df: pandas DataFrame
    :param metadata_df: the dataframe that contains the clinical data
    :type metadata_df: pandas DataFrame
    :param grouping: the column name of the grouping variable in the metadata_df
    :type grouping: str
    :param group1: the name of the first group for the linear model
    :type group1: str
    :param group2: the name of the second group for the linear model
    :type group2: str
    :param multiple_testing_correction_method: the method for multiple testing correction
    :type multiple_testing_correction_method: str
    :param alpha: the alpha value for the linear model
    :type alpha: float
    :param fc_threshold: the fold change threshold
    :type fc_threshold: float

    :return: a dataframe in typical protzilla long format with the differentially expressed
    proteins and a dict, containing the corrected p-values and the log2 fold change (coefficients), the alpha used
    and the corrected alpha, as well as filtered out proteins.
    :rtype: Tuple[pandas DataFrame, dict]
    """
    assert grouping in metadata_df.columns

    if not group1:
        group1 = metadata_df[grouping].unique()[0]
        logging.warning("auto-selected first group in linear model")
    if not group2:
        group2 = metadata_df[grouping].unique()[1]
        logging.warning("auto-selected second group in linear model")

    proteins = intensity_df.loc[:, "Protein ID"].unique().tolist()
    intensity_name = intensity_df.columns.values.tolist()[3]
    intensity_df = pd.merge(
        left=intensity_df,
        right=metadata_df[["Sample", grouping]],
        on="Sample",
        copy=False,
    )
    p_values = []
    log2_fold_change = []
    filtered_proteins = []

    # split into 4 processes
    proteins_chunks = list(chunks(proteins, 4))
    params = (intensity_df, grouping, group1, group2, intensity_name)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(linear_model_worker, chunk, *params) for chunk in proteins_chunks]
        results = [result for success, result in [f.result() for f in futures]]
        success = [success for success, result in [f.result() for f in futures]]

    if not all(success):
        msg = "There are Proteins with NaN values present in your data. \
                            Please filter them out before running the differential expression analysis."
        return dict(
            de_proteins_df=None,
            corrected_p_values=None,
            log2_fold_change=None,
            fc_threshold=None,
            alpha=alpha,
            corrected_alpha=None,
            messages=[dict(level=messages.ERROR, msg=msg)],
        )

    for result in results:
        p_values.append(result.pvalues[grouping])
        log2_fold_change.append(result.params[grouping])

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
        for protein, has_p, has_fc in zip(
            remaining_proteins, p_values_mask, fold_change_mask
        )
        if has_p and has_fc
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

    proteins_filtered = len(filtered_proteins) > 0
    proteins_filtered_warning_msg = f"Some proteins were filtered out because they had a mean intensity of 0 in one of the groups."

    return dict(
        de_proteins_df=de_proteins_df,
        corrected_p_values_df=corrected_p_values_df,
        log2_fold_change_df=log2_fold_change_df,
        fc_threshold=fc_threshold,
        corrected_alpha=corrected_alpha,
        filtered_proteins=filtered_proteins,
        messages=[dict(level=messages.WARNING, msg=proteins_filtered_warning_msg)]
        if proteins_filtered
        else [],
    )


def linear_model_worker(
        proteins_chunk, intensity_df, grouping, group1, group2, intensity_name
):
    """
    puts in results_dict: a Tuple of a boolean if successfully executed t-test and result of
    t-test or in event of no success the error msg
    """
    for protein in proteins_chunk:
        protein_df = intensity_df.loc[intensity_df["Protein ID"] == protein]
        protein_df = protein_df.loc[
            (protein_df.loc[:, grouping] == group1)
            | (protein_df.loc[:, grouping] == group2)
            ]
        protein_df[grouping] = protein_df[grouping].replace([group1, group2], [-1, 1])

        # if a protein has a NaN value in a sample, user should remove it
        intensity_is_nan = np.isnan(protein_df[[intensity_name]].to_numpy())
        if intensity_is_nan.any():
            return False, None

        # lm(intensity ~ group + constant)
        Y = protein_df[[intensity_name]]
        X = protein_df[[grouping]]
        X = sm.add_constant(X)
        model = sm.OLS(Y, X)
        results = model.fit()

        return True, results
