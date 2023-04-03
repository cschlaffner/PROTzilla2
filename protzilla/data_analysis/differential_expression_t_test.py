import dash_bio as dashbio
import numpy as np
import pandas as pd
from django.contrib import messages
from scipy import stats

from protzilla.constants.colors import PROTZILLA_DISCRETE_COLOR_SEQUENCE
from protzilla.data_analysis.differential_expression_helper import (
    apply_multiple_testing_correction,
)


def t_test(
    intensity_df,
    metadata_df,
    grouping,
    group1,
    group2,
    multiple_testing_correction_method,
    alpha,
    fc_threshold,
):
    # TODO think about how to get the grouping and group1, group2 from the user
    # TODO: alpha does not work in frontend
    print("ttest")
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
    filtered_proteins = []

    for protein in proteins:
        protein_df = intensity_df.loc[intensity_df["Protein ID"] == protein]

        group1_intensities = protein_df.loc[
            protein_df.loc[:, grouping] == group1, intensity_name
        ].to_numpy()
        group2_intensities = protein_df.loc[
            protein_df.loc[:, grouping] == group2, intensity_name
        ].to_numpy()

        # TODO: add new error handling
        # if a protein is not present in the sample something should be filtered out
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


def t_test_volcano_plot(df, result_df, current_out, proteins_of_interest):
    # TODO: add proteins of interest to frontend
    # TODO: write tests? -> think about proteins of interest

    pvalues_log2fc_df = pd.DataFrame(
        {
            "protein": df.loc[:, "Protein ID"].unique().tolist(),
            "corrected_p_values": current_out["corrected_p_values"],
            "log2_fold_change": current_out["log2_fold_change"],
        }
    )

    if current_out["corrected_alpha"] is None:
        p_values_thresh = -np.log10(current_out["alpha"])
    else:
        p_values_thresh = -np.log10(current_out["corrected_alpha"])

    fig = dashbio.VolcanoPlot(
        dataframe=pvalues_log2fc_df,
        effect_size="log2_fold_change",
        p="corrected_p_values",
        snp=None,
        gene=None,
        genomewideline_value=p_values_thresh,
        effect_size_line=[
            -current_out["fc_threshold"],
            current_out["fc_threshold"],
        ],
        xlabel="log2(fc)",
        ylabel="-log10(p)",
        title="Volcano Plot",
        annotation="protein",
    )

    proteins_of_interest = [] if proteins_of_interest is None else proteins_of_interest

    # annotate the proteins of interest permanently in the plot
    for protein in proteins_of_interest:
        fig.add_annotation(
            x=pvalues_log2fc_df.loc[
                pvalues_log2fc_df["protein"] == protein,
                "log2_fold_change",
            ].values[0],
            y=-np.log10(
                pvalues_log2fc_df.loc[
                    pvalues_log2fc_df["protein"] == protein,
                    "corrected_p_values",
                ].values[0]
            ),
            text=protein,
            showarrow=True,
            arrowhead=1,
            font=dict(color="#ffffff"),
            align="center",
            arrowcolor=PROTZILLA_DISCRETE_COLOR_SEQUENCE[0],
            bgcolor=PROTZILLA_DISCRETE_COLOR_SEQUENCE[0],
            opacity=0.8,
            ax=0,
            ay=-20,
        )

    new_names = {
        "Point(s) of interest": "Significant Proteins",
        "Dataset": "Not Significant Proteins",
    }

    return [
        fig.for_each_trace(
            lambda t: t.update(
                name=new_names[t.name],
                legendgroup=new_names[t.name],
            )
        )
    ]
