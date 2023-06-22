import csv
import json
from pathlib import Path

import pandas as pd
from django.contrib import messages

from .database_query import biomart_query


def uniprot_ids_to_uppercase_gene_symbols(proteins):
    """
    A method that converts a list of uniprot ids to uppercase gene symbols.
    This is done by querying the biomart database. If a protein group is not found
    in the database, it is added to the filtered_groups list. For every protein group
    all resulting gene symbols are added to the group_to_genes dict.
    :param proteins: list of uniprot ids
    :type proteins: list
    :return: dict gene_to_groups with keys uppercase gene symbols and values list of protein_groups,
        dict group_to_genes with keys protein_groups and values list of gene symbols and
        a list of uniprot ids that were not found.
    :rtype: tuple
    """
    proteins_set = set()
    for group in proteins:
        group = group.split(";")
        # isoforms map to the same gene symbol, that is only found with base protein
        for protein in group:
            if "-" in protein:
                proteins_set.add(protein.split("-")[0])
            elif "_VAR_" in protein:
                proteins_set.add(protein.split("_VAR_")[0])
            else:
                proteins_set.add(protein)
    proteins_list = list(proteins_set)
    q = list(
        biomart_query(
            proteins_list, "uniprotswissprot", ["uniprotswissprot", "hgnc_symbol"]
        )
    )
    q += list(
        biomart_query(
            proteins_list, "uniprotsptrembl", ["uniprotsptrembl", "hgnc_symbol"]
        )
    )
    uniprotID_to_hgnc_symbol = dict(set(map(tuple, q)))
    # check per group in proteins if all proteins have the same gene symbol
    # if yes, use that gene symbol, otherwise use all gene symbols
    filtered_groups = []
    gene_to_groups = {}
    group_to_genes = {}
    for group in proteins:
        symbols = set()
        for protein in group.split(";"):
            if "-" in protein:
                protein = protein.split("-")[0]
            elif "_VAR_" in protein:
                protein = protein.split("_VAR_")[0]
            if result := uniprotID_to_hgnc_symbol.get(protein):
                symbols.add(result)

        if not symbols:  # no gene symbol for any protein in group
            filtered_groups.append(group)
        else:
            for symbol in symbols:
                if symbol.upper() in gene_to_groups:
                    gene_to_groups[symbol.upper()].append(group)
                else:
                    gene_to_groups[symbol.upper()] = [group]
            group_to_genes[group] = list(symbols)

    return gene_to_groups, group_to_genes, filtered_groups


def read_protein_or_gene_sets_file(path):
    """
    A method that reads a file with protein or gene sets and returns a dict with them.
    The file can be a .csv, .txt, .json or .gmt file.
    The file must have one set per line with the set name and the proteins or genes.
    .gmt files are not parsed because GSEApy can handle them directly.
        - .txt: Setname or identifier followed by a tab-separated list of genes
            Set_name    Protein1    Protein2...
            Set_name    Protein1    Protein2...
        - .csv: Setname or identifier followed by a comma-separated list of genes
            Set_name, Protein1, Protein2, ...
            Set_name2, Protein2, Protein3, ...
        - .json:
            {Set_name: [Protein1, Protein2, ...], Set_name2: [Protein2, Protein3, ...]}
    :param path: path to file
    :type path: str
    :return: dict with protein or gene sets, a path to a gmt file or error message
    :rtype: dict
    """
    if not path:
        msg = "No file uploaded for protein sets."
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    file_extension = Path(path).suffix
    if file_extension == ".csv":
        with open(path, "r") as f:
            reader = csv.reader(f)
            sets = {}
            for row in reader:
                key, *values = row
                sets[key] = values

    elif file_extension == ".txt":
        with open(path, "r") as f:
            sets = {}
            for line in f.readlines():
                key, *values = line.strip().split("\t")
                sets[key] = values

    elif file_extension == ".json":
        with open(path, "r") as f:
            sets = json.load(f)

    elif file_extension == ".gmt":
        # gseapy can handle gmt files
        sets = path

    else:
        msg = "Invalid file type for protein sets. Must be .csv, .txt, .json or .gmt"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    return sets


def read_background_file(path):
    if not path:
        return None
    else:
        file_extension = Path(path).suffix
        if file_extension == ".csv":
            background = pd.read_csv(path, low_memory=False, header=None)
            # if multiple columns, use first
            background = background.iloc[:, 0].tolist()
        elif file_extension == ".txt":
            with open(path, "r") as f:
                background = [line.strip() for line in f]
        else:
            msg = "Invalid file type for background. Must be .csv, .txt or no upload"
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])

        return background
