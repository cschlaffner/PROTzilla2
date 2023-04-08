import pytest

from protzilla.constants.paths import PROJECT_PATH
from protzilla.importing import ms_data_import
import pandas as pd


@pytest.fixture
def ms_fragger_raw_df():
    return pd.read_csv(
        f"{PROJECT_PATH}/tests/combined_protein_method_small_cut.tsv",
        sep="\t",
        low_memory=False,
        na_values=["", 0],
        keep_default_na=True,
    )


def intensity_values_for_sample_and_intensity(
    ms_fragger_raw_df, sample_name, intensity_name
):
    intensity_name_raw_df = sample_name + " " + intensity_name
    df = ms_fragger_raw_df[["Protein ID", intensity_name_raw_df]]
    df.sort_values(by=["Protein ID"], ignore_index=True, inplace=True)
    df = df[intensity_name_raw_df]
    return df


@pytest.mark.parametrize(
    "intensity_name",
    [
        "Intensity",
        "MaxLFQ Total Intensity",
        "MaxLFQ Intensity",
        "Total Intensity",
        "MaxLFQ Unique Intensity",
        "Unique Spectral Count",
        "Unique Intensity",
        "Spectral Count",
        "Total Spectral Count",
    ],
)
def test_ms_fragger_import(ms_fragger_raw_df, intensity_name):
    intensity_df, _ = ms_data_import.ms_fragger_import(
        _=None,
        file_path=f"{PROJECT_PATH}/tests/combined_protein_method_small_cut.tsv",
        intensity_name=intensity_name,
    )

    samples = intensity_df["Sample"].unique().tolist()
    for sample in samples:
        left = intensity_values_for_sample_and_intensity(
            ms_fragger_raw_df, sample, intensity_name
        )

        right = intensity_df.loc[intensity_df["Sample"] == sample, intensity_name]

        pd.testing.assert_series_equal(
            left, right, check_index=False, check_names=False, check_dtype=False
        )
