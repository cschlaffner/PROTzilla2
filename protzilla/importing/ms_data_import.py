from pathlib import Path

import numpy as np
import pandas as pd
from django.contrib import messages

from protzilla.utilities import clean_uniprot_id


def max_quant_import(_, file_path, intensity_name):
    assert intensity_name in ["Intensity", "iBAQ", "LFQ intensity"]
    if not Path(file_path).is_file():
        msg = "The file upload is empty. Please provide a Max Quant file."
        return None, dict(
            messages=[dict(level=messages.ERROR, msg=msg)],
        )
    selected_columns = ["Protein IDs", "Gene names"]
    read = pd.read_csv(
        file_path,
        sep="\t",
        low_memory=False,
        na_values=["", 0],
        keep_default_na=True,
    )
    df = read.drop(columns=["Intensity", "iBAQ", "iBAQ peptides"], errors="ignore")
    df["Protein IDs"] = df["Protein IDs"].map(handle_protein_ids)
    df = df[df["Protein IDs"].map(bool)]  # remove rows without valid protein id
    if "Gene names" not in df.columns:  # genes column should be removed eventually
        df["Gene names"] = np.nan
    id_df = df[selected_columns]
    intensity_df = df.filter(regex=f"^{intensity_name} ", axis=1)

    if intensity_df.empty:
        msg = f"{intensity_name} was not found in the provided file, please use another intensity and try again"
        return None, dict(
            messages=[dict(level=messages.ERROR, msg=msg)],
        )

    intensity_df.columns = [c[len(intensity_name) + 1 :] for c in intensity_df.columns]
    molten = pd.melt(
        pd.concat([id_df, intensity_df], axis=1),
        id_vars=selected_columns,
        var_name="Sample",
        value_name=intensity_name,
    )
    molten = molten.rename(columns={"Protein IDs": "Protein ID", "Gene names": "Gene"})
    ordered = molten[["Sample", "Protein ID", "Gene", intensity_name]]
    ordered.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)
    return ordered, {}


def ms_fragger_import(_, file_path, intensity_name):
    assert intensity_name in [
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
    if not Path(file_path).is_file():
        msg = "The file upload is empty. Please provide a MS Fragger file."
        return None, dict(
            messages=[dict(level=messages.ERROR, msg=msg)],
        )
    selected_columns = ["Protein ID", "Gene"]
    read = pd.read_csv(
        file_path,
        sep="\t",
        low_memory=False,
        na_values=["", 0],
        keep_default_na=True,
    )
    df = read.drop(
        columns=[
            "Combined Spectral Count",
            "Combined Unique Spectral Count",
            "Combined Total Spectral Count",
        ]
    )
    df["Protein ID"] = df["Protein ID"].map(handle_protein_ids)
    df = df[df["Protein ID"].map(bool)]  # remove rows without valid protein id
    id_df = df[selected_columns]
    intensity_df = df.filter(regex=f"{intensity_name}$", axis=1)
    intensity_df.columns = [
        c[: -(len(intensity_name) + 1)] for c in intensity_df.columns
    ]
    intensity_df = intensity_df.drop(
        columns=intensity_df.filter(
            regex="MaxLFQ Total$|MaxLFQ$|Total$|MaxLFQ Unique$|Unique$", axis=1
        ).columns
    )
    molten = pd.melt(
        pd.concat([id_df, intensity_df], axis=1),
        id_vars=selected_columns,
        var_name="Sample",
        value_name=intensity_name,
    )
    ordered = molten[["Sample", "Protein ID", "Gene", intensity_name]]
    ordered.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)
    return ordered, {}


def valid_uniprot_id(uniprot_id):
    return not uniprot_id.startswith("CON__") and not uniprot_id.startswith("REV__")


def isoforms_together(protein_id):
    # put isofroms together, and the non-isofrom version first
    clean = clean_uniprot_id(protein_id)
    return clean, clean != protein_id, protein_id


def handle_protein_ids(protein_group):
    # todo add mapping to uniprot here
    group = filter(valid_uniprot_id, protein_group.split(";"))
    return ";".join(sorted(group, key=isoforms_together))
