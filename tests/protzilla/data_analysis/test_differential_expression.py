import pandas as pd
import pytest

from protzilla.data_analysis.differential_expression import t_test, t_test_volcano_plot


def test_differential_expression_t_test(show_figures):
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 18],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample2", "Protein1", "Gene1", 20],
        ["Sample2", "Protein2", "Gene1", 15],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 14],
        ["Sample3", "Protein3", "Gene1", 3],
        ["Sample4", "Protein1", "Gene1", 8],
        ["Sample4", "Protein2", "Gene1", 15],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 14],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", 13],
        ["Sample6", "Protein3", "Gene1", 3],
        ["Sample7", "Protein1", "Gene1", 12],
        ["Sample7", "Protein2", "Gene1", 13],
        ["Sample7", "Protein3", "Gene1", 3],
    )

    test_intensity_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    test_metadata_list = (
        ["Sample1", "Group1"],
        ["Sample2", "Group1"],
        ["Sample3", "Group1"],
        ["Sample4", "Group2"],
        ["Sample5", "Group2"],
        ["Sample6", "Group2"],
        ["Sample7", "Group3"],
    )

    test_metadata_df = pd.DataFrame(
        data=test_metadata_list,
        columns=["Sample", "Group"],
    )

    test_alpha = 0.05
    test_fc_threshold = 0

    de_proteins_df, current_out = t_test(
        test_intensity_df,
        test_metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        fc_threshold=test_fc_threshold,
    )

    fig = t_test_volcano_plot(test_intensity_df, de_proteins_df, current_out, [])[0]
    if show_figures:
        fig.show()

    corrected_p_values = [0.0108, 0.4318, 1.000]
    log2_fc = [-1, -0.0996, 0]
    de_proteins = ["Protein1", "Protein2"]

    assert (
        current_out["corrected_p_values"].round(4) == corrected_p_values
    ), f"P \
        values do not match! P Values should be {corrected_p_values}, \
                but are {current_out['corrected_p_values'].round(4)}"

    assert (
        current_out["log2_fold_change"].round(4) == log2_fc
    ), f"log2 \
        fold change does not match! Should be {log2_fc}, \
                but are {current_out['log2_fold_change'].round(4)}"

    assert (
        de_proteins_df["Protein ID"].values() == de_proteins
    ), f"\
        Differentially expressed proteins do not match! Should be \
            {de_proteins} but are {de_proteins_df['Protein ID'].values()}"

    assert (
        current_out["fc_threshold"] == test_fc_threshold
    ), f"fold change \
        threshold does not match!"
    assert current_out["alpha"] == test_alpha, f"alpha does not match!"
    assert (
        current_out["corrected_alpha"] is None
    ), f"corrected alpha does \
        not match"
