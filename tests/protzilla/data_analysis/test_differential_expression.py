import numpy as np
import pandas as pd
import pytest

from protzilla.data_analysis.differential_expression import anova, linear_model, t_test
from protzilla.data_analysis.plots import create_volcano_plot


@pytest.fixture
def diff_expr_test_data():
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 20],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample1", "Protein4", "Gene1", 14],
        ["Sample2", "Protein1", "Gene1", 20],
        ["Sample2", "Protein2", "Gene1", 15],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample2", "Protein4", "Gene1", 15],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 14],
        ["Sample3", "Protein3", "Gene1", 3],
        ["Sample3", "Protein4", "Gene1", 16],
        ["Sample4", "Protein1", "Gene1", 8],
        ["Sample4", "Protein2", "Gene1", 15],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample4", "Protein4", "Gene1", 9],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 14],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample5", "Protein4", "Gene1", 10],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", 13],
        ["Sample6", "Protein3", "Gene1", 3],
        ["Sample6", "Protein4", "Gene1", 11],
        ["Sample7", "Protein1", "Gene1", 12],
        ["Sample7", "Protein2", "Gene1", 13],
        ["Sample7", "Protein3", "Gene1", 3],
        ["Sample7", "Protein4", "Gene1", 11],
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
    return test_intensity_df, test_metadata_df


def test_differential_expression_linear_model(
    diff_expr_test_data,
    show_figures,
):
    test_intensity_df, test_metadata_df = diff_expr_test_data
    test_alpha = 0.05
    test_fc_threshold = 0

    current_input = dict(
        intensity_df=test_intensity_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        log_base="log2",
    )
    current_out = linear_model(**current_input)

    fig = create_volcano_plot(
        p_values=current_out["corrected_p_values_df"],
        log2_fc=current_out["log2_fold_change_df"],
        alpha=current_out["corrected_alpha"],
        group1=current_input["group1"],
        group2=current_input["group2"],
        fc_threshold=test_fc_threshold,
    )

    if show_figures:
        fig.show()

    corrected_p_values = [0.0053, 0.3838, 1.0, 0.0072]
    log2_fc = [-10.1926, -1.0, 0.0, -5.0]
    differentially_expressed_proteins = ["Protein1", "Protein2", "Protein3", "Protein4"]

    p_values_rounded = [
        round(x, 4) for x in current_out["corrected_p_values_df"]["corrected_p_value"]
    ]
    log2fc_rounded = [
        round(x, 4) for x in current_out["log2_fold_change_df"]["log2_fold_change"]
    ]

    assert p_values_rounded == corrected_p_values
    assert log2fc_rounded == log2_fc
    assert (
        list(current_out["differentially_expressed_proteins_df"]["Protein ID"].unique())
        == differentially_expressed_proteins
    )
    assert current_out["corrected_alpha"] == test_alpha


def test_differential_expression_student_t_test(diff_expr_test_data, show_figures):
    test_intensity_df, test_metadata_df = diff_expr_test_data
    test_alpha = 0.05
    test_fc_threshold = 0.9

    current_input = dict(
        intensity_df=test_intensity_df,
        metadata_df=test_metadata_df,
        ttest_type="Student's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        log_base="None",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )
    current_out = t_test(**current_input)

    fig = create_volcano_plot(
        current_out["corrected_p_values_df"],
        current_out["log2_fold_change_df"],
        test_fc_threshold,
        current_out["corrected_alpha"],
        current_input["group1"],
        current_input["group2"],
    )
    if show_figures:
        fig.show()

    corrected_p_values = [0.0072, 0.3838, 1.0, 0.0072]
    differentially_expressed_proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
        "Protein4",
    ]
    significant_proteins = ["Protein1", "Protein4"]

    p_values_rounded = [
        round(x, 4) for x in current_out["corrected_p_values_df"]["corrected_p_value"]
    ]
    log2fc_rounded = [
        round(x, 4) for x in current_out["log2_fold_change_df"]["log2_fold_change"]
    ]

    assert p_values_rounded == corrected_p_values
    assert (
        list(current_out["differentially_expressed_proteins_df"]["Protein ID"].unique())
        == differentially_expressed_proteins
    )
    assert current_out["corrected_alpha"] == test_alpha
    assert (
        list(current_out["significant_proteins_df"]["Protein ID"].unique())
        == significant_proteins
    )


def test_differential_expression_welch_t_test(diff_expr_test_data, show_figures):
    test_intensity_df, test_metadata_df = diff_expr_test_data
    test_alpha = 0.05
    test_fc_threshold = 0.9

    current_input = dict(
        intensity_df=test_intensity_df,
        metadata_df=test_metadata_df,
        ttest_type="Welch's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        log_base="None",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )
    current_out = t_test(**current_input)

    fig = create_volcano_plot(
        current_out["corrected_p_values_df"],
        current_out["log2_fold_change_df"],
        test_fc_threshold,
        current_out["corrected_alpha"],
        current_input["group1"],
        current_input["group2"],
    )
    if show_figures:
        fig.show()

    corrected_p_values = [0.0053, 0.3838, 1.0, 0.0072]
    differentially_expressed_proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
        "Protein4",
    ]
    significant_proteins = ["Protein1", "Protein4"]

    p_values_rounded = [
        round(x, 4) for x in current_out["corrected_p_values_df"]["corrected_p_value"]
    ]
    log2fc_rounded = [
        round(x, 4) for x in current_out["log2_fold_change_df"]["log2_fold_change"]
    ]

    assert p_values_rounded == corrected_p_values
    assert (
        list(current_out["differentially_expressed_proteins_df"]["Protein ID"].unique())
        == differentially_expressed_proteins
    )
    assert current_out["corrected_alpha"] == test_alpha
    assert (
        list(current_out["significant_proteins_df"]["Protein ID"].unique())
        == significant_proteins
    )


def test_differential_expression_t_test_types(diff_expr_test_data, show_figures):
    test_intensity_df, test_metadata_df = diff_expr_test_data
    test_alpha = 0.05

    # Run Student's t-test
    student_out = t_test(
        test_intensity_df,
        test_metadata_df,
        ttest_type="Student's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        log_base="None",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )

    # Run Welch's t-test
    welch_out = t_test(
        test_intensity_df,
        test_metadata_df,
        ttest_type="Welch's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        log_base="None",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )

    # Check if the p-values are different
    assert not np.array_equal(
        student_out["corrected_p_values_df"]["corrected_p_value"],
        welch_out["corrected_p_values_df"]["corrected_p_value"],
    )


def test_differential_expression_t_test_with_log_data(show_figures):
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1"],
        ["Sample1", "Protein2", "Gene1"],
        ["Sample2", "Protein1", "Gene1"],
        ["Sample2", "Protein2", "Gene1"],
        ["Sample3", "Protein1", "Gene1"],
        ["Sample3", "Protein2", "Gene1"],
        ["Sample4", "Protein1", "Gene1"],
        ["Sample4", "Protein2", "Gene1"],
        ["Sample5", "Protein1", "Gene1"],
        ["Sample5", "Protein2", "Gene1"],
        ["Sample6", "Protein1", "Gene1"],
        ["Sample6", "Protein2", "Gene1"],
    )
    intensities = np.log2([18, 16, 20, 15, 22, 14, 8, 15, 10, 14, 12, 13])
    test_intensity_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene"],
    )

    test_intensity_df["Intensity"] = intensities

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

    current_out = t_test(
        test_intensity_df,
        test_metadata_df,
        ttest_type="Student's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        log_base="log2",
    )

    log2_fc = [-1, -0.1]
    # because of the longer fc calculation the comparison does not work as accurately as on paper (inaccuracy due to multiple float operations)
    log2fc_rounded = [
        round(x, 1) for x in current_out["log2_fold_change_df"]["log2_fold_change"]
    ]

    assert log2fc_rounded == log2_fc


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

    output_dict = anova(
        intensity_df=test_intensity_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        log_base="log2",
        selected_groups=test_metadata_df["Group"].unique().tolist(),
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
    )
    corrected_p_values_df = output_dict["corrected_p_values_df"]

    p_values_rounded = [
        round(x, 4) for x in corrected_p_values_df["corrected_p_values"]
    ]
    assertion_p_values = [
        0.0054,
        0.0013,
        1.0000,
    ]

    assert assertion_p_values == p_values_rounded