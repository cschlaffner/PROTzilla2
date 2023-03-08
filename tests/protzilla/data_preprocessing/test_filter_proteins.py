import pandas as pd
import numpy as np
from protzilla.data_preprocessing.filter_proteins import by_low_frequency


def test_filter_proteins_by_low_frequency():

    test_intensity_list = (
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
    )

    test_intensity_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    test_intensity_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True, inplace=True
    )

    results = by_low_frequency(test_intensity_df, "bar", threshold=0.6)
    list_proteins_excluded = results[2]["filtered_proteins"]
    fig = results[1][0]
    fig.show()

    assert [
        "Protein1",
        "Protein4",
    ] == list_proteins_excluded, f"excluded proteins do not match \
            Protein1 and Protein4, but are {list_proteins_excluded}"