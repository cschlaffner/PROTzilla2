from xml.etree.ElementTree import Element, SubElement, tostring
import pandas
import requests

from protzilla.constants.paths import DATABASES_PATH


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


def uniprot_query(uniprot_ids, fields):
    df = read_uniprot(fields)
    return df[df.Entry.isin(uniprot_ids)][fields].to_dict("index")


def uniprot_query_dataframe(uniprot_ids, fields):
    df = read_uniprot(fields)
    return df[df.Entry.isin(uniprot_ids)][fields]


def read_uniprot(fields):
    try:
        df = pandas.read_csv(DATABASES_PATH / "uniprot.tsv", sep="\t")
    except FileNotFoundError:
        print(f"Uniprot database not found at {DATABASES_PATH / 'uniprot.tsv'}")
        return pandas.DataFrame(columns=["Entry"] + fields)
    df.index = df["Entry"]
    return df


print(uniprot_query(["P10636"], fields=["Length"]))
