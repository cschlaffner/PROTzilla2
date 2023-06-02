import numpy as np
import pandas as pd
import pytest

from protzilla.data_preprocessing.filter_proteins import (
    by_low_frequency,
    by_low_frequency_plot,
    by_samples_missing,
    by_samples_missing_plot,
)


@pytest.fixture
def filter_proteins_df():
    filter_proteins_df = pd.DataFrame(
        (
            ["Sample2", "Protein2", "Gene2", 1],
            ["Sample4", "Protein4", "Gene4", 1],
            ["Sample1", "Protein1", "Gene1", np.nan],
            ["Sample3", "Protein3", "Gene3", 1],
            ["Sample1", "Protein2", "Gene2", 1],
            ["Sample1", "Protein3", "Gene3", 1],
            ["Sample2", "Protein1", "Gene1", np.nan],
            ["Sample2", "Protein3", "Gene3", 1],
            ["Sample3", "Protein1", "Gene1", np.nan],
            ["Sample3", "Protein2", "Gene2", 1],
            ["Sample4", "Protein2", "Gene2", np.nan],
            ["Sample4", "Protein3", "Gene3", 1],
            ["Sample1", "Protein4", "Gene4", np.nan],
            ["Sample2", "Protein4", "Gene4", 1],
            ["Sample3", "Protein4", "Gene4", np.nan],
            ["Sample4", "Protein1", "Gene1", 1],
        ),
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    filter_proteins_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True, inplace=True
    )

    return filter_proteins_df


@pytest.fixture
def filter_proteins_by_perentage_df():
    df = pd.DataFrame(
        (
            ["Sample1", "Protein1", "Gene1", 1],
            ["Sample1", "Protein2", "Gene1", np.nan],
            ["Sample1", "Protein3", "Gene1", np.nan],
            ["Sample1", "Protein4", "Gene1", np.nan],
            ["Sample1", "Protein5", "Gene1", np.nan],
            ["Sample2", "Protein1", "Gene1", 1],
            ["Sample2", "Protein2", "Gene1", 1],
            ["Sample2", "Protein3", "Gene1", np.nan],
            ["Sample2", "Protein4", "Gene1", np.nan],
            ["Sample2", "Protein5", "Gene1", np.nan],
            ["Sample3", "Protein1", "Gene1", 1],
            ["Sample3", "Protein2", "Gene1", 1],
            ["Sample3", "Protein3", "Gene1", 1],
            ["Sample3", "Protein4", "Gene1", np.nan],
            ["Sample3", "Protein5", "Gene1", np.nan],
            ["Sample4", "Protein1", "Gene1", 1],
            ["Sample4", "Protein2", "Gene1", 1],
            ["Sample4", "Protein3", "Gene1", 1],
            ["Sample4", "Protein4", "Gene1", 1],
            ["Sample4", "Protein5", "Gene1", np.nan],
        ),
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return df


def test_filter_proteins_by_low_frequency(filter_proteins_df, show_figures):
    result_df, dropouts = by_low_frequency(filter_proteins_df, threshold=0.6)
    list_proteins_excluded = dropouts["filtered_proteins"]

    fig = by_low_frequency_plot(filter_proteins_df, result_df, dropouts, "Pie chart")[0]
    if show_figures:
        fig.show()

    assert [
        "Protein1",
        "Protein4",
    ] == list_proteins_excluded, f"excluded proteins do not match \
            Protein1 and Protein4, but are {list_proteins_excluded}"


def test_filter_proteins_by_missing_samples(
    filter_proteins_by_perentage_df, show_figures
):
    result_df, method_output = by_samples_missing(
        filter_proteins_by_perentage_df, percentage=1.0
    )

    fig = by_samples_missing_plot(
        filter_proteins_df, result_df, method_output, "Pie chart"
    )[0]
    if show_figures:
        fig.show()
    assert method_output["filtered_proteins"] == [
        "Protein2",
        "Protein3",
        "Protein4",
        "Protein5",
    ]

    result_df, method_output = by_samples_missing(
        filter_proteins_by_perentage_df, percentage=0.5
    )
    method_output["filtered_proteins"]

    assert method_output["filtered_proteins"] == ["Protein4", "Protein5"]

    result_df, method_output = by_samples_missing(
        filter_proteins_by_perentage_df, percentage=0.0
    )
    method_output["filtered_proteins"]

    assert method_output["filtered_proteins"] == []
