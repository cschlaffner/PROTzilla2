from xml.etree.ElementTree import Element, SubElement, tostring

import pandas as pd
import requests
from biomart import BiomartServer

from protzilla.constants.paths import EXTERNAL_DATA_PATH
from protzilla.constants.protzilla_logging import logger
from protzilla.utilities import clean_uniprot_id


def biomart_query(queries, filter_name, attributes, use_grch37=False):
    """
    Construct an XML query for BioMart, send it, decode the result and return it as an
    iterator.

    :param queries: what entities to look for with the filter
    :type queries: list[str]
    :param filter_name: the name of the BioMart category the queries will be searched in
    :type filter_name: str
    :param attributes: what BioMart categories to return for each found entity
    :type attributes: Iterable[str]
    :param use_grch37: if truthy, use the outdated GRCh37 biomart endpoint
    :type use_grch37: bool
    """
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

    biomart_urls = [
        "https://ensembl.org",
        "https://asia.ensembl.org",
        "https://useast.ensembl.org",
    ]
    if use_grch37:
        biomart_urls = ["http://grch37.ensembl.org/biomart/martservice"]

    for biomart_url in biomart_urls:
        try:
            response = requests.post(
                url=biomart_url,
                data={"query": tostring(root)},
                stream=True,
            )
            break
        except requests.ConnectionError:
            continue
    else:
        logger.warning("biomart server not available at the moment")
        return

    for line in response.iter_lines():
        decoded = line.decode("utf-8")
        if decoded == "<html>" or len(tabbed := decoded.split("\t")) != len(attributes):
            logger.warning("biomart query failed")
            return
        yield tabbed


def uniprot_query_dataframe(filename, uniprot_ids, fields):
    df = pd.read_csv(EXTERNAL_DATA_PATH / "uniprot" / f"{filename}.tsv", sep="\t")
    df.index = df["Entry"]
    return df[df.Entry.isin(uniprot_ids)][fields]


def uniprot_columns(filename):
    return pd.read_csv(
        EXTERNAL_DATA_PATH / "uniprot" / f"{filename}.tsv", sep="\t", nrows=0
    ).columns.tolist()


def biomart_database(
    database_name: str = "ENSEMBL_MART_ENSEMBL", max_attempts: int = 3
):
    mirror_list = [
        "http://ensembl.org/biomart",
        "http://asia.ensembl.org/biomart",
        "http://useast.ensembl.org/biomart",
    ]
    for _ in range(max_attempts):
        for url in mirror_list:
            try:
                server = BiomartServer(url)
                if server:
                    db = server.databases[database_name]
                    return db

            except requests.ConnectionError:
                continue


def uniprot_databases():
    uniprot_path = EXTERNAL_DATA_PATH / "uniprot"
    if not uniprot_path.exists():
        return []
    databases = []
    for path in uniprot_path.iterdir():
        if path.suffix == ".tsv":
            databases.append(path.stem)
    return sorted(databases)


def uniprot_to_genes(uniprot_ids, databases, use_biomart):
    """
    Maps uniprot IDs to hgnc gene symbols. Also returns IDs that could not be mapped.
    First uses all uniprot databases that contain genes, then uses biomart to map
    proteins that have not been found with uniprot if biomart is enabled.

    :param uniprot_ids: cleaned uniprot IDs, not containing isoforms or other
        modifications
    :type uniprot_ids: list[str]
    :param databases: names of uniprot databases that should be used for mapping
    :type databases: list[str]
    :param use_biomart: if true, biomart should be used to map ids that could not be
        mapped with databases
    :type use_biomart: bool

    :return: a dict that maps uniprot ids to genes and a list of uniprot ids that were
        not found
    :rtype: tuple[dict[str, str], list[str]]
    """

    def merge_dict(gene_mapping, new_gene_mapping):
        added_keys = set()
        for key, value in new_gene_mapping.items():
            if value and isinstance(value, str):
                gene_mapping[key] = value
                added_keys.add(key)
        return gene_mapping, added_keys

    logger.info("Mapping Uniprot IDs to genes.")
    out_dict = {}
    ids_to_search = set(uniprot_ids)
    for db_name in databases:
        # all available databases that have a gene column are used
        cols = uniprot_columns(db_name)
        if "Gene Names (primary)" in cols:
            df = uniprot_query_dataframe(
                db_name, ids_to_search, ["Gene Names (primary)"]
            )
            mapping = df.to_dict()["Gene Names (primary)"]
            out_dict, found_proteins = merge_dict(out_dict, mapping)
            ids_to_search -= found_proteins
        elif "Gene Names" in cols:
            df = uniprot_query_dataframe(
                db_name, ids_to_search, ["Gene Names"]
            ).dropna()
            mapping = df.to_dict()["Gene Names"]
            first_gene_dict = {k: v and v.split()[0] for k, v in mapping.items()}
            out_dict, found_proteins = merge_dict(out_dict, first_gene_dict)
            ids_to_search -= found_proteins

        if not ids_to_search:
            logger.info(
                "All proteins mapped using uniprot, no biomart mapping will be performed."  # noqa E501
            )
            return out_dict, []
    if not use_biomart:
        logger.info("Skipping biomart, done with mapping uniprot IDs to genes.")
        return out_dict, list(ids_to_search)
    logger.info("Starting biomart mapping.")
    biomart_results = list(
        biomart_query(
            ids_to_search, "uniprotswissprot", ["uniprotswissprot", "hgnc_symbol"]
        )
    )
    biomart_results += list(
        biomart_query(
            ids_to_search, "uniprotsptrembl", ["uniprotsptrembl", "hgnc_symbol"]
        )
    )
    uniprot_id_to_hgnc_symbol = dict(set(map(tuple, biomart_results)))
    # should not overwrite anything as ids_to_search not in out_dict yet
    out_dict, found_proteins = merge_dict(out_dict, uniprot_id_to_hgnc_symbol)
    not_found = ids_to_search - found_proteins
    logger.info("Done with mapping uniprot IDs to genes.")
    return out_dict, list(not_found)


def uniprot_groups_to_genes(
    uniprot_groups: list[str], databases: list[str], use_biomart: bool
):
    """
    Maps uniprot ID groups to hgnc gene symbols. Returns a DataFrame with "Protein ID" and "Gene" columns.

    :param uniprot_groups: groups of UniProt IDs, as found in a protein dataframe, may
        contain isoforms and modifications
    :type uniprot_groups: list[str]
    :param databases: names of uniprot databases that should be used for mapping
    :type databases: list[str]
    :param use_biomart: should biomart be used to map ids that could not be mapped with
        databases
    :type use_biomart: bool

    :return: a dict with a DataFrame mapping protein IDs to genes and a list of protein IDs that were not found
    :rtype: dict[str, Union[pd.DataFrame, list[str]]
    """
    proteins = set()
    for group in uniprot_groups:
        for protein in group.split(";"):
            proteins.add(clean_uniprot_id(protein))
    id_to_gene, not_found = uniprot_to_genes(list(proteins), databases, use_biomart)
    protein_id_gene_pairs = []
    filtered = []
    for group in uniprot_groups:
        clean = set(clean_uniprot_id(protein) for protein in group.split(";"))
        genes = [
            id_to_gene[protein_id] for protein_id in clean if id_to_gene.get(protein_id)
        ]
        if not genes:
            filtered.append(group)
        for gene in genes:
            protein_id_gene_pairs.append((group, gene))

    mapping_df = pd.DataFrame(protein_id_gene_pairs, columns=["Protein ID", "Gene"])
    return dict(gene_mapping_df=mapping_df, filtered_protein_ids=filtered)
