import logging

import gseapy as gp
import numpy as np
import pandas as pd
from django.contrib import messages

from protzilla.utilities.transform_dfs import long_to_wide

from .enrichment_analysis_helper import (
    read_protein_or_gene_sets_file,
    uniprot_ids_to_uppercase_gene_symbols,
)


def gsea_preranked(
    protein_df,
    ranking_direction,
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
        group_to_genes_mapping,
        filtered_groups,
    ) = uniprot_ids_to_uppercase_gene_symbols(protein_groups)

    if not gene_symbols:
        msg = "All proteins could not be mapped to gene symbols"
        return dict(
            filtered_groups=filtered_groups,
            messages=[dict(level=messages.ERROR, msg=msg)],
        )

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
        gene_sets=gene_sets,
        min_size=min_size,
        max_size=max_size,
        permutation_num=number_of_permutations,
        permutation_type=permutation_type,
        weighted_score_type=weighted_score,
        outdir=None,
        seed=seed,
        verbose=True,
    )

    # TODO: add proteins here again
    return dict(
        enriched_df=pre_res.res2d,
        ranking=pre_res.ranking,
        filtered_groups=filtered_groups,
    )


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
    # input example is significant proteins df for now
    protein_groups = protein_df["Protein ID"].unique()
    logging.info("Mapping Uniprot IDs to uppercase gene symbols")
    (
        gene_symbols,
        group_to_genes_mapping,
        filtered_groups,
    ) = uniprot_ids_to_uppercase_gene_symbols(protein_groups)

    if not gene_symbols:
        msg = "All proteins could not be mapped to gene symbols"
        return dict(
            filtered_groups=filtered_groups,
            messages=[dict(level=messages.ERROR, msg=msg)],
        )

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

    if set(cls) != 2:
        msg = "Input groups have to be 2!"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    # try not providing name column in df
    # run gsea
    # enrichr libraries are supported by gsea module. Just provide the name
    gs_res = gp.gsea(
        data=df,  # or data='./P53_resampling_data.txt'
        gene_sets=["KEGG_2016"],  # or enrichr library names
        cls=cls,
        # set permutation_type to phenotype if samples >=15
        permutation_type="phenotype",
        permutation_num=1000,  # reduce number to speed up test
        outdir=None,  # do not write output to disk
        method="signal_to_noise",
        seed=seed,
    )
    # TODO: add proteins here again

    return dict(enriched_df=gs_res.res2d, filtered_groups=filtered_groups)
