import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from django.contrib import messages

from protzilla.data_integration.database_query import biomart_query


def max_quant_import(_, file_path, intensity_name, map_to_uniprot=False):
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
    if "Gene names" not in df.columns:  # genes column should be removed eventually
        df["Gene names"] = np.nan
    id_df = df[selected_columns]
    id_df = id_df.rename(columns={"Protein IDs": "Protein ID", "Gene names": "Gene"})
    intensity_df = df.filter(regex=f"^{intensity_name} ", axis=1)

    if intensity_df.empty:
        msg = f"{intensity_name} was not found in the provided file, please use another intensity and try again"
        return None, dict(
            messages=[dict(level=messages.ERROR, msg=msg)],
        )
    intensity_df.columns = [c[len(intensity_name) + 1 :] for c in intensity_df.columns]

    df = pd.concat([id_df, intensity_df], axis=1)
    return transform_and_clean(df, intensity_name, map_to_uniprot)


def ms_fragger_import(_, file_path, intensity_name, map_to_uniprot=False):
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
    df = pd.concat([id_df, intensity_df], axis=1)
    return transform_and_clean(df, intensity_name, map_to_uniprot)


def transform_and_clean(df, intensity_name, map_to_uniprot):
    contaminant_groups_mask = df["Protein ID"].map(
        lambda group: any(id_.startswith("CON__") for id_ in group.split(";"))
    )
    contaminants = df[contaminant_groups_mask].reset_index(drop=True)
    df = df[~contaminant_groups_mask]

    # REV__ and XXX__ proteins get removed here as well
    new_groups, filtered_proteins = clean_protein_groups(
        df["Protein ID"].tolist(), map_to_uniprot
    )
    df["Protein ID"] = new_groups

    has_valid_protein_id = df["Protein ID"].map(bool)
    df = df[has_valid_protein_id]

    # sum intensities for duplicate protein groups, NaN if all are NaN, sum of numbers otherwise
    df = df.groupby("Protein ID", as_index=False).sum(min_count=1)
    df["Gene"] = np.nan  # add genes column back (removed by groupby)

    molten = pd.melt(
        df, id_vars=["Protein ID", "Gene"], var_name="Sample", value_name=intensity_name
    )
    ordered = molten[["Sample", "Protein ID", "Gene", intensity_name]]
    ordered.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)

    return ordered, dict(contaminants=contaminants, filtered_proteins=filtered_proteins)


def clean_protein_groups(protein_groups, map_to_uniprot=True):
    regex = {
        "ensembl_peptide_id": re.compile(r"^ENSP\d{11}"),
        "refseq_peptide": re.compile(r"^NP_\d{6,}"),
        "refseq_peptide_predicted": re.compile(r"^XP_\d{9}"),
    }
    uniprot = re.compile(
        r"""^[A-Z]               # start with capital letter
        [A-Z\d]{5}([A-Z\d]{4})?  # match ids of length 6 or 10
        ([-_][-\d]+)?            # match variations like -8 and _9-6
        """,
        re.VERBOSE,
    )

    removed_protein_ids = []

    extracted_ids = {k: set() for k in regex.keys()}
    found_ids_per_group = []
    for group in protein_groups:
        found_in_group = set()
        for protein_id in group.split(";"):
            if match := uniprot.search(protein_id):
                found_in_group.add(match.group(0))
                continue
            for identifier, pattern in regex.items():
                if match := pattern.search(protein_id):
                    found_id = match.group(0)
                    extracted_ids[identifier].add(found_id)
                    found_in_group.add(found_id)
                    break  # can only match one regex
            else:
                removed_protein_ids.append(protein_id)
        found_ids_per_group.append(found_in_group)

    if map_to_uniprot:
        id_to_uniprot = map_ids_to_uniprot(extracted_ids)
    new_groups = []

    for group in found_ids_per_group:
        all_ids_of_group = set()
        for old_id in group:
            if uniprot.search(old_id):
                all_ids_of_group.add(old_id)
            elif map_to_uniprot:
                new_ids = id_to_uniprot.get(old_id, [])
                all_ids_of_group.update(new_ids)
            else:
                all_ids_of_group.add(old_id)
        new_groups.append(";".join(sorted(all_ids_of_group)))
    return new_groups, removed_protein_ids


def map_ids_to_uniprot(extracted_ids):
    id_to_uniprot = defaultdict(list)
    for identifier, matching_ids in extracted_ids.items():
        if not matching_ids:
            continue

        result = biomart_query(
            matching_ids,
            identifier,
            [identifier, "uniprotswissprot"],
        )
        for other_id, uniport_id in result:
            if uniport_id:
                id_to_uniprot[other_id].append(uniport_id)

        # we trust reviewed results more, so we don't look up ids we found in
        # uniprotswissprot in uniprotsptrembl again
        left = matching_ids - set(id_to_uniprot.keys())

        result = biomart_query(
            left,
            identifier,
            [identifier, "uniprotsptrembl"],
        )
        for other_id, uniport_id in result:
            if uniport_id:
                id_to_uniprot[other_id].append(uniport_id)

    return dict(id_to_uniprot)
