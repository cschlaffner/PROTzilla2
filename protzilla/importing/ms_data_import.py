from pathlib import Path

import numpy as np
import pandas as pd
import re
from django.contrib import messages
from collections import defaultdict

from protzilla.utilities import clean_uniprot_id
from protzilla.data_integration.database_query import biomart_query


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
    df["Protein IDs"] = map_groups_to_uniprot(df["Protein IDs"].tolist())
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

    df = pd.concat([id_df, intensity_df], axis=1)
    # sum intensities if id appears multiple times
    df = df.groupby(["Protein IDs"]).sum(numeric_only=True).reset_index()

    molten = pd.melt(
        df,
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
    group = filter(valid_uniprot_id, set(protein_group.split(";")))
    return ";".join(sorted(group, key=isoforms_together))


def map_ids(extracted_ids):
    id_to_uniprot = defaultdict(list)
    all_count = 0
    for identifier, matching_ids in extracted_ids.items():
        # print(" ".join(matching_ids))
        all_count += len(matching_ids)
        if not matching_ids:
            continue
        result = list(
            biomart_query(
                matching_ids,
                identifier,
                [identifier, "uniprotswissprot"],
            )
        )
        for query, swiss in result:
            if swiss:
                id_to_uniprot[query].append(swiss)
        left = matching_ids - set(id_to_uniprot.keys())
        # uniprotswissprot and uniprotsptrembl are non overlapping, so no problem
        result = list(
            biomart_query(
                left,
                identifier,
                [identifier, "uniprotsptrembl"],
            )
        )
        for query, trembl in result:
            if trembl:
                id_to_uniprot[query].append(trembl)
    print(len(id_to_uniprot), all_count)
    return dict(id_to_uniprot)


def map_groups_to_uniprot(protein_groups):
    regex = {
        "ensembl_peptide_id": re.compile(r"^ENSP\d{11}"),
        "refseq_peptide": re.compile(r"^NP_\d{6,}"),
        "refseq_peptide_predicted": re.compile(r"^XP_\d{9}"),
    }

    # go through groups, find protein ids
    extracted_ids = {k: set() for k in regex.keys()}
    found_ids = []
    for group in protein_groups:
        found_in_group = set()
        for protein_id in group.split(";"):
            for identifier, pattern in regex.items():
                if match := pattern.search(protein_id):
                    found_id = match.group(0)
                    extracted_ids[identifier].add(found_id)
                    found_in_group.add(found_id)
                    break  # can only match one regex
        found_ids.append(found_in_group)
    id_to_uniprot = map_ids(extracted_ids)
    new_groups = []
    for found in found_ids:
        all_ids_of_group = set()
        for old_id in found:
            # check if uniprot?
            new_ids = id_to_uniprot.get(old_id, [])
            all_ids_of_group.update(new_ids)
        new_groups.append(";".join(all_ids_of_group))
    return new_groups


if __name__ == "__main__":
    df, _ = max_quant_import(
        None,
        "/Users/fynnkroeger/Desktop/Studium/Bachelorprojekt/inputs/not-uniprot-maxquant.txt",
        "Intensity",
    )

    df.to_csv("out.csv")
