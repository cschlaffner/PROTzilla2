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
from tests.protzilla.data_preprocessing.test_peptide_preprocessing import (
    assert_peptide_filtering_matches_protein_filtering,
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
        ["Sample4", "Protein1", "Gene1", 0],
        ["Sample4", "Protein2", "Gene2"],
        ["Sample4", "Protein3", "Gene3"],
        ["Sample4", "Protein4", "Gene4"],
        ["Sample4", "Protein5", "Gene5"],
    )

    filter_samples_df = pd.DataFrame(
        data=filter_samples_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    filter_samples_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True, inplace=True
    )

    return filter_samples_df


def test_by_proteins_missing(filter_samples_df, show_figures, peptides_df):
    method_input1 = {
        "protein_df": filter_samples_df,
        "peptide_df": None,
        "percentage": 0.5,
    }
    method_output1 = by_proteins_missing(**method_input1)
    method_input2 = {
        "protein_df": filter_samples_df,
        "peptide_df": peptides_df,
        "percentage": 0.6,
    }
    method_output2 = by_proteins_missing(**method_input2)
    method_input3 = {
        "protein_df": filter_samples_df,
        "peptide_df": None,
        "percentage": 0.65,
    }
    method_output3 = by_proteins_missing(**method_input3)

    list_samples_excluded_1 = method_output1["filtered_samples"]
    list_samples_excluded_2 = method_output2["filtered_samples"]
    list_samples_excluded_3 = method_output3["filtered_samples"]

    fig = by_proteins_missing_plot(method_input1, method_output1, "Pie chart")[0]
    if show_figures:
        fig.show()

    assert list_samples_excluded_1 == [
        "Sample2",
        "Sample4",
    ], f"excluded samples do not match \
                Sample2 and Sample4, but are {list_samples_excluded_1}"

    assert list_samples_excluded_2 == [
        "Sample2",
        "Sample4",
    ], f"excluded samples do not match \
                Sample2 and Sample4, but are {list_samples_excluded_2}"
    assert list_samples_excluded_3 == [
        "Sample2",
        "Sample3",
        "Sample4",
    ], f"excluded samples do not match \
                    Sample2, Sampel3 and Sample4, but are {list_samples_excluded_3}"

    assert_peptide_filtering_matches_protein_filtering(
        method_output1["protein_df"],
        None,
        method_output1["peptide_df"],
        "Sample",
    )
    assert_peptide_filtering_matches_protein_filtering(
        method_output2["protein_df"],
        peptides_df,
        method_output2["peptide_df"],
        "Sample",
    )


def test_filter_samples_by_protein_count(filter_samples_df, show_figures, peptides_df):
    method_input1 = {
        "protein_df": filter_samples_df,
        "peptide_df": None,
        "deviation_threshold": 0.3,
    }
    method_output1 = by_protein_count(**method_input1)
    method_input2 = {
        "protein_df": filter_samples_df,
        "peptide_df": peptides_df,
        "deviation_threshold": 1.0,
    }
    method_output2 = by_protein_count(**method_input2)

    list_samples_excluded_1 = method_output1["filtered_samples"]
    list_samples_excluded_2 = method_output2["filtered_samples"]

    fig = by_protein_count_plot(method_input1, method_output1, "Pie chart")[0]
    if show_figures:
        fig.show()

    fig = by_protein_count_plot(method_input1, method_output1, "Bar chart")[0]
    if show_figures:
        fig.show()

    assert list_samples_excluded_1 == [
        "Sample1",
        "Sample4",
    ], f"excluded samples do not match \
            Sample1 and Sample4, but are {list_samples_excluded_1}"

    assert list_samples_excluded_2 == [
        "Sample1",
    ], f"excluded samples do not match \
            Sample1, but are {list_samples_excluded_2}"

    assert_peptide_filtering_matches_protein_filtering(
        method_output1["protein_df"],
        None,
        method_output1["peptide_df"],
        "Sample",
    )
    assert_peptide_filtering_matches_protein_filtering(
        method_output2["protein_df"],
        peptides_df,
        method_output2["peptide_df"],
        "Sample",
    )


def test_filter_samples_by_protein_intensity_sum(
    filter_samples_df, show_figures, peptides_df
):
    method_input1 = {
        "protein_df": filter_samples_df,
        "peptide_df": None,
        "deviation_threshold": 1.0,
    }
    method_output1 = by_protein_intensity_sum(**method_input1)
    method_input2 = {
        "protein_df": filter_samples_df,
        "peptide_df": peptides_df,
        "deviation_threshold": 0.3,
    }
    method_output2 = by_protein_intensity_sum(**method_input2)

    list_samples_excluded_1 = method_output1["filtered_samples"]
    list_samples_excluded_2 = method_output2["filtered_samples"]

    fig = by_protein_intensity_sum_plot(method_input1, method_output1, "Pie chart")[0]
    if show_figures:
        fig.show()

    assert list_samples_excluded_1 == [
        "Sample3",
    ], f"excluded samples do not match \
            Sample3, but are {list_samples_excluded_1}"

    assert list_samples_excluded_2 == [
        "Sample3",
        "Sample4",
    ], f"excluded samples do not match \
            Sample2 and Sample3, but are {list_samples_excluded_2}"

    assert_peptide_filtering_matches_protein_filtering(
        method_output1["protein_df"],
        None,
        method_output1["peptide_df"],
        "Sample",
    )
    assert_peptide_filtering_matches_protein_filtering(
        method_output2["protein_df"],
        peptides_df,
        method_output2["peptide_df"],
        "Sample",
    )
