import logging
from pathlib import Path

import pandas as pd

from protzilla.importing.ms_data_import import clean_protein_groups


def peptide_import(file_path, intensity_name, map_to_uniprot) -> dict:
    try:
        assert intensity_name in [
            "Intensity",
            "iBAQ",
            "LFQ intensity",
        ], f"Unknown intensity name: {intensity_name}"
        assert Path(file_path).is_file(), f"Cannot find Peptide File at {file_path}"
    except AssertionError as e:
        return dict(
            messages=[dict(level=logging.ERROR, msg=e)],
        )

    # Intensity -> Intensity, iBAQ -> LFQ, LFQ -> LFQ
    peptide_intensity_name = (
        "LFQ intensity" if intensity_name == "iBAQ" else intensity_name
    )

    id_columns = ["Proteins", "Sequence", "Missed cleavages", "PEP"]
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
        value_name="Intensity",
    )

    molten = molten.rename(columns={"Proteins": "Protein ID"})
    ordered = molten[
        ["Sample", "Protein ID", "Sequence", "Intensity", "PEP"]
    ]
    ordered.dropna(subset=["Protein ID"], inplace=True)
    ordered.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)

    new_groups, filtered_proteins = clean_protein_groups(
        ordered["Protein ID"].tolist(), map_to_uniprot
    )
    cleaned = ordered.assign(**{"Protein ID": new_groups})

    return dict(peptide_df=cleaned)


def evidence_import(file_path, intensity_name, map_to_uniprot) -> dict:
    try:
        assert intensity_name in [
            "Intensity",
            "iBAQ",
            "LFQ intensity",
        ], f"Unknown intensity name: {intensity_name}"
        assert Path(file_path).is_file(), f"Cannot find Peptide File at {file_path}"
    except AssertionError as e:
        return dict(messages=[dict(level=logging.ERROR, msg=e)])

    # Intensity -> Intensity, iBAQ -> LFQ, LFQ -> LFQ
    peptide_intensity_name = (
        "LFQ intensity" if intensity_name == "iBAQ" else intensity_name
    )

    id_columns = [
        "Experiment",
        "Proteins",
        "Sequence",
        peptide_intensity_name,
        "Modifications",
        "Modified sequence",
        "Missed cleavages",
        "PEP",
        "Raw file",
    ]

    read = pd.read_csv(
        file_path,
        sep="\t",
        low_memory=False,
        na_values=["", 0],
        keep_default_na=True,
    )

    df = read[id_columns]

    df = df.rename(columns={"Proteins": "Protein ID"})
    df = df.rename(columns={"Experiment": "Sample"})

    df.dropna(subset=["Protein ID"], inplace=True)
    df.sort_values(
        by=["Sample", "Protein ID", "Sequence", "Modifications"],
        ignore_index=True,
        inplace=True,
    )

    new_groups, filtered_proteins = clean_protein_groups(
        df["Protein ID"].tolist(), map_to_uniprot
    )
    df = df.assign(**{"Protein ID": new_groups})

    return dict(peptide_df=df)
