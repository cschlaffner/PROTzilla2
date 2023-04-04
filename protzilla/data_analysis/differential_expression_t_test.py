import numpy as np
import pandas as pd
from django.contrib import messages
from scipy import stats

from protzilla.data_analysis.differential_expression_helper import (
    apply_multiple_testing_correction,
)


def t_test(
    intensity_df,
    metadata_df,
    t_test_grouping,
    group1,
    group2,
    multiple_testing_correction_method,
    alpha,
    fc_threshold,
):
    print("ttest")
    proteins = intensity_df.loc[:, "Protein ID"].unique().tolist()
    intensity_name = intensity_df.columns.values.tolist()[3]
    intensity_df = pd.merge(
        left=intensity_df,
        right=metadata_df[["Sample", t_test_grouping]],
        on="Sample",
        copy=False,
    )
    p_values = []
    fold_change = []
    filtered_proteins = []

    for protein in proteins:
        protein_df = intensity_df.loc[intensity_df["Protein ID"] == protein]

        group1_intensities = protein_df.loc[
            protein_df.loc[:, t_test_grouping] == group1, intensity_name
        ].to_numpy()
        group2_intensities = protein_df.loc[
            protein_df.loc[:, t_test_grouping] == group2, intensity_name
        ].to_numpy()

        # if a protein has a NaN value in a sample, user should remove it
        group1_is_nan = np.isnan(group1_intensities)
        group2_is_nan = np.isnan(group2_intensities)
        if group1_is_nan.any() or group2_is_nan.any():
            msg = "There are Proteins with NaN values present in your data. \
                Please filter them out before running the differential expression analysis."
            return intensity_df, dict(
                corrected_p_values=None,
                log2_fold_change=None,
                fc_threshold=None,
                alpha=alpha,
                corrected_alpha=None,
                messages=[dict(level=messages.ERROR, msg=msg)],
            )

        p = stats.ttest_ind(group1_intensities, group2_intensities)[1]

        # if the intensity of a group for a protein is 0, it should be filtered out
        if np.mean(group1_intensities) == 0 or np.mean(group2_intensities) == 0:
            filtered_proteins.append(protein)
            continue

        p_values.append(p)
        fold_change.append(np.mean(group2_intensities) / np.mean(group1_intensities))

    (corrected_p_values, corrected_alpha) = apply_multiple_testing_correction(
        p_values=p_values,
        method=multiple_testing_correction_method,
        alpha=alpha,
    )

    log2_fold_change = np.log2(fold_change)
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

    if len(filtered_proteins) > 0:
        msg = f"Some proteins were filtered out because they had a mean intensity of 0 in one of the groups."
        return (
            de_proteins_df,
            dict(
                corrected_p_values=corrected_p_values,
                log2_fold_change=log2_fold_change,
                fc_threshold=fc_threshold,
                alpha=alpha,
                corrected_alpha=corrected_alpha,
                filtered_proteins=filtered_proteins,
                messages=[dict(level=messages.WARNING, msg=msg)],
            ),
        )

    return (
        de_proteins_df,
        dict(
            corrected_p_values=corrected_p_values,
            log2_fold_change=log2_fold_change,
            fc_threshold=fc_threshold,
            alpha=alpha,
            corrected_alpha=corrected_alpha,
        ),
    )
