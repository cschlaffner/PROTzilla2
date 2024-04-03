import numpy as np
import pandas as pd
import pytest

from protzilla.data_preprocessing.filter_proteins import (
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
def filter_proteins_by_samples_missing_df():
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


@pytest.fixture
def filter_peptides_df():
    df = pd.DataFrame(
        (
            ["Sample1", "Protein1", "Gene1", "Peptide1", 1],
            ["Sample1", "Protein2", "Gene1", "Peptide2", 1],
            ["Sample1", "Protein2", "Gene1", "Peptide3", 1],
            ["Sample1", "Protein2", "Gene1", "Peptide4", 1],
            ["Sample1", "Protein3", "Gene1", "Peptide5", 1],
            ["Sample1", "Protein3", "Gene1", "Peptide6", 1],
            ["Sample1", "Protein3", "Gene1", "Peptide7", 1],
            ["Sample1", "Protein4", "Gene1", "Peptide8", 1],
            ["Sample1", "Protein5", "Gene1", "Peptide9", 1],
            ["Sample2", "Protein1", "Gene1", "Peptide10", 1],
            ["Sample2", "Protein2", "Gene1", "Peptide11", 1],
            ["Sample2", "Protein3", "Gene1", "Peptide12", 1],
            ["Sample2", "Protein4", "Gene1", "Peptide13", 1],
            ["Sample2", "Protein5", "Gene1", "Peptide14", 1],
            ["Sample3", "Protein1", "Gene1", "Peptide15", 1],
            ["Sample3", "Protein2", "Gene1", "Peptide16", 1],
            ["Sample3", "Protein3", "Gene1", "Peptide17", 1],
            ["Sample3", "Protein4", "Gene1", "Peptide18", 1],
            ["Sample3", "Protein5", "Gene1", "Peptide19", 1],
            ["Sample4", "Protein1", "Gene1", "Peptide20", 1],
            ["Sample4", "Protein2", "Gene1", "Peptide21", 1],
            ["Sample4", "Protein3", "Gene1", "Peptide22", 1],
            ["Sample4", "Protein4", "Gene1", "Peptide23", 1],
        ),
        columns=["Sample", "Protein ID", "Gene", "Peptide", "Intensity"],
    )

    return df


def test_filter_proteins_by_missing_samples(
    filter_proteins_by_samples_missing_df, show_figures
):
    result_df, _, method_output = by_samples_missing(
        filter_proteins_by_samples_missing_df, percentage=1.0
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

    result_df, _, method_output = by_samples_missing(
        filter_proteins_by_samples_missing_df, percentage=0.5
    )
    method_output["filtered_proteins"]

    assert method_output["filtered_proteins"] == ["Protein4", "Protein5"]

    result_df, _, method_output = by_samples_missing(
        filter_proteins_by_samples_missing_df, percentage=0.0
    )
    method_output["filtered_proteins"]

    assert method_output["filtered_proteins"] == []


def test_proteins_by_missing_samples_with_peptides(
        filter_proteins_df, filter_peptides_df, show_figures
):
    result_df, result_peptide_df, method_output = by_samples_missing(
        filter_proteins_df, percentage=1.0
    )

    assert result_peptide_df is None

    result_df, result_peptide_df, method_output = by_samples_missing(
        filter_proteins_df, filter_peptides_df, percentage=1.0
    )

    assert result_peptide_df is not None
    assert (
        not result_peptide_df["Protein ID"]
        .isin(method_output["filtered_proteins"])
        .any()
    )
