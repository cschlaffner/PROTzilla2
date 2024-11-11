import logging

import gseapy
import numpy as np
import pandas as pd

from protzilla.constants.protzilla_logging import logger
from protzilla.utilities import default_intensity_column
from protzilla.utilities.transform_dfs import is_intensity_df, long_to_wide

from .enrichment_analysis_helper import read_protein_or_gene_sets_file


def create_ranked_df(
    protein_groups,
    protein_df,
    ranking_column,
    ranking_direction,
    protein_group_to_genes,
    filtered_groups,
):
    """
    Creates a ranked dataframe of genes according to values in ranking_column from protein_df and ranking_direction.
    Groups that were filtered out are not included in the ranking.
    If multiple genes exist per group the same ranking value is used for all genes. If duplicate genes
    exist the one with the worse score is kept, so for example for p values the one with the higher p value.

    :param protein_groups: list of protein groups
    :type protein_groups: list
    :param protein_df: dataframe with protein groups and ranking values
    :type protein_df: pd.DataFrame
    :param ranking_column: column name of ranking column
    :type ranking_column: str
    :param ranking_direction: direction of ranking, either ascending or descending
    :type ranking_direction: str
    :param protein_group_to_genes: dictionary mapping protein groups to list of genes
    :type protein_group_to_genes: dict
    :param filtered_groups: list of protein groups that were filtered out
    :type filtered_groups: list

    :return: ranked dataframe of genes
    :rtype: pd.DataFrame
    """
    logger.info("Ranking input")
    # remove all columns but "Protein ID" and ranking column
    protein_df = protein_df[["Protein ID", ranking_column]]
    protein_df.drop_duplicates(subset="Protein ID", inplace=True)

    gene_values = {"Gene symbol": [], "Ranking value": []}
    for group in protein_groups:
        if group in filtered_groups:
            continue
        for gene in protein_group_to_genes[group]:
            # if multiple genes per group, use same score value
            ranking_value = protein_df.loc[
                protein_df["Protein ID"] == group, ranking_column
            ].values[0]
            gene_values["Gene symbol"].append(gene)
            gene_values["Ranking value"].append(ranking_value)
    ranked_df = pd.DataFrame(gene_values)
    # if duplicate genes only keep the one with the worse score
    if ranking_direction == "ascending":
        ranked_df = ranked_df.groupby("Gene symbol").max()
    else:
        ranked_df = ranked_df.groupby("Gene symbol").min()

    # sort rank df by score according to ranking direction
    ranked_df.sort_values(
        by="Ranking value", ascending=ranking_direction == "ascending", inplace=True
    )
    return ranked_df


# TODO we need to adjust the method to use the gene_mapping_df
def gsea_preranked(
    protein_df,
    gene_mapping_df,
    ranking_column=None,
    ranking_direction="ascending",
    gene_sets_path=None,
    gene_sets_enrichr=None,
    min_size=15,
    max_size=500,
    number_of_permutations=1000,
    permutation_type="phenotype",
    weighted_score=1.0,
    seed=123,
    threads=4,
    **kwargs,
):
    """
    Ranks proteins by a provided value column according to ranking_direction and
    maps the Uniprot IDs to uppercase gene symbols.
    Protein groups that could not be mapped are not included in the ranking.
    If multiple genes exist per group the same ranking value is used for all genes.
    If duplicate genes exist the one with the worse score is kept.
    Then runs GSEA on it.
    If gene_sets_path is provided, reads in gene sets from file, otherwise uses
    gene sets libraries provided by Enrichr.

    :param protein_df: dataframe with protein IDs and ranking values
    :type protein_df: pd.DataFrame
    :param gene_mapping_df: dataframe with protein IDs and gene symbols
    :type gene_mapping_df: pandas.DataFrame
    :param ranking_column: column name of ranking column in protein_df
    :type ranking_column: str
    :param ranking_direction: direction of ranking for sorting, either ascending or descending
        (ascending - smaller values are better, descending - larger values are better)
    :type ranking_direction: str
    :param gene_sets_path: path to file with gene sets
        The file can be a .csv, .txt, .json or .gmt file.
        .gmt files are not parsed because GSEApy can handle them directly.
        Other files must have one set per line with the set name and the proteins.
            - .txt: Setname or identifier followed by a tab-separated list of genes
                Set_name    Protein1    Protein2...
                Set_name    Protein1    Protein2...
            - .csv: Setname or identifier followed by a comma-separated list of genes
                Set_name, Protein1, Protein2, ...
                Set_name2, Protein2, Protein3, ...
            - .json:
                {Set_name: [Protein1, Protein2, ...], Set_name2: [Protein2, Protein3, ...]}
    :type gene_sets_path: str
    :param gene_sets_enrichr: list of gene set library names from Enrichr
    :type gene_sets_enrichr: list
    :param min_size: Minimum number of genes from gene set also in data set
    :type min_size: int
    :param max_size: Maximum number of genes from gene set also in data set
    :type max_size: int
    :param number_of_permutations: Number of permutations
    :type number_of_permutations: int
    :param permutation_type: Permutation type, either phenotype or gene_set
         (if samples >=15 set to phenotype)
    :type permutation_type: str
    :param weighted_score: Weighted score for the enrichment score calculation, recommended values: 0, 1, 1.5 or 2
    :type weighted_score: float
    :param seed: Random seed
    :type seed: int
    :param threads: Number of threads
    :type threads: int

    :return: dictionary with results dataframe, ranking, enrichment detail dataframe per enriched gene set and messages
    :rtype: dict
    """
    if (
        not isinstance(protein_df, pd.DataFrame)
        or "Protein ID" not in protein_df.columns
        or ranking_column not in protein_df.columns
        or not protein_df[ranking_column].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and numeric ranking column (e.g. p values)"
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

    if gene_sets_path:
        gene_sets = read_protein_or_gene_sets_file(gene_sets_path)
        if isinstance(gene_sets, dict) and "messages" in gene_sets:  # an error occurred
            return gene_sets
    elif gene_sets_enrichr:
        if not isinstance(gene_sets_enrichr, list):
            gene_sets = [gene_sets_enrichr]
        else:
            gene_sets = gene_sets_enrichr
    else:
        msg = "No gene sets provided"
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

    protein_groups = protein_df["Protein ID"].unique().tolist()

    protein_group_to_genes = (
        gene_mapping_df.groupby("Protein ID")["Gene"].apply(list).to_dict()
    )
    gene_to_protein_groups = (
        gene_mapping_df.groupby("Gene")["Protein ID"].apply(list).to_dict()
    )
    filtered_groups = list(set(protein_groups) - set(protein_group_to_genes.keys()))

    if not gene_to_protein_groups:
        msg = "No proteins could be mapped to gene symbols"
        return dict(
            filtered_groups=filtered_groups,
            messages=[dict(level=logging.ERROR, msg=msg)],
        )

    ranked_df = create_ranked_df(
        protein_groups,
        protein_df,
        ranking_column,
        ranking_direction,
        protein_group_to_genes,
        filtered_groups,
    )

    logger.info("Running GSEA")
    try:
        preranked_result = gseapy.prerank(
            rnk=ranked_df,
            gene_sets=gene_sets,
            min_size=min_size,
            max_size=max_size,
            ascending=ranking_direction == "ascending",
            permutation_num=number_of_permutations,
            permutation_type=permutation_type,
            weighted_score_type=weighted_score,
            outdir=None,
            seed=seed,
            threads=threads,
            verbose=True,
            no_plot=True,
        )
    except Exception as e:
        msg = "An error occurred while running GSEA. Please check your input and try again. Try to lower min_size or increase max_size."
        return dict(messages=[dict(level=logging.ERROR, msg=msg, trace=str(e))])

    # add proteins to output df
    enrichment_df = preranked_result.res2d
    enrichment_df["Lead_proteins"] = enrichment_df["Lead_genes"].apply(
        lambda x: ";".join(
            ";".join(gene_to_protein_groups[gene]) for gene in x.split(";")
        )
    )

    out_dict = {
        "enrichment_df": enrichment_df,
        "ranking": preranked_result.ranking,
    }
    out_dict.update(preranked_result.results)

    if filtered_groups:
        msg = "Some proteins could not be mapped to gene symbols and were excluded from the analysis"
        out_dict["filtered_groups"] = filtered_groups
        out_dict["messages"] = [dict(level=logging.WARNING, msg=msg)]
    return out_dict


def create_genes_intensity_wide_df(
    protein_df, protein_groups, samples, protein_group_to_genes, filtered_groups
):
    """
    Creates a wide dataframe with genes in rows and samples in columns with intensity values.
    This is done by transforming the protein_df and using the protein_group_to_genes dict
    to map the protein IDs to gene names.
    Protein groups that could not be mapped to gene symbols will not be included in the dataframe.
    If a protein group maps to multiple genes, the same intensity values are used for all.
    If multiple groups map to the same gene, the mean of intensities of the respective protein groups is used.

    :param protein_df: dataframe with protein IDs and intensities
    :type protein_df: pd.DataFrame
    :param protein_groups: list of protein IDs
    :type protein_groups: list
    :param samples: list of sample names
    :type samples: list
    :param protein_group_to_genes: dict with protein IDs as keys and gene symbols as values
    :type protein_group_to_genes: dict
    :param filtered_groups: list of protein IDs that could not be mapped to gene symbols
    :type filtered_groups: list

    :return: dataframe with genes in rows and samples in columns with intensity values
    :rtype: pd.DataFrame
    """
    # (gene symbols in rows x samples in cols with intensities)
    protein_df_wide = long_to_wide(protein_df).transpose()
    column_names = ["Gene symbol"] + samples
    processed_data = []

    for group in protein_groups:
        if group in filtered_groups:
            continue
        for gene in protein_group_to_genes[group]:
            # if multiple genes per group, use same intensity value
            intensity_values = protein_df_wide.loc[group, :].tolist()
            row_data = [gene] + intensity_values
            processed_data.append(row_data)

    df = pd.DataFrame(processed_data, columns=column_names)

    # if duplicate genes exist, use mean of intensities
    df = df.groupby("Gene symbol").mean()
    return df


def gsea(
    protein_df,
    metadata_df,
    grouping,
    gene_mapping_df,
    group1=None,
    group2=None,
    gene_sets_path=None,
    gene_sets_enrichr=None,
    min_size=15,
    max_size=500,
    number_of_permutations=1000,
    permutation_type="phenotype",
    ranking_method="signal_to_noise",
    weighted_score=1.0,
    seed=123,
    threads=4,
    **kwargs,
):
    """
    Performs Gene Set Enrichment Analysis (GSEA) on a dataframe with protein IDs, samples and intensities.
    To do this Protein IDs are mapped to uppercase gene symbols.
    The dataframe is converted to a dataframe with genes in rows and samples in columns with intensity values.
    If multiple protein groups map to the same gene, the same intensity value is used for all.
    If duplicate genes exist, the mean of intensities is used.

    :param protein_df: dataframe with protein IDs, samples and intensities
    :type protein_df: pd.DataFrame
    :param metadata_df: dataframe with metadata
    :type metadata_df: pd.DataFrame
    :param gene_mapping_df: dataframe with protein IDs and gene symbols
    :type gene_mapping_df: pd.DataFrame
    :param grouping: column name in metadata_df to group samples by
    :type grouping: str
    :param group1: name of group 1
    :type group1: str
    :param group2: name of group 2
    :type group2: str
    :param gene_sets_path: path to file with gene sets
         The file can be a .csv, .txt, .json or .gmt file.
        .gmt files are not parsed because GSEApy can handle them directly.
        Other files must have one set per line with the set name and the proteins.
            - .txt: Setname or identifier followed by a tab-separated list of genes
                Set_name    Protein1    Protein2...
                Set_name    Protein1    Protein2...
            - .csv: Setname or identifier followed by a comma-separated list of genes
                Set_name, Protein1, Protein2, ...
                Set_name2, Protein2, Protein3, ...
            - .json:
                {Set_name: [Protein1, Protein2, ...], Set_name2: [Protein2, Protein3, ...]}
    :type gene_sets_path: str
    :param gene_sets_enrichr: list of gene set library names to use from Enrichr
    :type gene_sets_enrichr: list
    :param min_size: minimum number of proteins from a gene set that must be present in the data
    :type min_size: int
    :param max_size: maximum number of proteins from a gene set that must be present in the data
    :type max_size: int
    :param number_of_permutations: number of permutations to perform
    :type number_of_permutations: int
    :param permutation_type: type of permutations to perform, phenotype or gene_set
         (if samples >=15 set to phenotype)
    :type permutation_type: str
    :param ranking_method: method to rank proteins by, default: 'signal_to_noise'
        refer to GSEApy documentation for more information
               1. 'signal_to_noise'
                    You must have at least three samples for each phenotype to use this metric.

               2. 't_test'
                    You must have at least three samples for each phenotype to use this metric.

               3. 'ratio_of_classes' (also referred to as fold change).

               4. 'diff_of_classes' (fold change for nature scale data)

               5. 'log2_ratio_of_classes'
    :type ranking_method: str
    :param weighted_score: Weighted score for the enrichment score calculation,
        recommended values: 0, 1, 1.5 or 2
    :type weighted_score: float
    :param seed: Random seed
    :type seed: int
    :param threads: Number of threads to use
    :type threads: int

    :return: dict with enriched dataframe, ranking, enrichment detail dataframe per enriched gene set and messages
    :rtype: dict
    """
    if grouping not in metadata_df.columns:
        msg = "Grouping column not in metadata df"
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

    groups = metadata_df[grouping].unique().tolist()
    if group1 not in groups or group2 not in groups:
        msg = "Group names should be in metadata df but are not"
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

    if not is_intensity_df(protein_df):
        msg = "Input must be a dataframe with protein IDs, samples and intensities"
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

    intensity_name = default_intensity_column(protein_df)
    # cannot use log2_ratio_of_classes if there are negative values
    if (
        ranking_method == "log2_ratio_of_classes"
        and (protein_df[intensity_name] < 0).any()
    ):
        msg = "Negative values in the dataframe. Please use a different ranking method."
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

    if gene_sets_path:
        gene_sets = read_protein_or_gene_sets_file(gene_sets_path)
        if isinstance(gene_sets, dict) and "messages" in gene_sets:  # an error occurred
            return gene_sets
    elif gene_sets_enrichr:
        if not isinstance(gene_sets_enrichr, list):
            gene_sets = [gene_sets_enrichr]
        else:
            gene_sets = gene_sets_enrichr
    else:
        msg = "No gene sets provided"
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

    # only keep samples from the two groups
    group_samples = metadata_df.loc[
        metadata_df[grouping].isin([group1, group2]), "Sample"
    ].tolist()
    protein_df = protein_df[protein_df["Sample"].isin(group_samples)]
    samples = protein_df["Sample"].unique().tolist()
    protein_groups = protein_df["Protein ID"].unique().tolist()

    protein_group_to_genes = (
        gene_mapping_df.groupby("Protein ID")["Gene"].apply(list).to_dict()
    )
    gene_to_protein_groups = (
        gene_mapping_df.groupby("Gene")["Protein ID"].apply(list).to_dict()
    )
    filtered_groups = list(set(protein_groups) - set(protein_group_to_genes.keys()))

    if not gene_to_protein_groups:
        msg = "No proteins could be mapped to gene symbols"
        return dict(
            filtered_groups=filtered_groups,
            messages=[dict(level=logging.ERROR, msg=msg)],
        )

    df = create_genes_intensity_wide_df(
        protein_df, protein_groups, samples, protein_group_to_genes, filtered_groups
    )

    class_labels = []
    for sample in samples:
        group_label = metadata_df.loc[metadata_df["Sample"] == sample, grouping].iloc[0]
        class_labels.append(group_label)

    logger.info("Running GSEA")
    try:
        gsea_result = gseapy.gsea(
            data=df,
            gene_sets=gene_sets,
            cls=class_labels,
            min_size=min_size,
            max_size=max_size,
            method=ranking_method,
            permutation_type=permutation_type,
            permutation_num=number_of_permutations,
            weighted_score_type=weighted_score,
            outdir=None,
            seed=seed,
            threads=threads,
            verbose=True,
            no_plot=True,
        )
    except Exception as e:
        msg = "GSEA failed. Please check your input data and parameters. Try to lower min_size or increase max_size"
        return dict(messages=[dict(level=logging.ERROR, msg=msg, trace=str(e))])

    # add proteins to output df
    enrichment_df = gsea_result.res2d
    enrichment_df["Lead_proteins"] = enrichment_df["Lead_genes"].apply(
        lambda x: ";".join(
            [";".join(gene_to_protein_groups[gene]) for gene in x.split(";")]
        )
    )

    out_dict = {
        "enrichment_df": enrichment_df,
        "ranking": gsea_result.ranking,
    }
    out_dict.update(gsea_result.results)

    if filtered_groups:
        msg = "Some proteins could not be mapped to gene symbols and were excluded from the analysis"
        out_dict["filtered_groups"] = filtered_groups
        out_dict["messages"] = [dict(level=logging.WARNING, msg=msg)]
    return out_dict
