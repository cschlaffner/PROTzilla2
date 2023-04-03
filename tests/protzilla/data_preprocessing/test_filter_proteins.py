import numpy as np
import pandas as pd
import pytest

from protzilla.data_preprocessing.filter_proteins import (
    by_low_frequency,
    by_low_frequency_plot,
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
