import pytest
import pandas as pd
from protzilla.data_preprocessing.filter_samples import (
    by_protein_count,
    by_protein_intensity_sum,
    by_protein_count_plot,
    by_protein_intensity_sum_plot,
)


@pytest.fixture
def filter_samples_df():
    filter_samples_list = (
        ["Sample1", "Protein1", "Gene1", 1],
        ["Sample1", "Protein2", "Gene2", 2],
        ["Sample1", "Protein3", "Gene3", 3],
        ["Sample1", "Protein4", "Gene4", 4],
        ["Sample1", "Protein5", "Gene5", 5],
        [
            "Sample2",
            "Protein1",
            "Gene1",
        ],
        ["Sample2", "Protein2", "Gene2", 2],
        [
            "Sample2",
            "Protein3",
            "Gene3",
        ],
        ["Sample2", "Protein4", "Gene4", 5],
        [
            "Sample2",
            "Protein5",
            "Gene5",
        ],
        [
            "Sample3",
            "Protein1",
            "Gene1",
        ],
        [
            "Sample3",
            "Protein2",
            "Gene2",
        ],
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


def test_filter_samples_by_protein_count(filter_samples_df, show_figures):
    result_df1, dropouts1 = by_protein_count(filter_samples_df, threshold=0.3)
    result_df2, dropouts2 = by_protein_count(filter_samples_df, threshold=1)

    list_proteins_excluded_1 = dropouts1["filtered_samples"]
    list_proteins_excluded_2 = dropouts2["filtered_samples"]

    fig = by_protein_count_plot(filter_samples_df, result_df1, dropouts1, "Pie chart")[
        0
    ]
    if show_figures:
        fig.show()

    assert [
        "Sample1",
        "Sample2",
    ] == list_proteins_excluded_1, f"excluded proteins do not match \
            Protein1 and Protein4, but are {list_proteins_excluded_1}"

    assert [
        "Sample1",
    ] == list_proteins_excluded_2, f"excluded proteins do not match \
            Protein1 and Protein4, but are {list_proteins_excluded_2}"


def test_filter_samples_by_protein_intensity_sum(filter_samples_df, show_figures):
    result_df1, dropouts1 = by_protein_intensity_sum(filter_samples_df, threshold=1)
    result_df2, dropouts2 = by_protein_intensity_sum(filter_samples_df, threshold=0.3)

    list_proteins_excluded_1 = dropouts1["filtered_samples"]
    list_proteins_excluded_2 = dropouts2["filtered_samples"]

    fig = by_protein_intensity_sum_plot(
        filter_samples_df, result_df1, dropouts1, "Pie chart"
    )[0]
    if show_figures:
        fig.show()

    assert [
        "Sample3",
    ] == list_proteins_excluded_1, f"excluded proteins do not match \
            Protein1 and Protein4, but are {list_proteins_excluded_1}"

    assert [
        "Sample2",
        "Sample3",
    ] == list_proteins_excluded_2, f"excluded proteins do not match \
            Protein1 and Protein4, but are {list_proteins_excluded_2}"
