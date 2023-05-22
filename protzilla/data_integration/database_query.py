from xml.etree.ElementTree import Element, SubElement, tostring

import requests


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
