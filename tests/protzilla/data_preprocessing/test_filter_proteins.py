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
            ["Sample4", "Protein1", "SEQT", 20000000, 0.0002],
            ["Sample4", "Protein2", "SEQU", 21000000, 0.00021],
            ["Sample4", "Protein3", "SEQV", 22000000, 0.00022],
            ["Sample4", "Protein4", "SEQW", 23000000, 0.00023],
        ),
        columns=["Sample", "Protein ID", "Sequence", "Intensity", "PEP"],
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
    filter_proteins_df, peptides_df, show_figures
):
    result_df, result_peptide_df, method_output = by_samples_missing(
        filter_proteins_df, percentage=1.0
    )

    assert result_peptide_df is None

    result_df, result_peptide_df, method_output = by_samples_missing(
        filter_proteins_df, peptides_df, percentage=1.0
    )

    assert result_peptide_df is not None
    assert (
        not result_peptide_df["Protein ID"]
        .isin(method_output["filtered_proteins"])
        .any()
    )
