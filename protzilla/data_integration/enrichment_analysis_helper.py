import csv
import json
import os

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
    proteins_list = []
    for group in proteins:
        group = group.split(";")
        # isoforms map to the same gene symbol, that is only found with base protein
        without_isoforms = set()
        for protein in group:
            if "-" in protein:
                without_isoforms.add(protein.split("-")[0])
            elif "_VAR_" in protein:
                without_isoforms.add(protein.split("_VAR_")[0])
            else:
                without_isoforms.add(protein)
        proteins_list.extend(list(without_isoforms))
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
    q = dict(set(map(tuple, q)))
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
            if result := q.get(protein):
                symbols.add(result)

        if not symbols:  # no gene symbol for any protein in group
            filtered_groups.append(group)
        else:
            for symbol in symbols:
                # duplicates per gene are not expected but handled here
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
        - .txt:
            Set_name: Protein1, Protein2, ...
            Set_name2: Protein2, Protein3, ...
        - .csv:
            Set_name, Protein1, Protein2, ...
            Set_name2, Protein2, Protein3, ...
        - .json:
            {Set_name: [Protein1, Protein2, ...], Set_name2: [Protein2, Protein3, ...]}
    :param path: path to file
    :type path: str
    :return: dict with protein or gene sets, a path to a gmt file or error message
    :rtype: dict
    """
    if path == "" or path is None:
        return dict(
            messages=[
                dict(
                    level=messages.ERROR,
                    msg="No file uploaded for protein sets.",
                )
            ]
        )

    file_extension = os.path.splitext(path)[1]
    if file_extension == ".csv":
        with open(path, "r") as f:
            reader = csv.reader(f)
            sets = {}
            for row in reader:
                key = row[0]
                values = row[1:]
                sets[key] = values

    elif file_extension == ".txt":
        with open(path, "r") as f:
            sets = {}
            for line in f:
                key, value_str = line.strip().split(":")
                values = [v.strip() for v in value_str.split(",")]
                sets[key] = values

    elif file_extension == ".json":
        with open(path, "r") as f:
            sets = json.load(f)

    elif file_extension == ".gmt":
        # gseapy can handle gmt files
        sets = path

    else:
        return dict(
            messages=[
                dict(
                    level=messages.ERROR,
                    msg="Invalid file type for protein sets. Must be .csv, .txt, .json or .gmt",
                )
            ]
        )
    return sets
