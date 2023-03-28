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

    return pd.melt(
        df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )


@pytest.fixture
def transform_df_long_invalid_data():
    df = pd.DataFrame(
        data=(
            ["Sample_1", "Gene_1", 1, 2, 3, 4, 5], # TODO fill with 0s
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
    df = wide_to_long(long_to_wide(transform_df_long), transform_df_long)
    # df = wide_to_long(transform_df_wide, transform_df_long_invalid_data)
    print("\n\n")
    print(df.info())
    print("\n\n")
    print(transform_df_long.info())
    print("\n\n")
    print(df)
    print("\n\n")
    print(transform_df_long)
    print("\n\nconcat")
    print(pd.concat([transform_df_wide, transform_df_long]).drop_duplicates(keep=False))
    print("\n\ncompare")

    # reicht das vielleicht einfach?
    print(df.compare(transform_df_long))


    assert df.equals(transform_df_wide)
