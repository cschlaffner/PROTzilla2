from pathlib import Path

import pandas as pd
from django.contrib import messages


def max_quant_import(_, file_path, intensity_name):
    assert intensity_name in ["Intensity", "iBAQ", "LFQ intensity"]
    if not Path(file_path).is_file():
        msg = "The file upload is empty. Please provide a Max Quant file."
        return None, dict(
            meta_df=None,
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
    df = read.drop(columns=["Intensity", "iBAQ", "iBAQ peptides"])
    id_df = df[selected_columns]
    intensity_df = df.filter(regex=f"^{intensity_name} ", axis=1)
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
    ordered["Protein ID"] = ordered["Protein ID"].map(handle_protein_ids)
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
            meta_df=None,
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
    ordered["Protein ID"] = ordered["Protein ID"].map(handle_protein_ids)
    return ordered, {}


def handle_protein_ids(protein_group):
    # todo add mapping to uniprot here
    def by_normalized_id(protein_id):
        return (clean := clean_uniprot_id(protein_id)), clean != protein_id

    return ";".join(sorted(protein_group.split(";"), key=by_normalized_id))


def clean_uniprot_id(uniprot_id):
    if "-" in uniprot_id:
        uniprot_id = uniprot_id.split("-")[0]
    if uniprot_id.startswith("CON__") or uniprot_id.startswith("REV__"):
        uniprot_id = uniprot_id[5:]
    if "_" in uniprot_id:
        uniprot_id = uniprot_id.split("_")[0]
    return uniprot_id
