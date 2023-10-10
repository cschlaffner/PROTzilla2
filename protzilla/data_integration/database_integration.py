import pandas as pd
from django.contrib import messages

from protzilla.data_integration import database_query
from protzilla.utilities import clean_uniprot_id, unique_justseen


def add_uniprot_data(dataframe, database_name=None, fields=None):
    """
    Extend a protein dataframe with information from UniProt for each protein.

    :param dataframe: the protein dataframe to be extendet
    :type dataframe: pd.DataFrame
    :param database_name: name of the database file that will be queried
    :type database_name: str
    :param fields: the fields of the database that will be added to the dataframe
    :type fields: list[str]

    :return: the extended dataframe, and a message if applicable
    :rtype: dict
    """
    if not fields:
        msg = "No fields that should be added specified."
        return dict(
            results_df=dataframe,
            messages=[dict(level=messages.INFO, msg=msg)],
        )
    if isinstance(fields, str):
        fields = [fields]
    groups = dataframe["Protein ID"].tolist()
    clean_groups = []
    all_proteins = set()

    # remove isoforms and variants from groups
    for group in groups:
        proteins = group.split(";")
        cleaned = []
        for protein in proteins:
            clean = clean_uniprot_id(protein)
            cleaned.append(clean)
            all_proteins.add(clean)
        # this can be done because we make isoforms appear together
        clean_groups.append(list(unique_justseen(cleaned)))

    # add links
    if "Links" in fields:
        links = []
        for group in clean_groups:
            group_links = [
                f"https://uniprot.org/uniprotkb/{protein}" for protein in group
            ]
            links.append(" ".join(group_links))
        dataframe["Links"] = links
    database_fields = [field for field in fields if field != "Links"]
    if not database_fields:
        return {"results_df": dataframe}
    res: pd.DataFrame = database_query.uniprot_query_dataframe(
        database_name, list(all_proteins), database_fields
    )

    for field in database_fields:
        new_column = []
        for group in clean_groups:
            group_values = []
            for member in group:
                if member not in res.index:
                    group_values.append(None)
                    continue
                result = res.loc[member][field]
                if "Gene Names" in field and isinstance(result, str):
                    # to remove space seperated groupings
                    group_values.append(result.split()[0])
                else:
                    group_values.append(result)
            if len(set(group_values)) == 1:
                new_column.append(group_values[0])
            else:
                new_column.append(";".join(map(str, group_values)))
        dataframe[field] = new_column
    return {"results_df": dataframe}


def gene_mapping(dataframe, database_names, use_biomart=False):
    """
    Maps the protein ID groups to HGNC gene symbols, filtering out ones that are not found.

    :param dataframe: the protein dataframe of which the protein ID groups will be mapped.
    :type dataframe: pd.DataFrame
    :param database_names: names of the database files that will be queried
    :type database_names: list[str] | str
    :param use_biomart: should biomart be used to map ids that could not be mapped with databases
    :type use_biomart: bool

    :return: the gene mapping, consisting of group_to_genes, gene_to_groups and filtered
    :rtype: dict
    """
    try:
        groups = dataframe["Protein ID"].unique().tolist()
    except KeyError:
        msg = "No Protein ID column found."
        return dict(
            messages=[dict(level=messages.ERROR, msg=msg)],
        )
    if isinstance(database_names, str):
        database_names = [database_names]
    gene_to_groups, groups_to_genes, filtered = database_query.uniprot_groups_to_genes(
        groups, database_names, use_biomart=use_biomart
    )
    return {
        "gene_mapping": {
            "group_to_genes": groups_to_genes,
            "gene_to_groups": gene_to_groups,
            "filtered": filtered,
        }
    }
