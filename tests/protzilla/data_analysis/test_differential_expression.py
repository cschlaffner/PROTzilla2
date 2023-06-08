import numpy as np
import pandas as pd
import pytest

from protzilla.data_analysis.differential_expression import anova, t_test
from protzilla.data_analysis.differential_expression_linear_model import linear_model
from protzilla.data_analysis.plots import create_volcano_plot


@pytest.fixture
def diff_expr_test_data():
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 18],
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

    current_out = linear_model(
        test_intensity_df,
        test_metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        fc_threshold=test_fc_threshold,
    )

    fig = create_volcano_plot(
        current_out["corrected_p_values_df"],
        current_out["log2_fold_change_df"],
        current_out["fc_threshold"],
        current_out["corrected_alpha"],
    )
    if show_figures:
        fig.show()

    corrected_p_values = [0.0072, 0.3838, 1, 0.0072]
    log2_fc = [-5, -0.5, 0, -2.5]
    de_proteins = ["Protein1", "Protein4"]

    p_values_rounded = [
        round(x, 4) for x in current_out["corrected_p_values_df"]["corrected_p_value"]
    ]
    log2fc_rounded = [
        round(x, 4) for x in current_out["log2_fold_change_df"]["log2_fold_change"]
    ]

    assert p_values_rounded == corrected_p_values
    assert log2fc_rounded == log2_fc
    assert (current_out["de_proteins_df"]["Protein ID"].unique() == de_proteins).all()
    assert current_out["fc_threshold"] == test_fc_threshold
    assert current_out["corrected_alpha"] == test_alpha


def test_differential_expression_t_test(diff_expr_test_data, show_figures):
    test_intensity_df, test_metadata_df = diff_expr_test_data
    test_alpha = 0.05
    test_fc_threshold = 0.9

    current_out = t_test(
        test_intensity_df,
        test_metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        fc_threshold=test_fc_threshold,
        log_base="",
    )

    fig = create_volcano_plot(
        current_out["corrected_p_values_df"],
        current_out["log2_fold_change_df"],
        current_out["fc_threshold"],
        current_out["corrected_alpha"],
    )
    if show_figures:
        fig.show()

    corrected_p_values = [0.0072, 0.3838, 1.0, 0.0072]
    log2_fc = [-1, -0.0995, 0, -0.585]
    de_proteins = ["Protein1"]
    significant_proteins = ["Protein1", "Protein4"]

    p_values_rounded = [
        round(x, 4) for x in current_out["corrected_p_values_df"]["corrected_p_value"]
    ]
    log2fc_rounded = [
        round(x, 4) for x in current_out["log2_fold_change_df"]["log2_fold_change"]
    ]

    assert p_values_rounded == corrected_p_values
    assert log2fc_rounded == log2_fc
    assert current_out["de_proteins_df"]["Protein ID"].unique() == de_proteins
    assert current_out["fc_threshold"] == test_fc_threshold
    assert current_out["corrected_alpha"] == test_alpha
    assert (
        current_out["significant_proteins_df"]["Protein ID"].unique()
        == significant_proteins
    ).all()


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
    test_fc_threshold = 0

    current_out = t_test(
        test_intensity_df,
        test_metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        fc_threshold=test_fc_threshold,
        log_base=2,
    )

    log2_fc = [-1, -0.1]
    # because of the longer fc calculation the comparison does not work as accurately as on paper (inaccuracy due to multiple float operations)
    log2fc_rounded = [
        round(x, 1) for x in current_out["log2_fold_change_df"]["log2_fold_change"]
    ]

    assert log2fc_rounded == log2_fc


def test_differential_expression_t_test_with_nan(diff_expr_test_data):
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
    _, test_metadata_df = diff_expr_test_data

    test_alpha = 0.05
    test_fc_threshold = 0

    current_out = t_test(
        test_intensity_df,
        test_metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        fc_threshold=test_fc_threshold,
        log_base="",
    )

    assert "messages" in current_out
    assert "NaN values" in current_out["messages"][0]["msg"]


def test_differential_expression_t_test_with_zero_mean(
    diff_expr_test_data, show_figures
):
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

    _, test_metadata_df = diff_expr_test_data

    test_alpha = 0.05
    test_fc_threshold = 0

    current_out = t_test(
        test_intensity_df,
        test_metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        fc_threshold=test_fc_threshold,
        log_base="",
    )

    fig = create_volcano_plot(
        current_out["corrected_p_values_df"],
        current_out["log2_fold_change_df"],
        current_out["fc_threshold"],
        current_out["corrected_alpha"],
    )
    if show_figures:
        fig.show()

    corrected_p_values = [0.0072, 1.000]
    log2_fc = [-1, 0]
    de_proteins = ["Protein1"]

    p_values_rounded = [
        round(x, 4) for x in current_out["corrected_p_values_df"]["corrected_p_value"]
    ]
    log2fc_rounded = [
        round(x, 4) for x in current_out["log2_fold_change_df"]["log2_fold_change"]
    ]

    assert p_values_rounded == corrected_p_values
    assert log2fc_rounded == log2_fc
    assert current_out["de_proteins_df"]["Protein ID"].unique() == de_proteins
    assert current_out["fc_threshold"] == test_fc_threshold
    assert current_out["corrected_alpha"] == test_alpha

    assert "messages" in current_out
    assert "mean intensity of 0" in current_out["messages"][0]["msg"]


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
