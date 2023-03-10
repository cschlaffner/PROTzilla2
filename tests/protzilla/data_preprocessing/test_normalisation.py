import pandas as pd
import numpy as np
import pytest

from protzilla.data_preprocessing.normalisation import *


@pytest.fixture
def test_intensity_df():
    test_intensity_df = pd.DataFrame(
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
        ]
    )

    return pd.melt(
        test_intensity_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )


@pytest.fixture
def expected_result_df_by_median_normalisation():
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
        ]
    )
    return pd.melt(
        expected_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Normalised Intensity",
    ).sort_values(by=["Sample", "Protein ID"], ignore_index=True)


@pytest.fixture
def expected_result_df_by_totalsum_normalisation():
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
        ]
    )
    return pd.melt(
        expected_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Normalised Intensity",
    ).sort_values(by=["Sample", "Protein ID"], ignore_index=True)


@pytest.fixture
def test_intensity_df_by_ref_protein_normalisation():
    return pd.DataFrame(
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
        ]
    )


@pytest.fixture
def expected_result_by_ref_protein_normalisation():
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
        ]
    )

    return (
        pd.melt(
            expected_df,
            id_vars=["Sample", "Gene"],
            var_name="Protein ID",
            value_name="Normalised Intensity",
        ).sort_values(by=["Sample", "Protein ID"], ignore_index=True)
        , pd.DataFrame(
            ["Sample_1", "Sample_4"], columns=["Dropped Samples"]
        )
    )


def test_normalisation_by_median(
        test_intensity_df,
        expected_result_df_by_median_normalisation,
        show_figures=True
):
    result_df, dropouts = by_median(test_intensity_df)

    if show_figures:
        fig = by_median_plot(
           test_intensity_df, result_df, dropouts, "box"
        )
        fig.show()

    assert result_df.round(3).equals(
        expected_result_df_by_median_normalisation
    ), f"median normalisation does not match! Median normalisation should be \
            \n{expected_result_df_by_median_normalisation}\nbut is\n{result_df}"


def test_totalsum_normalisation(
        test_intensity_df,
        expected_result_df_by_totalsum_normalisation,
        show_figures=True
):
    result_df, dropouts = by_totalsum(test_intensity_df)

    if show_figures:
        fig = by_totalsum_plot(
           test_intensity_df, result_df, dropouts, "box"
        )
        fig.show()

    assert result_df.round(3).equals(
        expected_result_df_by_totalsum_normalisation
    ), f"Total normalisation does not match! Total sum normalisation should be\
            \n{expected_result_df_by_totalsum_normalisation}\n but is \n{result_df}"


def test_ref_protein_normalisation(
        test_intensity_df_by_ref_protein_normalisation,
        expected_result_by_ref_protein_normalisation,
        show_figures=True
):
    expected_df = expected_result_by_ref_protein_normalisation[0]
    expected_dropped_samples = expected_result_by_ref_protein_normalisation[1]

    (
        result_df,
        dropouts
    ) = by_reference_protein(test_intensity_df_by_ref_protein_normalisation, "ABC32")

    if show_figures:
        fig = by_reference_protein_plot(
           test_intensity_df, result_df, dropouts, "box"
        )
        fig.show()

    result_df_sorted = result_df.sort_values(
        by=["Sample"], ignore_index=True
    )
    assert result_df_sorted.round(3).equals(
        expected_df
    ), "reference protein normalisation does not match!"
    pd.testing.assert_frame_equal(
        expected_dropped_samples, result_df_sorted
    )


def test_ref_protein_missing(capsys):
    intensities = (
        ["Sample_1", "Gene_1", 0, 0, 30],
        ["Sample_2", "Gene_2", 10, 2, 3],
        ["Sample_3", "Gene_3", 30, 30, 90],
        ["Sample_4", "Gene_4", np.nan, 0, 0],
    )
    columns = [
        "Sample",
        "Gene",
        "XCV993;ABC32;BBD55;AB9393",
        "MNSZ9",
        "G99490;ABC321",
    ]
    test_df = setup_test_df(intensities, columns)

    standardiser = RefProteinScalerScaling()
    standardiser.get_scaled_or_normalised_data(test_df, "non_existing_Protein")
    out, err = capsys.readouterr()
    assert "The protein was not found" in out


"""def test_z_score_normalisation(show_figures):

    # create test data frame
    test_transformed_df = setup_test_df(test_intensity_list, test_columns)

    # perform normalisation on test data frame
    standardiser = StandardScalerScaling()
    z_score_df = standardiser.get_scaled_or_normalised_data(
        test_transformed_df
    )

    if show_figures:
        Fig = standardiser.get_visualisation(
            intensity_df=test_transformed_df, group_by="Sample"
        )
        Fig.show()

    # create data frame with correct answers
    assertion_list = (
        ["Sample_1", "Gene_1", 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [
            "Sample_2",
            "Gene_2",
            -1.549,
            -1.162,
            -0.775,
            -0.387,
            0.000,
            0.387,
            0.775,
            1.162,
            1.549,
        ],
        [
            "Sample_3",
            "Gene_3",
            0.183,
            0.183,
            0.730,
            -0.365,
            -1.461,
            1.826,
            0.730,
            -0.365,
            -1.461,
        ],
        [
            "Sample_4",
            "Gene_4",
            -0.687,
            -0.687,
            -0.687,
            -0.566,
            1.738,
            0.525,
            -0.687,
            1.738,
            -0.687,
        ],
    )

    assertion_df = setup_assertion_df(assertion_list, test_columns)

    # compare calculated data frame with correct answers
    assert z_score_df.round(3).equals(
        assertion_df
    ), f"z scores do not match! Z scores should be \
            {assertion_df} but are {z_score_df}"
"""
