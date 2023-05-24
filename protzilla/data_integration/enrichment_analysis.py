import csv
import json
import logging
import os

import gseapy as gp
import pandas as pd
from django.contrib import messages

from .database_query import biomart_query


def uniprot_ids_to_uppercase_gene_symbols(proteins):
    """
    A method that converts a list of uniprot ids to uppercase gene symbols.
    This is done by querying the biomart database. If a protein group is not found
    in the database, it is added to the filtered_groups list.

    :param proteins: list of uniprot ids
    :type proteins: list
    :return: list of uppercase gene symbols and list of uniprot ids that were not found
    :rtype: tuple
    """
    proteins_list = []
    for group in proteins:
        if ";" not in group:
            proteins_list.append(group)
        else:
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
    gene_symbols = []
    for group in proteins:
        if ";" not in group:
            symbol = q.get(group, None)
            if symbol is None:
                filtered_groups.append(group)
            else:
                gene_symbols.append(symbol.upper())
        else:
            # remove duplicate symbols within one group
            symbols = set()
            for protein in group.split(";"):
                if "-" in protein:
                    symbols.add(q.get(protein.split("-")[0], None))
                elif "_VAR_" in protein:
                    symbols.add(q.get(protein.split("_VAR_")[0], None))
                else:
                    symbols.add(q.get(protein, None))

            symbols = list(symbols)
            if not any(symbols):
                # no gene symbol for any protein in group
                filtered_groups.append(group)
            elif len(symbols) == 1:
                gene_symbols.append(symbols[0].upper())
            else:
                gene_symbols.extend([s.upper() for s in symbols if s is not None])

    return gene_symbols, filtered_groups


def go_analysis_with_enrichr(proteins, protein_sets, organism):
    """
    A method that performs online overrepresentation analysis for a given set of proteins
    against a given set of protein sets using the GSEApy package which accesses
    the Enrichr API. Uniprot Protein IDs are converted to uppercase HGNC gene symbols.
    If no match is found, the protein is excluded from the analysis. All excluded proteins
    are returned in a list.

    :param proteins: proteins to be analyzed
    :type proteins: list, series or dataframe
    :param protein_sets: list of Enrichr Library name(s) to use as sets for the enrichment
        (e.g. ['KEGG_2016','KEGG_2013'])
    :type protein_sets_path: list of str
    :param organism: organism to be used for the analysis, must be one of the following
        supported by Enrichr: "human", "mouse", "yeast", "fly", "fish", "worm"
    :type organism: str
    :return: dictionary with results and filtered groups
    :rtype: dict
    """
    # enhancement: protein_sets are categorical for now, could also be custom file upload later
    #       background parameter would work then (with uploaded file)
    # dependency: refactoring/designing of more complex input choices

    # make list of proteins
    if isinstance(proteins, pd.DataFrame):
        proteins = proteins["Protein ID"].unique().tolist()
    elif isinstance(proteins, pd.Series):
        proteins = proteins.unique().tolist()
    elif isinstance(proteins, list):
        pass
    else:
        return dict(
            messages=[
                dict(
                    level=messages.ERROR,
                    msg="Invalid input type for proteins. Must be list, series or dataframe",
                )
            ]
        )

    gene_symbols, filtered_groups = uniprot_ids_to_uppercase_gene_symbols(proteins)

    enr = gp.enrichr(
        gene_list=gene_symbols,
        gene_sets=protein_sets,
        organism=organism,
        outdir=None,
        verbose=True,
    )

    if len(filtered_groups) > 0:
        msg = "Some proteins could not be mapped to gene symbols and were excluded from the analysis"
        return dict(
            results=enr.results,
            filtered_groups=filtered_groups,
            messages=[dict(level=messages.WARNING, msg=msg)],
        )

    return {"results": enr.results, "filtered_groups": filtered_groups}


def go_analysis_offline(proteins, protein_sets_path, background=None):
    """
    A method that performs offline overrepresentation analysis for a given set of proteins
    against a given set of protein sets using the GSEApy package.
    For the analysis a hypergeometric test is used.

    :param proteins: proteins to be analyzed
    :type proteins: list, series or dataframe
    :param protein_sets_path: path to file containing protein sets. The identifers
        in the protein_sets should be the same type as the backgrounds and the proteins.

        This could be any of the following file types: .gmt, .txt, .csv, .json
        - .txt:
            Set_name: Protein1, Protein2, ...
            Set_name2: Protein2, Protein3, ...
        - .csv:
            Set_name, Protein1, Protein2, ...
            Set_name2, Protein2, Protein3, ...
        - .json:
            {Set_name: [Protein1, Protein2, ...], Set_name2: [Protein2, Protein3, ...]}
    :type protein_sets_path: str
    :param background: background proteins to be used for the analysis. If no
        background is provided, all proteins in protein sets are used.
        The background is defined by your experiment.
    :type background: str or None
    """
    # enhancement: proteins could also be a number input (or an uploaded file)
    # dependency: refactoring/designing of more complex input choices

    # enhancement: make sure ID type for all inputs match

    # make list of proteins
    if isinstance(proteins, pd.DataFrame):
        proteins = proteins["Protein ID"].unique().tolist()
    elif isinstance(proteins, pd.Series):
        proteins = proteins.unique().tolist()
    elif isinstance(proteins, list):
        pass
    else:
        return dict(
            messages=[
                dict(
                    level=messages.ERROR,
                    msg="Invalid input type for proteins. Must be list, series or dataframe",
                )
            ]
        )

    if protein_sets_path == "":
        return dict(
            messages=[
                dict(
                    level=messages.ERROR,
                    msg="No file uploaded for protein sets.",
                )
            ]
        )

    file_extension = os.path.splitext(protein_sets_path)[1]
    if file_extension == ".csv":
        with open(protein_sets_path, "r") as f:
            reader = csv.reader(f)
            protein_sets = {}
            for row in reader:
                key = row[0]
                values = row[1:]
                protein_sets[key] = values

    elif file_extension == ".txt":
        with open(protein_sets_path, "r") as f:
            protein_sets = {}
            for line in f:
                key, value_str = line.strip().split(":")
                values = [v.strip() for v in value_str.split(",")]
                protein_sets[key] = values

    elif file_extension == ".json":
        with open(protein_sets_path, "r") as f:
            protein_sets = json.load(f)

    elif file_extension == ".gmt":
        # gseapy can handle gmt files
        protein_sets = protein_sets_path

    else:
        return dict(
            messages=[
                dict(
                    level=messages.ERROR,
                    msg="Invalid file type for protein sets. Must be .csv, .txt, .json or .gmt",
                )
            ]
        )

    if background == "" or background is None:
        logging.info("No background provided, using all proteins in protein sets")
        background = None
    else:
        file_extension = os.path.splitext(background)[1]
        if file_extension == ".csv":
            background = pd.read_csv(
                background, sep="\t", low_memory=False, header=None
            )
            # if multiple columns, use first
            background = background.iloc[:, 0].tolist()
        elif file_extension == ".txt":
            with open(background, "r") as f:
                background = [line.strip() for line in f]
        else:
            return dict(
                messages=[
                    dict(
                        level=messages.ERROR,
                        msg="Invalid file type for background. Must be .csv, .txt or no upload",
                    )
                ]
            )

    # gene set and gene list identifiers need to match
    try:
        enr = gp.enrich(
            gene_list=proteins,
            gene_sets=protein_sets,
            background=background,
            outdir=None,
            verbose=True,
        )
    except ValueError as e:
        return dict(
            messages=[
                dict(
                    level=messages.ERROR,
                    msg="Something went wrong with the analysis. Please check your inputs.",
                    trace=str(e),
                )
            ]
        )

    return {"results": enr.results}
