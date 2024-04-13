import logging
from pathlib import Path

import pandas as pd


def peptide_import(file_path, intensity_name) -> dict:
    try:
        assert intensity_name in [
            "Intensity",
            "iBAQ",
            "LFQ intensity",
        ], f"Unknown intensity name: {intensity_name}"
        assert Path(file_path).is_file(), f"Cannot find Peptide File at {file_path}"
    except AssertionError as e:
        return dict(
            peptide_df=None,
            messages=[dict(level=logging.ERROR, msg=e)],
        )

    # Intensity -> Intensity, iBAQ -> LFQ, LFQ -> LFQ
    peptide_intensity_name = (
        "LFQ intensity" if intensity_name == "iBAQ" else intensity_name
    )

    id_columns = ["Proteins", "Sequence", "PEP"]
    read = pd.read_csv(
        file_path,
        sep="\t",
        low_memory=False,
        na_values=["", 0],
        keep_default_na=True,
    )

    df = read.drop(columns=["Intensity"])
    id_df = df[id_columns]
    intensity_df = df.filter(regex=f"^{peptide_intensity_name} ", axis=1)
    intensity_df.columns = [
        c[len(peptide_intensity_name) + 1 :] for c in intensity_df.columns
    ]
    molten = pd.melt(
        pd.concat([id_df, intensity_df], axis=1),
        id_vars=id_columns,
        var_name="Sample",
        value_name=peptide_intensity_name,
    )

    molten = molten.rename(columns={"Proteins": "Protein ID"})
    ordered = molten[
        ["Sample", "Protein ID", "Sequence", peptide_intensity_name, "PEP"]
    ]
    ordered.dropna(subset=["Protein ID"], inplace=True)
    ordered.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)

    return dict(peptide_df=ordered)
