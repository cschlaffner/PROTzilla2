from xml.etree.ElementTree import Element, SubElement, tostring

import pandas
import requests

from protzilla.constants.logging import logger
from protzilla.constants.paths import EXTERNAL_DATA_PATH


def biomart_query(queries, filter_name, attributes):
    if not queries:
        return

    root = Element(
        "Query",
        attrib={
            "virtualSchemaName": "default",
            "formatter": "TSV",
            "header": "0",
            "uniqueRows": "1",
            "datasetConfigVersion": "0.6",
        },
    )
    dataset = SubElement(
        root,
        "Dataset",
        attrib={"name": "hsapiens_gene_ensembl", "interface": "default"},
    )
    SubElement(
        dataset,
        "Filter",
        attrib={"name": filter_name, "value": ",".join(queries)},
    )
    for attribute in attributes:
        SubElement(dataset, "Attribute", attrib={"name": attribute})
    response = requests.post(
        url="http://grch37.ensembl.org/biomart/martservice",
        data={"query": tostring(root)},
        stream=True,
    )
    for line in response.iter_lines():
        yield line.decode("utf-8").split("\t")


def uniprot_query_dataframe(filename, uniprot_ids, fields):
    try:
        df = pandas.read_csv(
            EXTERNAL_DATA_PATH / "uniprot" / f"{filename}.tsv", sep="\t"
        )
    except FileNotFoundError:
        logger.error(
            f"Uniprot database not found at {EXTERNAL_DATA_PATH / 'uniprot.tsv'}\nGo to https://github.com/antonneubauer/PROTzilla2/wiki/Databases for more info."
        )
        return pandas.DataFrame(columns=["Entry"] + fields)
    df.index = df["Entry"]
    return df[df.Entry.isin(uniprot_ids)][fields]


def uniprot_columns(filename):
    return pandas.read_csv(
        EXTERNAL_DATA_PATH / "uniprot" / f"{filename}.tsv", sep="\t", nrows=0
    ).columns.tolist() + ["Links"]


def uniprot_databases():
    uniprot_path = EXTERNAL_DATA_PATH / "uniprot"
    if not uniprot_path.exists():
        return []
    databases = []
    for path in uniprot_path.iterdir():
        if path.suffix == ".tsv":
            databases.append(path.stem)
    return databases
