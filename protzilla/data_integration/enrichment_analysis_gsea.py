import logging

import gseapy as gp
import numpy as np
import pandas as pd
from django.contrib import messages

from protzilla.utilities.transform_dfs import long_to_wide

from .database_query import biomart_query


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
    group_to_genes_mapping = {}
    for group in proteins:
        if ";" not in group:
            symbol = q.get(group, None)
            if symbol is None:
                filtered_groups.append(group)
            else:
                gene_mapping[symbol.upper()] = group
                group_to_genes_mapping[group] = [symbol.upper()]
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
                group_to_genes_mapping[group] = list(symbols)

    return gene_mapping, group_to_genes_mapping, filtered_groups


def gsea_preranked(protein_df, ranking_direction, seed=123):
    """
    Run GSEA on a preranked list of proteins.
    """

    # TODO 182: set logging level for whole django app in beginning
    logging.basicConfig(level=logging.INFO)

    if (
        not isinstance(protein_df, pd.DataFrame)
        or protein_df.shape[1] != 2
        or not "Protein ID" in protein_df.columns
        or not protein_df.iloc[:, 1].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and numeric ranking column (e.g. p values)"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    protein_groups = protein_df["Protein ID"].unique()
    logging.info("Mapping Uniprot IDs to uppercase gene symbols")
    (
        gene_mapping,
        group_to_genes_mapping,
        filtered_groups,
    ) = uniprot_ids_to_uppercase_gene_symbols(protein_groups)

    logging.info("Ranking input")
    rnk = pd.DataFrame(columns=["Gene symbol", "Score"])
    for group in protein_groups:
        if group in filtered_groups:
            continue
        for gene in group_to_genes_mapping[group]:
            # if multiple genes per group, use same score value
            score = protein_df.loc[
                protein_df["Protein ID"] == group, protein_df.columns[1]
            ].values[0]
            rnk.loc[len(rnk)] = [gene, score]

    # if duplicate genes only keep the one with the worse score
    if ranking_direction == "ascending":
        rnk = rnk.groupby("Gene symbol").max()
    else:
        rnk = rnk.groupby("Gene symbol").min()

    # sort rank df by score according to ranking direction
    rnk = rnk.sort_values(by="Score", ascending=ranking_direction == "ascending")

    logging.info("Running GSEA")
    pre_res = gp.prerank(
        rnk=rnk,
        gene_sets=["KEGG_2016"],
        threads=4,
        min_size=5,
        max_size=1000,
        permutation_num=1000,  # reduce number to speed up testing
        outdir=None,  # don't write to disk
        seed=seed,
        verbose=True,
    )

    # TODO: add proteins here again
    return dict(
        enriched_df=pre_res.res2d,
        ranking=pre_res.ranking,
        filtered_groups=filtered_groups,
    )


def gsea(protein_df):
    # , grouping, metadata_df
    # input example is significant proteins df for now
    protein_groups = protein_df["Protein ID"].unique()
    logging.info("Mapping Uniprot IDs to uppercase gene symbols")
    (
        gene_mapping,
        group_to_genes_mapping,
        filtered_groups,
    ) = uniprot_ids_to_uppercase_gene_symbols(protein_groups)

    # bring df into the right format (gene symbols in rows x samples in cols with intensities)
    protein_df_wide = long_to_wide(protein_df).transpose()
    samples = protein_df_wide.columns.tolist()
    column_names = samples + ["Gene symbol"]
    processed_data = []

    for group in protein_groups:
        if group in filtered_groups:
            continue
        for gene in group_to_genes_mapping[group]:
            # if multiple genes per group, use same intensity value
            intensity_values = protein_df_wide.loc[group, :].tolist()
            row_data = intensity_values + [gene]
            processed_data.append(row_data)

    df = pd.DataFrame(processed_data, columns=column_names)
    df.set_index("Gene symbol", inplace=True)

    cls = []
    for sample in samples:
        # TODO: read grouping column from metadata and make cls list
        # group_value = metadata.loc[metadata['Sample'] == sample, 'Group'].iloc[0]
        # cls.append(group_value)
        group_value = protein_df.loc[protein_df["Sample"] == sample, "Group"].iloc[0]
        cls.append(group_value)

    # try not providing name column in df
    # run gsea
    # enrichr libraries are supported by gsea module. Just provide the name
    gs_res = gp.gsea(data=df,  # or data='./P53_resampling_data.txt'
                     gene_sets=["KEGG_2016"],  # or enrichr library names
                     cls=cls,
                     # set permutation_type to phenotype if samples >=15
                     permutation_type='phenotype',
                     permutation_num=1000,  # reduce number to speed up test
                     outdir=None,  # do not write output to disk
                     method='signal_to_noise',
                     threads=4, seed=7)

    return dict(enriched_df=gs_res.res2d, filtered_groups=filtered_groups)