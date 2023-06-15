import gseapy as gp
import pandas as pd
from django.contrib import messages

from protzilla.constants.logging import logger
from protzilla.utilities.transform_dfs import is_intensity_df, long_to_wide

from .enrichment_analysis_helper import (
    read_protein_or_gene_sets_file,
    uniprot_ids_to_uppercase_gene_symbols,
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
    ranking_method="signal_to_noise",
    weighted_score=1.0,
    seed=123,
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
    :param grouping: column name in metadata_df to group samples by
    :type grouping: str
    :param gene_sets_path: path to file with gene sets
         The file can be a .csv, .txt, .json or .gmt file.
            .gmt files are not parsed because GSEApy can handle them directly.
            Other files must have one set per line with the set name and the proteins.
                - .txt:
                    Set_name: Protein1, Protein2, ...
                    Set_name2: Protein2, Protein3, ...
                - .csv:
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
    :return: dict with enriched dataframe and messages
    :rtype: dict
    """
    assert grouping in metadata_df.columns, "Grouping column not in metadata df"

    if not is_intensity_df(protein_df):
        msg = "Input must be a dataframe with protein IDs, samples and intensities"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    if gene_sets_path:
        gene_sets = read_protein_or_gene_sets_file(gene_sets_path)
        if isinstance(gene_sets, dict) and "messages" in gene_sets:  # an error occurred
            return gene_sets
    elif gene_sets_enrichr:
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
    logger.info("Mapping Uniprot IDs to uppercase gene symbols")
    (
        gene_to_groups,
        group_to_genes,
        filtered_groups,
    ) = uniprot_ids_to_uppercase_gene_symbols(protein_groups)

    if not gene_to_groups:
        msg = "No proteins could be mapped to gene symbols"
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

    # cannot use log2_ratio_of_classes if there are negative values
    if (df < 0).any().any() and ranking_method == "log2_ratio_of_classes":
        msg = "Negative values in the dataframe. Please use a different ranking method."
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    logger.info("Running GSEA")
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
        msg = "GSEA failed. Please check your input data and parameters. Try to lower min_size or increase max_size"
        return dict(messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))])

    # add proteins to output df
    enriched_df = gs_res.res2d
    enriched_df["Lead_proteins"] = enriched_df["Lead_genes"].apply(
        lambda x: ";".join([";".join(gene_to_groups[gene]) for gene in x.split(";")])
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
