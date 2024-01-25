import pandas as pd
import pytest

from protzilla.data_preprocessing.filter_samples import (
    by_protein_count,
    by_protein_count_plot,
    by_protein_intensity_sum,
    by_protein_intensity_sum_plot,
    by_proteins_missing,
    by_proteins_missing_plot,
)


@pytest.fixture
def filter_samples_df():
    filter_samples_list = (
        ["Sample1", "Protein1", "Gene1", 1],
        ["Sample1", "Protein2", "Gene2", 2],
        ["Sample1", "Protein3", "Gene3", 3],
        ["Sample1", "Protein4", "Gene4", 4],
        ["Sample1", "Protein5", "Gene5", 5],
        ["Sample2", "Protein1", "Gene1"],
        ["Sample2", "Protein2", "Gene2", 2],
        ["Sample2", "Protein3", "Gene3"],
        ["Sample2", "Protein4", "Gene4", 5],
        ["Sample2", "Protein5", "Gene5"],
        ["Sample3", "Protein1", "Gene1"],
        ["Sample3", "Protein2", "Gene2"],
        ["Sample3", "Protein3", "Gene3", 10],
        ["Sample3", "Protein4", "Gene4", 20],
        ["Sample3", "Protein5", "Gene5", 20],
    )

    filter_samples_df = pd.DataFrame(
        data=filter_samples_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    filter_samples_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True, inplace=True
    )

    return filter_samples_df


def test_by_proteins_missing(filter_samples_df, show_figures):
    result_df1, method_output1 = by_proteins_missing(filter_samples_df, percentage=0.5)
    result_df2, method_output2 = by_proteins_missing(filter_samples_df, percentage=0.6)
    result_df3, method_output3 = by_proteins_missing(filter_samples_df, percentage=0.65)

    list_samples_excluded_1 = method_output1["filtered_samples"]
    list_samples_excluded_2 = method_output2["filtered_samples"]
    list_samples_excluded_3 = method_output3["filtered_samples"]

    fig = by_proteins_missing_plot(
        filter_samples_df, result_df1, method_output1, "Pie chart"
    )[0]
    if show_figures:
        fig.show()

    assert list_samples_excluded_1 == [
        "Sample2"
    ], f"excluded samples do not match \
                Sample2, but are {list_samples_excluded_1}"

    assert list_samples_excluded_2 == [
        "Sample2",
    ], f"excluded samples do not match \
                Sample2 and Sample3, but are {list_samples_excluded_2}"
    assert list_samples_excluded_3 == [
        "Sample2",
        "Sample3",
    ], f"excluded samples do not match \
                    Sample2 and Sample3, but are {list_samples_excluded_3}"


def test_filter_samples_by_protein_count(filter_samples_df, show_figures):
    result_df1, method_output1 = by_protein_count(
        filter_samples_df, deviation_threshold=0.3
    )
    result_df2, method_output2 = by_protein_count(
        filter_samples_df, deviation_threshold=1
    )

    list_samples_excluded_1 = method_output1["filtered_samples"]
    list_samples_excluded_2 = method_output2["filtered_samples"]

    fig = by_protein_count_plot(
        filter_samples_df, result_df1, method_output1, "Pie chart"
    )[0]
    if show_figures:
        fig.show()

    assert list_samples_excluded_1 == [
        "Sample1",
        "Sample2",
    ], f"excluded samples do not match \
            Sample1 and Sample2, but are {list_samples_excluded_1}"

    assert list_samples_excluded_2 == [
        "Sample1"
    ], f"excluded samples do not match \
            Sample1, but are {list_samples_excluded_2}"


def test_filter_samples_by_protein_intensity_sum(filter_samples_df, show_figures):
    result_df1, method_output1 = by_protein_intensity_sum(
        filter_samples_df, deviation_threshold=1
    )
    result_df2, method_output2 = by_protein_intensity_sum(
        filter_samples_df, deviation_threshold=0.3
    )

    list_samples_excluded_1 = method_output1["filtered_samples"]
    list_samples_excluded_2 = method_output2["filtered_samples"]

    fig = by_protein_intensity_sum_plot(
        filter_samples_df, result_df1, method_output1, "Pie chart"
    )[0]
    if show_figures:
        fig.show()

    assert list_samples_excluded_1 == [
        "Sample3"
    ], f"excluded samples do not match \
            Sample3, but are {list_samples_excluded_1}"

    assert list_samples_excluded_2 == [
        "Sample2",
        "Sample3",
    ], f"excluded samples do not match \
            Sample2 and Sample3, but are {list_samples_excluded_2}"
