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


@pytest.fixture
def peptides_df():
    df = pd.DataFrame(
        (
            ["Sample1", "Protein1", "SEQA", 1000000, 0.00001],
            ["Sample1", "Protein2", "SEQB", 2000000, 0.00002],
            ["Sample1", "Protein2", "SEQC", 3000000, 0.00003],
            ["Sample1", "Protein2", "SEQD", 4000000, 0.00004],
            ["Sample1", "Protein3", "SEQE", 5000000, 0.00005],
            ["Sample1", "Protein3", "SEQF", 6000000, 0.00006],
            ["Sample1", "Protein3", "SEQG", 7000000, 0.00007],
            ["Sample1", "Protein4", "SEQH", 8000000, 0.00008],
            ["Sample1", "Protein5", "SEQI", 9000000, 0.00009],
            ["Sample2", "Protein1", "SEQJ", 10000000, 0.0001],
            ["Sample2", "Protein2", "SEQK", 11000000, 0.00011],
            ["Sample2", "Protein3", "SEQL", 12000000, 0.00012],
            ["Sample2", "Protein4", "SEQM", 13000000, 0.00013],
            ["Sample2", "Protein5", "SEQN", 14000000, 0.00014],
            ["Sample3", "Protein1", "SEQO", 15000000, 0.00015],
            ["Sample3", "Protein2", "SEQP", 16000000, 0.00016],
            ["Sample3", "Protein3", "SEQQ", 17000000, 0.00017],
            ["Sample3", "Protein4", "SEQR", 18000000, 0.00018],
            ["Sample3", "Protein5", "SEQS", 19000000, 0.00019],
        ),
        columns=["Sample", "Protein ID", "Sequence", "Intensity", "PEP"],
    )

    return df


def test_by_proteins_missing(filter_samples_df, show_figures):
    result_df1, _, method_output1 = by_proteins_missing(
        filter_samples_df, percentage=0.5
    )
    result_df2, _, method_output2 = by_proteins_missing(
        filter_samples_df, percentage=0.6
    )
    result_df3, _, method_output3 = by_proteins_missing(
        filter_samples_df, percentage=0.65
    )

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
    result_df1, _, method_output1 = by_protein_count(
        filter_samples_df, deviation_threshold=0.3
    )
    result_df2, _, method_output2 = by_protein_count(
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
    result_df1, _, method_output1 = by_protein_intensity_sum(
        filter_samples_df, deviation_threshold=1
    )
    result_df2, _, method_output2 = by_protein_intensity_sum(
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


@pytest.mark.parametrize(
    "filtering_method",
    [by_protein_intensity_sum, by_protein_count, by_proteins_missing],
)
def test_peptide_filtering(filtering_method, filter_samples_df, peptides_df):
    result_df1, result_peptide_df1, method_output1 = filtering_method(
        filter_samples_df, None, 0.5
    )
    result_df2, result_peptide_df2, method_output2 = filtering_method(
        filter_samples_df, peptides_df, 0.5
    )

    assert (
        result_peptide_df1 is None
    ), "Output peptide dataframe should be None, if no input peptide dataframe is provided"
    assert (
        result_peptide_df2 is not None
    ), "Peptide dataframe should not be None, if an input peptide dataframe is provided"
    assert (
        result_peptide_df2["Sample"].isin(result_df2["Sample"]).all()
    ), "Peptide dataframe should only contain samples that are in the filtered dataframe"
    assert (
        peptides_df[peptides_df["Sample"].isin(result_df2["Sample"])]
        .isin(result_peptide_df2)
        .all()
        .all()
    ), "Peptide dataframe should contain all entry's on samples that are in the filtered dataframe"
