import logging
import re
import traceback
from collections import defaultdict

import numpy as np
import pandas as pd

from protzilla.data_integration.database_query import biomart_query
from protzilla.utilities import format_trace


def max_quant_import(
    file_path: str,
    intensity_name: str,
    map_to_uniprot=False,
    aggregation_method: str = "Sum",
) -> dict:
    assert intensity_name in ["Intensity", "iBAQ", "LFQ intensity"]
    try:
        df = pd.read_csv(
            file_path,
            sep="\t",
            low_memory=False,
            na_values=["", 0],
            keep_default_na=True,
        )
        protein_groups = df["Majority protein IDs"]
        intensity_df = df.filter(regex=f"^{intensity_name} ", axis=1)
        intensity_df = intensity_df.filter(regex=r"^(?!.*peptides).*$", axis=1)

        if intensity_df.empty:
            msg = f"{intensity_name} was not found in the provided file, please use another intensity and try again or verify your file."
            return dict(messages=[dict(level=logging.ERROR, msg=msg)])

        intensity_df.columns = [
            c[len(intensity_name) + 1 :] for c in intensity_df.columns
        ]
        intensity_df = intensity_df.assign(**{"Protein ID": protein_groups})
        return transform_and_clean(
            intensity_df, intensity_name, map_to_uniprot, aggregation_method
        )

    except Exception as e:
        msg = f"An error occurred while reading the file: {e.__class__.__name__} {e}. Please provide a valid Max Quant file."
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg=msg,
                    trace=format_trace(traceback.format_exception(e)),
                )
            ]
        )


def ms_fragger_import(
    file_path: str,
    intensity_name: str,
    map_to_uniprot=False,
    aggregation_method: str = "Sum",
) -> dict:
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
    try:
        df = pd.read_csv(
            file_path,
            sep="\t",
            low_memory=False,
            na_values=["", 0],
            keep_default_na=True,
        )
        protein_groups = df["Protein ID"]
        columns_to_drop = [
            "Combined Spectral Count",
            "Combined Unique Spectral Count",
            "Combined Total Spectral Count",
        ]
        existing_columns = set(df.columns)
        columns_to_drop_existing = [
            col for col in columns_to_drop if col in existing_columns
        ]
        df = df.drop(columns=columns_to_drop_existing)

        intensity_df = df.filter(regex=f"{intensity_name}$", axis=1)
        # TODO 423 check if any samples are misinterpreted as intensities (see max_quant_import)
        intensity_df.columns = [
            c[: -(len(intensity_name) + 1)] for c in intensity_df.columns
        ]
        intensity_df = intensity_df.drop(
            columns=intensity_df.filter(
                regex="MaxLFQ Total$|MaxLFQ$|Total$|MaxLFQ Unique$|Unique$", axis=1
            ).columns
        )
        intensity_df = intensity_df.assign(**{"Protein ID": protein_groups})

        return transform_and_clean(
            intensity_df, intensity_name, map_to_uniprot, aggregation_method
        )
    except Exception as e:
        msg = f"An error occurred while reading the file: {e.__class__.__name__} {e}. Please provide a valid MS Fragger file."
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg=msg,
                    trace=format_trace(traceback.format_exception(e)),
                )
            ]
        )


def diann_import(
    file_path, map_to_uniprot=False, aggregation_method: str = "Sum"
) -> dict:
    try:
        df = pd.read_csv(
            file_path,
            sep="\t",
            low_memory=False,
            na_values=["", 0],
            keep_default_na=True,
        )
        df = df.drop(
            columns=[
                "Protein.Group",
                "Protein.Names",
                "Genes",
                "First.Protein.Description",
            ]
        )
        # rename column names of samples, removing file path and ".raw" if present
        intensity_df = df.rename(columns=lambda x: re.sub(r"(.*[/\\])|(.raw)", r"", x))
        intensity_df = intensity_df.rename(columns={"Protein.Ids": "Protein ID"})
        # TODO 423 check if any samples are misinterpreted as intensities (see max_quant_import)

        intensity_name = "Intensity"

        return transform_and_clean(
            intensity_df, intensity_name, map_to_uniprot, aggregation_method
        )
    except Exception as e:
        msg = f"An error occurred while reading the file: {e.__class__.__name__} {e}. Please provide a valid DIA-NN MS file."
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg=msg,
                    trace=format_trace(traceback.format_exception(e)),
                )
            ]
        )


def transform_and_clean(
    df: pd.DataFrame,
    intensity_name: str,
    map_to_uniprot: bool,
    aggregation_method: str = "Sum",
) -> dict:
    """
    Transforms a dataframe that is read from a file in wide format into long format,
    removing contaminant groups, and processing protein ids, removing invalid ones

    :param df: wide dataframe containing a protein column and sample columns
    :type df: pd.DataFrame
    :param intensity_name: name of the intensity in the output dataframe
    :type intensity_name: str
    :param map_to_uniprot: decides if protein ids will be mapped to uniprot ids
    :type map_to_uniprot: bool
    :return: a dict of a protzilla dataframe in long format with sample, protein, gene and
        intensity columns; contaminants and rejected proteins
    """
    assert "Protein ID" in df.columns
    contaminant_groups_mask = df["Protein ID"].map(
        lambda group: any(id_.startswith("CON__") for id_ in group.split(";"))
    )
    contaminants = df[contaminant_groups_mask]["Protein ID"].tolist()
    df = df[~contaminant_groups_mask]

    # REV__ and XXX__ proteins get removed here as well
    new_groups, filtered_proteins = clean_protein_groups(
        df["Protein ID"].tolist(), map_to_uniprot
    )
    df = df.assign(**{"Protein ID": new_groups})

    has_valid_protein_id = df["Protein ID"].map(bool)
    df = df[has_valid_protein_id]

    # applies the selected aggregation to duplicate protein groups, NaN if all are NaN, aggregation of numbers otherwise
    aggregation_method = aggregation_method.lower()
    agg_kwargs = {"sum": {"min_count": 1}, "median": {}, "mean": {}}
    df = df.groupby("Protein ID", as_index=False).agg(
        aggregation_method, **agg_kwargs[aggregation_method]
    )

    df = df.assign(Gene=lambda _: np.nan)  # add deprecated genes column

    molten = pd.melt(
        df, id_vars=["Protein ID", "Gene"], var_name="Sample", value_name=intensity_name
    )
    molten = molten[["Sample", "Protein ID", "Gene", intensity_name]]
    molten.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)

    msg = f"Successfully imported {len(df)} protein groups for {int(len(molten)/len(df))} samples. {len(contaminants)} contaminant groups were dropped. {len(filtered_proteins)} invalid proteins were filtered."
    return dict(
        protein_df=molten,
        contaminants=contaminants,
        filtered_proteins=filtered_proteins,
        messages=[dict(level=logging.INFO, msg=msg)],
    )


def clean_protein_groups(protein_groups, map_to_uniprot=True):
    regex = {
        "ensembl_peptide_id": re.compile(r"^ENSP\d{11}"),
        "refseq_peptide": re.compile(r"^NP_\d{6,}"),
        "refseq_peptide_predicted": re.compile(r"^XP_\d{9}"),
    }
    uniprot_regex = re.compile(
        r"""^[A-Z]               # start with capital letter
        [A-Z\d]{5}([A-Z\d]{4})?  # match ids of length 6 or 10
        ([-_][-\d]+)?            # match variations like -8 and _9-6
        """,
        re.VERBOSE,
    )

    removed_protein_ids = []

    extracted_ids = {k: set() for k in regex.keys()}
    found_ids_per_group = []
    # go through all groups and find the valid proteins
    # non uniprot ids are put into extracted_ids, so they can be mapped
    for group in protein_groups:
        found_in_group = []
        for protein_id in group.split(";"):
            if not protein_id.startswith("ENSP") and (
                match := uniprot_regex.search(protein_id)
            ):
                found_in_group.append(match.group(0))
                continue
            for identifier, pattern in regex.items():
                if match := pattern.search(protein_id):
                    found_id = match.group(0)
                    extracted_ids[identifier].add(found_id)
                    found_in_group.append(found_id)
                    break  # can only match one regex
            else:
                removed_protein_ids.append(protein_id)
        found_ids_per_group.append(found_in_group)

    if map_to_uniprot:
        id_to_uniprot = map_ids_to_uniprot(extracted_ids)
    new_groups = []

    for group in found_ids_per_group:
        all_ids_of_group = []
        for old_id in group:
            if uniprot_regex.search(old_id):
                all_ids_of_group.append(old_id)
            elif map_to_uniprot:
                new_ids = pd.Series(id_to_uniprot.get(old_id, []))
                new_ids = new_ids[~new_ids.isin(all_ids_of_group)]
                all_ids_of_group.extend(new_ids)
            else:
                all_ids_of_group.append(old_id)
        new_groups.append(all_ids_of_group[0] if all_ids_of_group else "")
    return new_groups, removed_protein_ids


def map_ids_to_uniprot(extracted_ids):
    id_to_uniprot = defaultdict(list)
    for identifier, ids in extracted_ids.items():
        if not ids:
            continue

        result = biomart_query(ids, identifier, [identifier, "uniprotswissprot"])
        for other_id, uniport_id in result:
            if uniport_id:
                id_to_uniprot[other_id].append(uniport_id)

        # we trust reviewed results more, so we don't look up ids we found in
        # uniprotswissprot in uniprotsptrembl again
        left = ids - set(id_to_uniprot.keys())
        result = biomart_query(left, identifier, [identifier, "uniprotsptrembl"])
        for other_id, uniport_id in result:
            if uniport_id:
                id_to_uniprot[other_id].append(uniport_id)

    return dict(id_to_uniprot)
