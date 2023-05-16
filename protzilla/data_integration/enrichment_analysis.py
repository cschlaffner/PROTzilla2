import os
import json
import csv
import logging
import pandas as pd
import gseapy as gp
from django.contrib import messages


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
    enr = gp.enrich(
        gene_list=proteins,
        gene_sets=protein_sets,
        background=background,
        outdir=None,
        verbose=True,
    )

    return {"results": enr.results}
