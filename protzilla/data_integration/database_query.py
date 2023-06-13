from xml.etree.ElementTree import Element, SubElement, tostring
import pandas
from pathlib import Path
import requests

database_path = Path(__file__).parent / "databases"


def biomart_query(queries, filter_name, attributes):
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


def uniprot_query(uniprot_ids, fields):
    df = pandas.read_csv(database_path / "uniprot.tsv", sep="\t")
    df.index = df["Entry"]
    return df[df.Entry.isin(uniprot_ids)][fields].to_dict("index")


def uniprot_query_dataframe(uniprot_ids, fields):
    df = pandas.read_csv(database_path / "uniprot.tsv", sep="\t")
    df.index = df["Entry"]
    return df[df.Entry.isin(uniprot_ids)][fields]


def uniprot_columns():
    return pandas.read_csv(
        database_path / "uniprot.tsv", sep="\t", nrows=0
    ).columns.tolist() + ["Links"]
