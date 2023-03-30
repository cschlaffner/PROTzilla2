import pandas as pd
import numpy as np
from statsmodels.stats.multitest import multipletests
from scipy import stats
import dash_bio as dashbio
from constants.colors import PROTZILLA_DISCRETE_COLOR_SEQUENCE
import differential_expression_anova

def _apply_multiple_testing_correction(
        p_values: list, method: str, alpha: float
    ):
        """
        Applies a multiple testing correction method to a list of p-values
        using a given alpha.
        :param p_values: list of p-values to be corrected
        :type p_values: list
        :param method: the multiple testing correction method to be used.\
            Can be either "Bonferroni" or "Benjamini-Hochberg"
        :type method: str
        :param alpha: the alpha value to be used for the correction
        :type alpha: float
        :return: a tuple containing the corrected p-values and the\
            corrected alpha value (if applicable)
        :rtype: tuple
        """
        to_param = {"Bonferroni": "bonferroni", "Benjamini-Hochberg": "fdr_bh"}
        correction = multipletests(
            pvals=p_values, alpha=alpha, method=to_param[method]
        )
        if method == "Bonferroni":
            return correction[1], correction[3]
        return correction[1], None




def anova(**kwargs):
    differential_expression_anova.anova(kwargs)


def t_test(
    # TODO think about how to get the grouping and group1, group2 from the user
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

    for protein in proteins:
        protein_df = intensity_df.loc[
            intensity_df["Protein ID"] == protein
        ]

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
        if group1_is_nan.any():
            raise ValueError(
                f"Protein {protein} has {group1_is_nan.sum()} missing values \
                    in group {group1}. Consider revising your \
                        preprocessing regarding missing values."
            )

        elif group2_is_nan.any():
            raise ValueError(
                f"Protein {protein} has {group2_is_nan.sum()} missing values \
                    in group {group2}. Consider revising your \
                        preprocessing regarding missing values."
            )

        p = stats.ttest_ind(group1_intensities, group2_intensities)[1]
        p_values += [p]

        # TODO: add new error handling
        # if the intensity of a group for a sample is 0, it should be filtered out
        if (
            np.mean(group1_intensities) == 0
            or np.mean(group2_intensities) == 0
        ):
            raise ValueError(
                "One of the groups has a mean of 0. Consider filtering \
                    your data before running the differential expression \
                        analysis."
            )

        fold_change.append(
            np.mean(group2_intensities) / np.mean(group1_intensities)
        )

    (corrected_p_values,corrected_alpha) = _apply_multiple_testing_correction(
        p_values=p_values,
        method=multiple_testing_correction_method,
        alpha=alpha,
    )

    log2_fold_change = np.log2(fold_change)
    p_values_thresh = alpha if corrected_alpha is None else corrected_alpha
    p_values_mask = corrected_p_values < p_values_thresh
    fold_change_mask = np.abs(log2_fold_change) > fc_threshold
    deg_proteins = [protein for i, protein in proteins if p_values_mask[i] and fold_change_mask[i]]
    deg_proteins_df = intensity_df.loc[intensity_df["Protein ID"].isin(deg_proteins)]

    return (deg_proteins_df, dict(corrected_p_values=corrected_p_values, 
            log2_fold_change=log2_fold_change, fc_threshold=fc_threshold, 
            alpha=alpha, corrected_alpha=corrected_alpha))

def t_test_volcano_plot(df, result_df, current_out, proteins_of_interest):
    # TODO: add proteins of interest to frontend
    # TODO: Does this method need to be added to the mapping etc?

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
        effect_size_line=[-current_out["fc_threshold"], current_out["fc_threshold"]],
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

    return [fig.for_each_trace(
        lambda t: t.update(
            name=new_names[t.name],
            legendgroup=new_names[t.name],
        )
    )]
  