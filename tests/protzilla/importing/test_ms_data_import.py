from protzilla.constants.paths import PROJECT_PATH
from protzilla.importing import ms_data_import
import pandas as pd


def test_ms_quant_import():
    intensity_names = [
        "Intensity",
        "MaxLFQ Total Intensity",
        "MaxLFQ Intensity",
        "Total Intensity",
        "MaxLFQ Unique Intensity",
        "Unique Spectral Count",
        "Unique Intensity",
        "Spectral Count",
        "Total Spectral Count",
    ]
    raw_df = pd.read_csv(
        f"{PROJECT_PATH}/tests/combined_protein_method_small_cut.tsv",
        sep="\t",
        low_memory=False,
        na_values=["", 0],
        keep_default_na=True,
    )

    for intensity_name in intensity_names:
        intensity_df, _ = ms_data_import.ms_fragger_import(
            _=None,
            file_path=f"{PROJECT_PATH}/tests/combined_protein_method_small_cut.tsv",
            intensity_name=intensity_name,
        )
        samples = intensity_df["Sample"].unique().tolist()
        for sample in samples:
            intensity_name_raw_df = sample + " " + intensity_name
            left = raw_df[["Protein ID", intensity_name_raw_df]]
            left.sort_values(by=["Protein ID"], ignore_index=True, inplace=True)
            left = left[[intensity_name_raw_df]]

            right = intensity_df.loc[intensity_df["Sample"] == sample, [intensity_name]]

            left.equals(right)
