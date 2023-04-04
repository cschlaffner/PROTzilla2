import numpy as np
import pandas as pd

from protzilla.data_analysis.differential_expression import anova, t_test


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
        t_test_grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        fc_threshold=test_fc_threshold,
    )

    # fig = t_test_volcano_plot(test_intensity_df, de_proteins_df, current_out, [])[0]
    # if show_figures:
    #     fig.show()

    corrected_p_values = [0.0108, 0.4318, 1.000]
    log2_fc = [-1, -0.0995, 0]
    de_proteins = ["Protein1"]

    p_values_rounded = [round(x, 4) for x in current_out["corrected_p_values"]]
    log2fc_rounded = [round(x, 4) for x in current_out["log2_fold_change"]]

    assert (
        p_values_rounded == corrected_p_values
    ), f"P \
        values do not match! P Values should be {corrected_p_values}, \
                but are {p_values_rounded}"

    assert (
        log2fc_rounded == log2_fc
    ), f"log2 \
        fold change does not match! Should be {log2_fc}, \
                but are {log2fc_rounded}"

    assert (
        de_proteins_df["Protein ID"].unique() == de_proteins
    ), f"\
        Differentially expressed proteins do not match! Should be \
            {de_proteins} but are {de_proteins_df['Protein ID'].unique()}"

    assert (
        current_out["fc_threshold"] == test_fc_threshold
    ), f"fold change \
        threshold does not match!"
    assert current_out["alpha"] == test_alpha, f"alpha does not match!"
    assert (
        current_out["corrected_alpha"] is None
    ), f"corrected alpha does \
        not match"


def test_differential_expression_t_test_with_nan():
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 18],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample2", "Protein1", "Gene1", np.nan],
        ["Sample2", "Protein2", "Gene1", 15],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 14],
        ["Sample3", "Protein3", "Gene1", 3],
        ["Sample4", "Protein1", "Gene1", np.nan],
        ["Sample4", "Protein2", "Gene1", np.nan],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 14],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", np.nan],
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

    _, current_out = t_test(
        test_intensity_df,
        test_metadata_df,
        t_test_grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        fc_threshold=test_fc_threshold,
    )

    test_keywords = "NaN values"

    assert "messages" in current_out
    assert test_keywords in current_out["messages"][0]["msg"]


def test_differential_expression_t_test_with_zero_mean(show_figures):
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 18],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample1", "Protein4", "Gene1", 0],
        ["Sample2", "Protein1", "Gene1", 20],
        ["Sample2", "Protein2", "Gene1", 15],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample2", "Protein4", "Gene1", 0],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 14],
        ["Sample3", "Protein3", "Gene1", 3],
        ["Sample3", "Protein4", "Gene1", 0],
        ["Sample4", "Protein1", "Gene1", 8],
        ["Sample4", "Protein2", "Gene1", -5],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample4", "Protein4", "Gene1", 0],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 0],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample5", "Protein4", "Gene1", 18],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", 5],
        ["Sample6", "Protein3", "Gene1", 3],
        ["Sample6", "Protein4", "Gene1", 18],
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
        t_test_grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        fc_threshold=test_fc_threshold,
    )

    # fig = t_test_volcano_plot(test_intensity_df, de_proteins_df, current_out, [])[0]
    # if show_figures:
    #     fig.show()

    print(de_proteins_df)
    corrected_p_values = [0.0072, 1.000]
    log2_fc = [-1, 0]
    de_proteins = ["Protein1"]

    p_values_rounded = [round(x, 4) for x in current_out["corrected_p_values"]]
    log2fc_rounded = [round(x, 4) for x in current_out["log2_fold_change"]]

    assert (
        p_values_rounded == corrected_p_values
    ), f"P \
        values do not match! P Values should be {corrected_p_values}, \
                but are {p_values_rounded}"

    assert (
        log2fc_rounded == log2_fc
    ), f"log2 \
        fold change does not match! Should be {log2_fc}, \
                but are {log2fc_rounded}"

    assert (
        de_proteins_df["Protein ID"].unique() == de_proteins
    ), f"\
        Differentially expressed proteins do not match! Should be \
            {de_proteins} but are {de_proteins_df['Protein ID'].unique()}"

    assert (
        current_out["fc_threshold"] == test_fc_threshold
    ), f"fold change \
        threshold does not match!"
    assert current_out["alpha"] == test_alpha, f"alpha does not match!"
    assert (
        current_out["corrected_alpha"] is None
    ), f"corrected alpha does \
        not match"

    test_keywords = "mean intensity of 0"
    assert "messages" in current_out
    assert test_keywords in current_out["messages"][0]["msg"]


def test_differential_expression_anova(show_figures):
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
        ["Sample4", "Protein2", "Gene1", 2],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 5],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", 4],
        ["Sample6", "Protein3", "Gene1", 3],
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
    )

    test_metadata_df = pd.DataFrame(
        data=test_metadata_list,
        columns=["Sample", "Group"],
    )

    output_df, output_dict = anova(
        intensity_df=test_intensity_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        selected_groups=test_metadata_df["Group"].unique().tolist(),
        multiple_testing_correction_method="Bonferroni",
        alpha=0.05,
    )
    p_values = output_dict["p_values"]

    p_values_rounded = [round(x, 4) for x in p_values]

    # fig = anova_heatmap(
    #     output_df, grouping="Group", alpha=output_dict["corrected_alpha"]
    # )
    # if show_figures:
    #     fig.show()

    assertion_p_values = [
        0.0036,
        0.0004,
        1.0000,
    ]

    assert assertion_p_values == p_values_rounded
