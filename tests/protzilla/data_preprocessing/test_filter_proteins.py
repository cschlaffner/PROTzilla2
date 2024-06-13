import numpy as np
import pandas as pd
import pytest

from protzilla.data_preprocessing.filter_proteins import (
    by_samples_missing,
    by_samples_missing_plot,
)
from tests.protzilla.data_preprocessing.test_peptide_preprocessing import (
    assert_peptide_filtering_matches_protein_filtering,
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


def test_filter_proteins_by_missing_samples(
    filter_proteins_by_samples_missing_df, peptides_df, show_figures
):
    method_output = by_samples_missing(
        filter_proteins_by_samples_missing_df, peptide_df=None, percentage=1.0
    )

    fig = by_samples_missing_plot(filter_proteins_df, method_output, "Pie chart")[0]
    if show_figures:
        fig.show()
    assert method_output["filtered_proteins"] == [
        "Protein2",
        "Protein3",
        "Protein4",
        "Protein5",
    ]

    assert_peptide_filtering_matches_protein_filtering(
        method_output["protein_df"],
        None,
        method_output["peptide_df"],
        "Protein ID",
    )

    method_output = by_samples_missing(
        filter_proteins_by_samples_missing_df, None, percentage=0.5
    )
    method_output["filtered_proteins"]

    assert method_output["filtered_proteins"] == ["Protein4", "Protein5"]

    method_output = by_samples_missing(
        filter_proteins_by_samples_missing_df, peptides_df, percentage=0.0
    )
    method_output["filtered_proteins"]

    assert method_output["filtered_proteins"] == []

    assert_peptide_filtering_matches_protein_filtering(
        method_output["protein_df"],
        peptides_df,
        method_output["peptide_df"],
        "Protein ID",
    )
