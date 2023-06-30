import csv
import json
from pathlib import Path

from django.contrib import messages


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
        msg = "Invalid file type for protein sets. Must be .csv, .txt, .json or .gmt"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    return sets
