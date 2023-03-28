import numpy as np
import pandas as pd
import pytest

from protzilla.utilities.transform_dfs import long_to_wide, wide_to_long


@pytest.fixture
def transform_df_wide():
    return pd.DataFrame(
        {
            "Protein_1": {"Sample_1": 1, "Sample_2": 6, "Sample_3": 11},
            "Protein_2": {"Sample_1": 2, "Sample_2": 7, "Sample_3": 12},
            "Protein_3": {"Sample_1": 3, "Sample_2": 8, "Sample_3": 13},
            "Protein_4": {"Sample_1": 4, "Sample_2": 9, "Sample_3": 14},
            "Protein_5": {"Sample_1": 5, "Sample_2": 10, "Sample_3": 15},
        }
    )


@pytest.fixture
def transform_df_long():
    df = pd.DataFrame(
        data=(
            ["Sample_1", "Gene_1", 1, 2, 3, 4, 5],
            ["Sample_2", "Gene_2", 6, 7, 8, 9, 10],
            ["Sample_3", "Gene_3", 11, 12, 13, 14, 15],
        ),
        columns=[
            "Sample",
            "Gene",
            "Protein_1",
            "Protein_2",
            "Protein_3",
            "Protein_4",
            "Protein_5",
        ],
    )

    df = pd.melt(
        df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )

    df.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)
    return df
    # return pd.melt(
    #     df,
    #     id_vars=["Sample", "Gene"],
    #     var_name="Protein ID",
    #     value_name="Intensity",
    # )


@pytest.fixture
def transform_df_long_invalid_data():
    df = pd.DataFrame(
        data=(
            ["Sample_1", "Gene_1", 0, 0, 0, 0, 0],
            ["Sample_2", "Gene_2", 0, 0, np.nan, 0, 0],
            ["Sample_3", "Gene_3", 0, 0, 0, 0, 0],
        ),
        columns=[
            "Sample",
            "Gene",
            "Protein_1",
            "Protein_2",
            "Protein_3",
            "Protein_4",
            "Protein_5",
        ],
    )

    return pd.melt(
        df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )


def test_transform_long_to_wide(transform_df_long, transform_df_wide):
    assert long_to_wide(transform_df_long).equals(transform_df_wide)


def test_transform_wide_to_long(
    transform_df_long, transform_df_wide, transform_df_long_invalid_data
):
    l2l = wide_to_long(long_to_wide(transform_df_long), transform_df_long)
    # l2l = wide_to_long(transform_df_wide, transform_df_long_invalid_data)

    print("\n\n")
    print("l2l info\n", l2l.info())
    print("\n\n")
    print("long info\n", transform_df_long.info())
    print("\n\n")
    print("l2l\n", l2l)
    print("\n\n")
    print("long\n", transform_df_long)
    print("\n\nconcat")
    print(
        pd.concat([transform_df_wide, long_to_wide(transform_df_long)]).drop_duplicates(
            keep=False
        )
    )
    print("\n\ncompare")

    # reicht das vielleicht einfach?
    print(l2l.compare(transform_df_long))

    assert l2l.equals(transform_df_long)
