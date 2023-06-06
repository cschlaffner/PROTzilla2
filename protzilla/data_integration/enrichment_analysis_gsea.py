import gseapy as gp
import pandas as pd

from protzilla.utilities.transform_dfs import long_to_wide


def uniprot_ids_to_uppercase_gene_symbols(proteins):
    """
    A method that converts a list of uniprot ids to uppercase gene symbols.
    This is done by querying the biomart database. If a protein group is not found
    in the database, it is added to the filtered_groups list.

    :param proteins: list of uniprot ids
    :type proteins: list
    :return: dict with keys uppercase gene symbols and values protein_groups and a list of uniprot ids that were not found
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
    for group in proteins:
        if ";" not in group:
            symbol = q.get(group, None)
            if symbol is None:
                filtered_groups.append(group)
            else:
                gene_mapping[symbol.upper()] = group
        else:
            # remove duplicate symbols within one group
            symbols = set()
            for protein in group.split(";"):
                if "-" in protein:
                    symbols.add(q.get(protein.split("-")[0], None))
                elif "_VAR_" in protein:
                    symbols.add(q.get(protein.split("_VAR_")[0], None))
                else:
                    symbols.add(q.get(protein, None))

            symbols = list(symbols)
            if not any(symbols):
                # no gene symbol for any protein in group
                filtered_groups.append(group)
            elif len(symbols) == 1:
                gene_mapping[symbols[0].upper()] = group
            else:
                gene_mapping.update(
                    {s.upper(): group for s in symbols if s is not None}
                )

    return gene_mapping, filtered_groups


def gsea_preranked(protein_df, ranking_direction):
    """
    Run GSEA on a preranked list of proteins.
    """
    # map input Uniprot IDs to gene symbols
    gene_mapping, filtered_groups = uniprot_ids_to_uppercase_gene_symbols(protein_df)
    # mapping is not 1 - 1
    # what if I have multiple genes for the same e.g. p value? because group got split up and
    # mapped to different genes?

    pre_res = gp.prerank(rnk=rnk,  # or rnk = rnk,
                         gene_sets='KEGG_2016',
                         threads=4,
                         min_size=5,
                         max_size=1000,
                         permutation_num=1000,  # reduce number to speed up testing
                         outdir=None,  # don't write to disk
                         seed=6,
                         verbose=True,  # see what's going on behind the scenes
                         )
    return dict(result_df = pre_res.res2d, ranking = pre_res.ranking, filtered_groups = filtered_groups)


def gsea(protein_df):
    # input example is significant proteins df
    # transform to wide format?
    # long_to_wide(protein_df).transpose()

    # map input Uniprot IDs to gene symbols

    # bring df into the right format
    # TODO: find out if name column is required in df