import numpy as np
import pandas as pd
import pytest

from protzilla.data_preprocessing.normalisation import (
    by_median,
    by_median_plot,
    by_reference_protein,
    by_reference_protein_plot,
    by_totalsum,
    by_totalsum_plot,
)


@pytest.fixture
def normalisation_df():
    normalisation_df = pd.DataFrame(
        data=(
            ["Sample_1", "Gene_1", 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ["Sample_2", "Gene_2", 1, 2, 3, 4, 5, 6, 7, 8, 9],
            ["Sample_3", "Gene_3", 30, 30, 40, 20, 0, 60, 40, 20, 0],
            ["Sample_4", "Gene_4", 0, 0, 0, 1, 20, 10, 0, 20, 0],
        ),
        columns=[
            "Sample",
            "Gene",
            "Protein_1",
            "Protein_2",
            "Protein_3",
            "Protein_4",
            "Protein_5",
            "Protein_6",
            "Protein_7",
            "Protein_8",
            "Protein_9",
        ],
    )

    return pd.melt(
        normalisation_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )


@pytest.fixture
def normalisation_by_ref_protein_df():
    intensity_df = pd.DataFrame(
        data=(
            ["Sample_1", "Gene_1", 0, 0, 30],
            ["Sample_2", "Gene_2", 10, 2, 3],
            ["Sample_3", "Gene_3", 30, 30, 90],
            ["Sample_4", "Gene_4", np.nan, 0, 0],
        ),
        columns=[
            "Sample",
            "Gene",
            "XCV993;ABC32;BBD55;AB9393",
            "MNSZ9",
            "G99490;ABC321",
        ],
    )
    return pd.melt(
        intensity_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )


@pytest.fixture
def expected_df_by_median_normalisation():
    expected_df = pd.DataFrame(
        data=(
            ["Sample_1", "Gene_1", 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [
                "Sample_2",
                "Gene_2",
                0.200,
                0.400,
                0.600,
                0.800,
                1.000,
                1.200,
                1.400,
                1.600,
                1.800,
            ],
            [
                "Sample_3",
                "Gene_3",
                1.000,
                1.000,
                1.333,
                0.667,
                0.000,
                2.000,
                1.333,
                0.667,
                0.000,
            ],
            [
                "Sample_4",
                "Gene_4",
                0.000,
                0.000,
                0.000,
                0.000,
                0.000,
                0.000,
                0.000,
                0.000,
                0.000,
            ],
        ),
        columns=[
            "Sample",
            "Gene",
            "Protein_1",
            "Protein_2",
            "Protein_3",
            "Protein_4",
            "Protein_5",
            "Protein_6",
            "Protein_7",
            "Protein_8",
            "Protein_9",
        ],
    )
    return pd.melt(
        expected_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Normalised Intensity",
    ).sort_values(by=["Sample", "Protein ID"], ignore_index=True)


@pytest.fixture
def expected_df_by_totalsum_normalisation():
    expected_df = pd.DataFrame(
        data=(
            ["Sample_1", "Gene_1", 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [
                "Sample_2",
                "Gene_2",
                0.022,
                0.044,
                0.067,
                0.089,
                0.111,
                0.133,
                0.156,
                0.178,
                0.200,
            ],
            [
                "Sample_3",
                "Gene_3",
                0.125,
                0.125,
                0.167,
                0.083,
                0.000,
                0.250,
                0.167,
                0.083,
                0.000,
            ],
            [
                "Sample_4",
                "Gene_4",
                0.000,
                0.000,
                0.000,
                0.020,
                0.392,
                0.196,
                0.000,
                0.392,
                0.000,
            ],
        ),
        columns=[
            "Sample",
            "Gene",
            "Protein_1",
            "Protein_2",
            "Protein_3",
            "Protein_4",
            "Protein_5",
            "Protein_6",
            "Protein_7",
            "Protein_8",
            "Protein_9",
        ],
    )
    return pd.melt(
        expected_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Normalised Intensity",
    ).sort_values(by=["Sample", "Protein ID"], ignore_index=True)


@pytest.fixture
def expected_df_by_ref_protein_normalisation():
    expected_df = pd.DataFrame(
        data=(
            ["Sample_2", "Gene_2", 1, 0.2, 0.3],
            ["Sample_3", "Gene_3", 1, 1, 3],
        ),
        columns=[
            "Sample",
            "Gene",
            "XCV993;ABC32;BBD55;AB9393",
            "MNSZ9",
            "G99490;ABC321",
        ],
    )

    return (
        pd.melt(
            expected_df,
            id_vars=["Sample", "Gene"],
            var_name="Protein ID",
            value_name="Normalised Intensity",
        ).sort_values(by=["Sample", "Protein ID"], ignore_index=True),
        dict(dropped_samples=["Sample_1", "Sample_4"]),
    )


def test_normalisation_by_median(
    normalisation_df, expected_df_by_median_normalisation, show_figures
):
    result_df, dropouts = by_median(normalisation_df)

    if show_figures:
        fig = by_median_plot(
            normalisation_df, result_df, dropouts, "Boxplot", "Sample"
        )[0]
        fig.show()

    assert result_df.round(3).equals(
        expected_df_by_median_normalisation
    ), f"median normalisation does not match! Median normalisation should be \
            \n{expected_df_by_median_normalisation}\nbut is\n{result_df}"


def test_totalsum_normalisation(
    normalisation_df, expected_df_by_totalsum_normalisation, show_figures
):
    result_df, dropouts = by_totalsum(normalisation_df)

    if show_figures:
        fig = by_totalsum_plot(
            normalisation_df, result_df, dropouts, "Boxplot", "Sample"
        )[0]
        fig.show()

    assert result_df.round(3).equals(
        expected_df_by_totalsum_normalisation
    ), f"Total normalisation does not match! Total sum normalisation should be\
            \n{expected_df_by_totalsum_normalisation}\n but is \n{result_df}"


def test_ref_protein_normalisation(
    normalisation_by_ref_protein_df,
    expected_df_by_ref_protein_normalisation,
    show_figures,
):
    expected_df = expected_df_by_ref_protein_normalisation[0]
    expected_dropped_samples = expected_df_by_ref_protein_normalisation[1]

    (result_df, dropouts) = by_reference_protein(
        normalisation_by_ref_protein_df, "ABC32"
    )

    if show_figures:
        fig = by_reference_protein_plot(
            normalisation_by_ref_protein_df, result_df, dropouts, "Boxplot", "Sample"
        )[0]
        fig.show()

    result_df_sorted = result_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True
    )
    assert result_df_sorted.round(3).equals(
        expected_df
    ), "reference protein normalisation does not match!"
    assert expected_dropped_samples["dropped_samples"] == dropouts["dropped_samples"]


def test_ref_protein_missing(capsys, normalisation_by_ref_protein_df):
    by_reference_protein(normalisation_by_ref_protein_df, "non_existing_Protein")
    out, err = capsys.readouterr()
    assert "The protein was not found" in out
