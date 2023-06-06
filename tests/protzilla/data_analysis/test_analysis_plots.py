import pandas as pd
import pytest

from protzilla.data_analysis.differential_expression import t_test
from protzilla.data_analysis.plots import create_volcano_plot


@pytest.fixture
def ttest_output():
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

    return t_test(
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


def test_plots_volcano_plot_no_annotation(ttest_output, show_figures):
    fig = create_volcano_plot(
        p_values=ttest_output["corrected_p_values_df"],
        log2_fc=ttest_output["log2_fold_change_df"],
        fc_threshold=ttest_output["fc_threshold"],
        alpha=ttest_output["corrected_alpha"],
    )
    if show_figures:
        fig.show()


def test_plots_volcano_plot_multiple_annotations(ttest_output, show_figures):
    fig = create_volcano_plot(
        p_values=ttest_output["corrected_p_values_df"],
        log2_fc=ttest_output["log2_fold_change_df"],
        fc_threshold=ttest_output["fc_threshold"],
        alpha=ttest_output["corrected_alpha"],
        proteins_of_interest=["Protein1", "Protein2"],
    )
    if show_figures:
        fig.show()
