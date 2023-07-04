import csv
import json
from pathlib import Path

import pandas as pd
from django.contrib import messages

from protzilla.constants.logging import logger


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
    """
    Reads a file of background proteins or genes.
    Accepts .csv and .txt files with one protein or gene per line.
    :param path: path to file
    :type path: str or None
    :return: list of background proteins or genes or error message
    :rtype: list
    """
    if not path:
        return None
    else:
        file_extension = Path(path).suffix
        if file_extension == ".csv":
            background = pd.read_csv(path, low_memory=False, header=None)
            # if multiple columns, use first
            background = background.iloc[:, 0].tolist()
            logger.warning(
                "You provided a background file with multiple columns. Only the first will be used."
            )
        elif file_extension == ".txt":
            with open(path, "r") as f:
                background = [line.strip() for line in f]
        else:
            msg = "Invalid file type for background. Must be .csv, .txt or no upload"
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])

        return background
