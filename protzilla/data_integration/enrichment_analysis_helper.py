import csv
import json
from pathlib import Path

import pandas as pd
import requests
from django.contrib import messages

from protzilla.constants.logging import logger
from protzilla.utilities.utilities import random_string


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
    Empty strings are removed from the list of proteins or genes.
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
                sets[key] = [value for value in values if value.strip()]

    elif file_extension == ".txt":
        with open(path, "r") as f:
            sets = {}
            for line in f.readlines():
                key, *values = line.strip().split("\t")
                sets[key] = [value for value in values if value.strip()]

    elif file_extension == ".json":
        with open(path, "r") as f:
            sets = json.load(f)
            sets = {
                key: [value for value in values if value.strip()]
                for key, values in sets.items()
            }

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
    Empty strings are removed from the list of proteins or genes.
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
            background = background.iloc[:, 0].dropna().tolist()
            logger.warning(
                "You provided a background file with multiple columns. Only the first will be used."
            )
        elif file_extension == ".txt":
            with open(path, "r") as f:
                background = [line.strip() for line in f if line.strip()]
        else:
            msg = "Invalid file type for background. Must be .csv, .txt or no upload"
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])

        return background


def map_to_string_ids(proteins_list, organism):
    """
    This method maps a list of protein IDs to STRING IDs using the STRING API.
    :param proteins_list: list of protein IDs
    :type proteins_list: list
    :param organism: organism NCBI identifier
    :type organism: str
    :return: list of STRING IDs or None if no IDs could be found
    :rtype: list or None
    """
    logger.info("Mapping proteins to STRING IDs")
    string_api_url = "https://string-db.org/api"  # latest version while in development
    output_format = "tsv-no-header"
    method = "get_string_ids"

    params = {
        "identifiers": "\r".join(proteins_list),
        "species": organism,  # species NCBI identifier
        "limit": 1,  # only one (best) identifier per input protein
        "echo_query": 1,  # see input identifiers in the output
        "caller_identity": f"PROTzilla-{random_string()}",
    }

    request_url = "/".join([string_api_url, output_format, method])
    results = requests.post(request_url, data=params)  # call STRING API

    mapped = []
    for line in results.text.strip().split("\n"):
        split_line = line.split("\t")
        if len(split_line) < 3:  # no identifier found
            continue
        string_identifier = split_line[2]
        mapped.append(string_identifier)

    if len(mapped) == 0:
        logger.warning("No STRING IDs could be found")
        mapped = None
    else:
        logger.info(f"Mapped {len(mapped)} proteins to STRING IDs")
    return mapped
