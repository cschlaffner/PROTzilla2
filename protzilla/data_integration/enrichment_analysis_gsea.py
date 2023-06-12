import logging

import gseapy as gp
import numpy as np
import pandas as pd
from django.contrib import messages

from protzilla.utilities.transform_dfs import is_intensity_df, long_to_wide

from .enrichment_analysis_helper import (
    read_protein_or_gene_sets_file,
    uniprot_ids_to_uppercase_gene_symbols,
)


def create_ranked_df(
    protein_groups, protein_df, ranking_direction, group_to_genes, filtered_groups
):
    """
    Creates a ranked dataframe of genes according to values in protein_df and ranking_direction.
    Groups that were filtered out are not included in the ranking.
    If multiple genes exist per group the same ranking value is used for all genes. If duplicate genes
    exist the one with the worse score is kept, so for example for p values the one with the higher p value.

    :param protein_groups: list of protein groups
    :type protein_groups: list
    :param protein_df: dataframe with protein groups and ranking values
    :type protein_df: pd.DataFrame
    :param ranking_direction: direction of ranking, either ascending or descending
    :type ranking_direction: str
    :param group_to_genes: dictionary mapping protein groups to list of genes
    :type group_to_genes: dict
    :param filtered_groups: list of protein groups that were filtered out
    :type filtered_groups: list
    :return: ranked dataframe of genes
    :rtype: pd.DataFrame
    """
    logging.info("Ranking input")
    rnk = pd.DataFrame(columns=["Gene symbol", "Ranking value"])
    for group in protein_groups:
        if group in filtered_groups:
            continue
        for gene in group_to_genes[group]:
            # if multiple genes per group, use same score value
            ranking_value = protein_df.loc[
                protein_df["Protein ID"] == group, protein_df.columns[1]
            ].values[0]
            rnk.loc[len(rnk)] = [gene, ranking_value]

    # if duplicate genes only keep the one with the worse score
    if ranking_direction == "ascending":
        rnk = rnk.groupby("Gene symbol").max()
    else:
        rnk = rnk.groupby("Gene symbol").min()

    # sort rank df by score according to ranking direction
    rnk.sort_values(
        by="Ranking value", ascending=ranking_direction == "ascending", inplace=True
    )
    return rnk


def gsea_preranked(
    protein_df,
    ranking_direction="ascending",
    gene_sets_path=None,
    gene_sets_enrichr=None,
    min_size=15,
    max_size=500,
    number_of_permutations=1000,
    permutation_type="phenotype",
    weighted_score=1.0,
    seed=123,
    **kwargs,
):
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

    if gene_sets_path is not None and gene_sets_path != "":
        gene_sets = read_protein_or_gene_sets_file(gene_sets_path)
        if isinstance(gene_sets, dict) and "messages" in gene_sets:  # an error occurred
            return gene_sets
    elif gene_sets_enrichr is not None and gene_sets_enrichr != []:
        gene_sets = (
            [gene_sets_enrichr]
            if not isinstance(gene_sets_enrichr, list)
            else gene_sets_enrichr
        )
    else:
        msg = "No gene sets provided"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    protein_groups = protein_df["Protein ID"].unique()
    logging.info("Mapping Uniprot IDs to uppercase gene symbols")
    (
        gene_symbols,
        group_to_genes,
        filtered_groups,
    ) = uniprot_ids_to_uppercase_gene_symbols(protein_groups)

    if not gene_symbols:
        msg = "All proteins could not be mapped to gene symbols"
        return dict(
            filtered_groups=filtered_groups,
            messages=[dict(level=messages.ERROR, msg=msg)],
        )

    rnk = create_ranked_df(
        protein_groups,
        protein_df,
        ranking_direction,
        group_to_genes,
        filtered_groups,
    )

    logging.info("Running GSEA")
    try:
        pre_res = gp.prerank(
            rnk=rnk,
            gene_sets=gene_sets,
            min_size=min_size,
            max_size=max_size,
            ascending=ranking_direction == "ascending",
            permutation_num=number_of_permutations,
            permutation_type=permutation_type,
            weighted_score_type=weighted_score,
            outdir=None,
            seed=seed,
            verbose=True,
        )
    except Exception as e:
        msg = "An error occurred while running GSEA. Please check your input and try again."
        return dict(messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))])

    # add proteins to output df
    enriched_df = pre_res.res2d
    enriched_df["Lead_proteins"] = enriched_df["Lead_genes"].apply(
        lambda x: ";".join([gene_symbols[gene] for gene in x.split(";")])
    )

    if filtered_groups:
        msg = "Some proteins could not be mapped to gene symbols and were excluded from the analysis"
        return dict(
            enriched_df=enriched_df,
            ranking=pre_res.ranking,
            filtered_groups=filtered_groups,
            messages=[dict(level=messages.WARNING, msg=msg)],
        )

    return dict(
        enriched_df=enriched_df,
        ranking=pre_res.ranking,
    )


def create_genes_intensity_wide_df(
    protein_df, protein_groups, samples, group_to_genes, filtered_groups
):
    """
    Creates a dataframe with genes in rows and samples in columns with intensity values.
    If multiple proteins map to the same gene, the same intensity value is used for all.
    If duplicate genes exist, the mean of intensities is used.

    :param protein_df: dataframe with protein IDs and intensities
    :type protein_df: pd.DataFrame
    :param protein_groups: list of protein IDs
    :type protein_groups: list
    :param samples: list of sample names
    :type samples: list
    :param group_to_genes: dict with protein IDs as keys and gene symbols as values
    :type group_to_genes: dict
    :param filtered_groups: list of protein IDs that could not be mapped to gene symbols
    :type filtered_groups: list
    :return: dataframe with genes in rows and samples in columns with intensity values
    :rtype: pd.DataFrame
    """
    # (gene symbols in rows x samples in cols with intensities)
    protein_df_wide = long_to_wide(protein_df).transpose()
    column_names = samples + ["Gene symbol"]
    processed_data = []

    for group in protein_groups:
        if group in filtered_groups:
            continue
        for gene in group_to_genes[group]:
            # if multiple genes per group, use same intensity value
            intensity_values = protein_df_wide.loc[group, :].tolist()
            row_data = intensity_values + [gene]
            processed_data.append(row_data)

    df = pd.DataFrame(processed_data, columns=column_names)

    # if duplicate genes exist, use mean of intensities
    df = df.groupby("Gene symbol").mean()
    return df


def gsea(
    protein_df,
    metadata_df,
    grouping,
    gene_sets_path=None,
    gene_sets_enrichr=None,
    min_size=15,
    max_size=500,
    number_of_permutations=1000,
    permutation_type="phenotype",
    ranking_method="log2_ratio_of_classes",
    weighted_score=1.0,
    seed=123,
    **kwargs,
):
    assert grouping in metadata_df.columns, "Grouping column not in metadata df"

    if not is_intensity_df(protein_df):
        msg = "Input must be a dataframe with protein IDs, samples and intensities"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    if gene_sets_path is not None and gene_sets_path != "":
        gene_sets = read_protein_or_gene_sets_file(gene_sets_path)
        if isinstance(gene_sets, dict) and "messages" in gene_sets:  # an error occurred
            return gene_sets
    elif gene_sets_enrichr is not None and gene_sets_enrichr != []:
        gene_sets = (
            [gene_sets_enrichr]
            if not isinstance(gene_sets_enrichr, list)
            else gene_sets_enrichr
        )
    else:
        msg = "No gene sets provided"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    # input example is significant proteins df for now
    protein_groups = protein_df["Protein ID"].unique()
    logging.info("Mapping Uniprot IDs to uppercase gene symbols")
    (
        gene_symbols,
        group_to_genes,
        filtered_groups,
    ) = uniprot_ids_to_uppercase_gene_symbols(protein_groups)

    if not gene_symbols:
        msg = "All proteins could not be mapped to gene symbols"
        return dict(
            filtered_groups=filtered_groups,
            messages=[dict(level=messages.ERROR, msg=msg)],
        )

    samples = protein_df["Sample"].unique().tolist()
    df = create_genes_intensity_wide_df(
        protein_df, protein_groups, samples, group_to_genes, filtered_groups
    )

    cls = []
    for sample in samples:  # make class label list for samples
        group_value = metadata_df.loc[metadata_df["Sample"] == sample, grouping].iloc[0]
        cls.append(group_value)
    if len(set(cls)) != 2:
        msg = "Input samples have to belong to exactly two groups"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    logging.info("Running GSEA")
    try:
        gs_res = gp.gsea(
            data=df,
            gene_sets=gene_sets,
            cls=cls,
            min_size=min_size,
            max_size=max_size,
            method=ranking_method,
            permutation_type=permutation_type,
            permutation_num=number_of_permutations,
            weighted_score_type=weighted_score,
            outdir=None,
            seed=seed,
        )
    except Exception as e:
        msg = "GSEA failed. Please check your input data and parameters."
        return dict(messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))])

    # add proteins to output df
    enriched_df = gs_res.res2d
    enriched_df["Lead_proteins"] = enriched_df["Lead_genes"].apply(
        lambda x: ";".join([gene_symbols[gene] for gene in x.split(";")])
    )

    if filtered_groups:
        msg = "Some proteins could not be mapped to gene symbols and were excluded from the analysis"
        return dict(
            enriched_df=enriched_df,
            filtered_groups=filtered_groups,
            messages=[dict(level=messages.WARNING, msg=msg)],
        )
    return dict(
        enriched_df=enriched_df,
    )
