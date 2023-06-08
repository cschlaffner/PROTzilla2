from .database_query import biomart_query


def uniprot_ids_to_uppercase_gene_symbols(proteins):
    """
    A method that converts a list of uniprot ids to uppercase gene symbols.
    This is done by querying the biomart database. If a protein group is not found
    in the database, it is added to the filtered_groups list. For every protein group
    all resulting gene symbols are added to the group_to_genes dict.
    :param proteins: list of uniprot ids
    :type proteins: list
    :return: dict gene_mapping with keys uppercase gene symbols and values protein_groups or proteins,
        dict group_to_genes with keys protein_groups and values list of gene symbols and
        a list of uniprot ids that were not found.
    :rtype: tuple
    """
    proteins_list = []
    for group in proteins:
        if ";" not in group:
            proteins_list.append(group)
        else:
            group = group.split(";")
            # isoforms map to the same gene symbol, that is only found with base protein
            without_isoforms = set()
            for protein in group:
                if "-" in protein:
                    without_isoforms.add(protein.split("-")[0])
                elif "_VAR_" in protein:
                    without_isoforms.add(protein.split("_VAR_")[0])
                else:
                    without_isoforms.add(protein)
            proteins_list.extend(list(without_isoforms))
    q = list(
        biomart_query(
            proteins_list, "uniprotswissprot", ["uniprotswissprot", "hgnc_symbol"]
        )
    )
    q += list(
        biomart_query(
            proteins_list, "uniprotsptrembl", ["uniprotsptrembl", "hgnc_symbol"]
        )
    )
    q = dict(set(map(tuple, q)))
    # check per group in proteins if all proteins have the same gene symbol
    # if yes, use that gene symbol, otherwise use all gene symbols
    filtered_groups = []
    gene_mapping = {}
    group_to_genes = {}
    for group in proteins:
        if ";" not in group:
            symbol = q.get(group, None)
            if symbol is None:
                filtered_groups.append(group)
            else:
                gene_mapping[symbol.upper()] = group
                group_to_genes[group] = [symbol.upper()]
        else:
            # remove duplicate symbols within one group
            symbols = set()
            for protein in group.split(";"):
                if "-" in protein:
                    protein = protein.split("-")[0]
                elif "_VAR_" in protein:
                    protein = protein.split("_VAR_")[0]
                if result := q.get(protein):
                    symbols.add(result)

            if not symbols:  # no gene symbol for any protein in group
                filtered_groups.append(group)
            else:
                for symbol in symbols:
                    gene_mapping[symbol.upper()] = group
                group_to_genes[group] = list(symbols)

    return gene_mapping, group_to_genes, filtered_groups
