import os
import time

import gseapy
import numpy as np
import pandas as pd
from django.contrib import messages
from restring import restring

from protzilla.constants.logging import logger

# Import enrichment analysis gsea methods to remove redundant function definition
from .enrichment_analysis_gsea import gsea, gsea_preranked
from .enrichment_analysis_helper import (
    read_protein_or_gene_sets_file,
    uniprot_ids_to_uppercase_gene_symbols,
)


# call methods for precommit hook not to delete imports
def unused():
    gsea_preranked(**{})
    gsea(**{})


last_call_time = None
MIN_WAIT_TIME = 1  # Minimum wait time between STRING API calls in seconds


def get_functional_enrichment_with_delay(protein_list, **string_params):
    """
    This method performs online functional enrichment analysis using the STRING DB API
    via the restring package. It adds a delay between calls to the API to avoid
    exceeding the rate limit.
    :param protein_list: list of protein IDs to perform enrichment analysis for
    :type protein_list: list
    :param string_params: parameters for the restring package
    :type string_params: dict
    :return: dataframe with functional enrichment results
    :rtype: pandas.DataFrame
    """
    global last_call_time
    if last_call_time is not None:
        elapsed_time = time.time() - last_call_time
        if elapsed_time < MIN_WAIT_TIME:
            time.sleep(MIN_WAIT_TIME - elapsed_time)
    result_df = restring.get_functional_enrichment(protein_list, **string_params)
    last_call_time = time.time()
    return result_df


def merge_up_down_regulated_dfs_restring(up_df, down_df):
    """
    A method that merges the results for up- and down-regulated proteins for the restring
    enrichment results. If a category and Term combination is present in both dataframes,
    the one with the lower p-value is kept. The unique proteins (inputGenes column) and the
    unique genes (preferredNames column) of the two input dataframes are merged and the
    number_of_genes column is updated accordingly.

    :param up_df: dataframe with enrichment results for up-regulated proteins
    :type up_df: pandas.DataFrame
    :param down_df: dataframe with enrichment results for down-regulated proteins
    :type down_df: pandas.DataFrame
    :return: merged dataframe
    :rtype: pandas.DataFrame
    """
    logger.info("Merging results for up- and down-regulated proteins")
    up_df.set_index(["category", "term"], inplace=True)
    down_df.set_index(["category", "term"], inplace=True)
    enriched = up_df.copy()
    for gene_set, term in down_df.index:
        if (gene_set, term) in enriched.index:
            if (
                down_df.loc[(gene_set, term), "p_value"]
                < enriched.loc[(gene_set, term), "p_value"]
            ):
                enriched.loc[(gene_set, term)] = down_df.loc[(gene_set, term)]

            proteins = set(up_df.loc[(gene_set, term), "inputGenes"].split(","))
            proteins.update(down_df.loc[(gene_set, term), "inputGenes"].split(","))
            enriched.loc[(gene_set, term), "inputGenes"] = ",".join(list(proteins))

            genes = set(up_df.loc[(gene_set, term), "preferredNames"].split(","))
            genes.update(down_df.loc[(gene_set, term), "preferredNames"].split(","))
            enriched.loc[(gene_set, term), "preferredNames"] = ",".join(list(genes))

            # since inputGenes are proteins this is the number of unique proteins
            enriched.loc[(gene_set, term), "number_of_genes"] = len(proteins)
        else:
            enriched.loc[(gene_set, term), :] = down_df.loc[(gene_set, term), :]

    enriched = enriched.astype(
        {
            "number_of_genes": int,
            "number_of_genes_in_background": int,
            "ncbiTaxonId": int,
        }
    )
    enriched.reset_index(inplace=True)
    return enriched


def go_analysis_with_STRING(
    proteins,
    protein_set_dbs,
    organism,
    background=None,
    direction="both",
):
    """
    This method performs online functional enrichment analysis using the STRING DB API
    via the restring package. Results for up- and down-regulated proteins are aggregated
    and written into a result dataframe.

    :param proteins: dataframe with protein IDs and expression change column
        (e.g. log2 fold change). The expression change column is used to determine
        up- and down-regulated proteins. The magnitude of the expression change is
        not used.
    :type proteins: pandas.DataFrame
    :param protein_set_dbs: list of protein set databases to use for enrichment
        Possible values: KEGG, Component, Function, Process and RCTM
    :type protein_set_dbs: list
    :param organism: organism to use for enrichment as NCBI taxon identifier
        (e.g. Human is 9606)
    :type organism: int
    :param background: path to csv file with background proteins (one protein ID per line).
        If no background is provided, the entire proteome is used as background.
    :type background: str or None
    :param direction: direction of enrichment analysis.
        Possible values: up, down, both
        - up: Log2FC is > 0
        - down: Log2FC is < 0
        - both: functional enrichment info is retrieved for upregulated and downregulated
        proteins separately, but the terms are aggregated for the summary and results
    :type direction: str
    :return: dictionary with enriched dataframe
    :rtype: dict
    """

    out_messages = []
    if (
        not isinstance(proteins, pd.DataFrame)
        or proteins.shape[1] != 2
        or not "Protein ID" in proteins.columns
        or not proteins.iloc[:, 1].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and direction of expression change column (e.g. log2FC)"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    expression_change_col = proteins.drop("Protein ID", axis=1).iloc[:, 0]
    up_protein_list = list(proteins.loc[expression_change_col > 0, "Protein ID"])
    down_protein_list = list(proteins.loc[expression_change_col < 0, "Protein ID"])

    if len(up_protein_list) == 0:
        if direction == "up":
            msg = "No upregulated proteins found. Check your input or select 'down' direction."
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])
        elif direction == "both" and len(down_protein_list) == 0:
            msg = "No proteins found. Check your input."
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No upregulated proteins found. Running analysis for 'down' direction only."
            logger.warning(msg)
            direction = "down"
            out_messages.append(dict(level=messages.WARNING, msg=msg))

    if len(down_protein_list) == 0:
        if direction == "down":
            msg = "No downregulated proteins found. Check your input or select 'up' direction."
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No downregulated proteins found. Running analysis for 'up' direction only."
            logger.warning(msg)
            direction = "up"
            out_messages.append(dict(level=messages.WARNING, msg=msg))

    if protein_set_dbs is None or protein_set_dbs == "":
        protein_set_dbs = ["KEGG", "Component", "Function", "Process", "RCTM"]
        msg = "No protein set databases selected. Using all protein set databases."
        out_messages.append(dict(level=messages.INFO, msg=msg))
    elif not isinstance(protein_set_dbs, list):
        protein_set_dbs = [protein_set_dbs]

    if background == "" or background is None:
        logger.info("No background provided, using entire proteome")
        statistical_background = None
    else:
        # assuming headerless one column file, tab separated
        read = pd.read_csv(
            background,
            sep="\t",
            low_memory=False,
            header=None,
        )
        statistical_background = read.iloc[:, 0].tolist()

    string_params = {
        "species": organism,
        "caller_ID": "PROTzilla",
        "statistical_background": statistical_background,
    }

    # enhancement: add mapping to string API for identifiers before this (dont forget background)
    if direction == "up" or direction == "both":
        logger.info("Starting analysis for up-regulated proteins")

        up_df = get_functional_enrichment_with_delay(up_protein_list, **string_params)
        if len(up_df) <= 1:
            msg = "Error getting enrichment results. Check your input and make sure the organism id is correct."
            out_messages.append(
                dict(level=messages.ERROR, msg=msg, trace=up_df.to_string())
            )
            return dict(messages=out_messages)

        # remove unwanted protein set databases
        up_df.reset_index(inplace=True)
        up_df = up_df[up_df["category"].isin(protein_set_dbs)]
        logger.info("Finished analysis for up-regulated proteins")

    if direction == "down" or direction == "both":
        logger.info("Starting analysis for down-regulated proteins")

        down_df = get_functional_enrichment_with_delay(
            down_protein_list, **string_params
        )
        if len(down_df) <= 1:
            msg = "Error getting enrichment results. Check your input and make sure the organism id is correct."
            out_messages.append(
                dict(level=messages.ERROR, msg=msg, trace=down_df.to_string())
            )
            return dict(messages=out_messages)

        # remove unwanted protein set databases
        down_df.reset_index(inplace=True)
        down_df = down_df[down_df["category"].isin(protein_set_dbs)]
        logger.info("Finished analysis for down-regulated proteins")

    logger.info("Summarizing enrichment results")
    if direction == "both":
        merged_df = merge_up_down_regulated_dfs_restring(up_df, down_df)
    else:
        merged_df = up_df if direction == "up" else down_df
    merged_df.rename(columns={"category": "Gene_set"}, inplace=True)

    if len(out_messages) > 0:
        return dict(messages=out_messages, results=merged_df)

    return {"enriched_df": merged_df}


def merge_up_down_regulated_proteins_results(up_enriched, down_enriched, mapped=False):
    """
    A method that merges the results for up- and down-regulated proteins for the GSEApy
    enrichment results. If a Gene_set and Term combination is present in both dataframes,
    the one with the lower adjusted p-value is kept. Genes are merged and the overlap column
    is updated according to the number of genes.
    If mapped is True, the proteins were mapped to uppercase gene symbols and the proteins
    need to be merged as well.

    :param up_enriched: dataframe with enrichment results for up-regulated proteins
    :type up_enriched: pandas.DataFrame
    :param down_enriched: dataframe with enrichment results for down-regulated proteins
    :type down_enriched: pandas.DataFrame
    :param mapped: whether the proteins were mapped to uppercase gene symbols
    :type mapped: bool
    :return: merged dataframe
    :rtype: pandas.DataFrame
    """

    logger.info("Merging results for up- and down-regulated proteins")
    up_enriched.set_index(["Gene_set", "Term"], inplace=True)
    down_enriched.set_index(["Gene_set", "Term"], inplace=True)
    enriched = up_enriched.copy()
    for gene_set, term in down_enriched.index:
        if (gene_set, term) in enriched.index:
            if (
                down_enriched.loc[(gene_set, term), "Adjusted P-value"]
                < enriched.loc[(gene_set, term), "Adjusted P-value"]
            ):
                enriched.loc[(gene_set, term)] = down_enriched.loc[(gene_set, term)]

            # merge proteins, genes and overlap columns
            if mapped:
                proteins = set(up_enriched.loc[(gene_set, term), "Proteins"].split(";"))
                proteins.update(
                    down_enriched.loc[(gene_set, term), "Proteins"].split(";")
                )
                enriched.loc[(gene_set, term), "Proteins"] = ";".join(list(proteins))

            genes = set(up_enriched.loc[(gene_set, term), "Genes"].split(";"))
            genes.update(down_enriched.loc[(gene_set, term), "Genes"].split(";"))
            enriched.loc[(gene_set, term), "Genes"] = ";".join(list(genes))

            total = str(up_enriched.loc[(gene_set, term), "Overlap"]).split("/")[1]
            enriched.loc[(gene_set, term), "Overlap"] = f"{len(genes)}/{total}"
        else:
            enriched.loc[(gene_set, term), :] = down_enriched.loc[(gene_set, term), :]

    return enriched.reset_index()


def enrichr_helper(protein_list, protein_sets, organism, direction):
    """
    A helper method for the enrichment analysis with Enrichr. It maps the proteins to uppercase gene symbols
    and performs the enrichment analysis with GSEApy. It returns the enrichment results and the groups that
    were filtered out because no gene symbol could be found.

    :param protein_list: list of proteins
    :type protein_list: list
    :param protein_sets: list of protein sets to perform the enrichment analysis with
    :type protein_sets: list
    :param organism: organism
    :type organism: str
    :param direction: direction of regulation ("up" or "down")
    :type direction: str
    :return: enrichment results and filtered groups
    :rtype: tuple
    """
    logger.info("Mapping Uniprot IDs to gene symbols")
    gene_to_groups, _, filtered_groups = uniprot_ids_to_uppercase_gene_symbols(
        protein_list
    )

    if not gene_to_groups:
        msg = (
            "No gene symbols could be found for the proteins. Please check your input."
        )
        return dict(messages=[dict(level=messages.ERROR, msg=msg)]), None

    logger.info(f"Starting analysis for {direction}-regulated proteins")
    try:
        enriched = gseapy.enrichr(
            gene_list=list(gene_to_groups.keys()),
            gene_sets=protein_sets,
            organism=organism,
            outdir=None,
            verbose=True,
        ).results
    except ValueError as e:
        msg = "Something went wrong with the analysis. Please check your inputs."
        return dict(messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))]), None

    enriched["Proteins"] = enriched["Genes"].apply(
        lambda x: ";".join([";".join(gene_to_groups[gene]) for gene in x.split(";")])
    )
    logger.info(f"Finished analysis for {direction}-regulated proteins")
    return enriched, filtered_groups


def go_analysis_with_enrichr(proteins, protein_sets, organism, direction="both"):
    """
    A method that performs online overrepresentation analysis for a given set of proteins
    against a given set of protein sets using the GSEApy package which accesses
    the Enrichr API. Uniprot Protein IDs are converted to uppercase HGNC gene symbols.
    If no match is found, the protein is excluded from the analysis. All excluded proteins
    are returned in a list.

    :param proteins: proteins to be analyzed
    :type proteins: list, series or dataframe
    :param protein_sets: list of Enrichr Library name(s) to use as sets for the enrichment
        (e.g. ['KEGG_2016','KEGG_2013'])
    :type protein_sets: list of str
    :param organism: organism to be used for the analysis, must be one of the following
        supported by Enrichr: "human", "mouse", "yeast", "fly", "fish", "worm"
    :type organism: str
    :param direction: direction of enrichment analysis.
        Possible values: up, down, both
        - up: Log2FC is > 0
        - down: Log2FC is < 0
        - both: functional enrichment info is retrieved for upregulated and downregulated
        proteins separately, but the terms are aggregated for the resulting dataframe
    :type direction: str
    :return: dictionary with results and filtered groups
    :rtype: dict
    """
    # enhancement: protein_sets are categorical for now, could also be custom file upload later
    #       background parameter would work then (with uploaded file)

    out_messages = []
    if (
        not isinstance(proteins, pd.DataFrame)
        or proteins.shape[1] != 2
        or not "Protein ID" in proteins.columns
        or not proteins.iloc[:, 1].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and direction of expression change column (e.g. log2FC)"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    expression_change_col = proteins.drop("Protein ID", axis=1).iloc[:, 0]
    up_protein_list = list(proteins.loc[expression_change_col > 0, "Protein ID"])
    down_protein_list = list(proteins.loc[expression_change_col < 0, "Protein ID"])

    if not up_protein_list:
        if direction == "up":
            msg = "No upregulated proteins found. Check your input or select 'down' direction."
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])
        elif direction == "both" and not down_protein_list:
            msg = "No proteins found. Check your input."
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No upregulated proteins found. Running analysis for 'down' direction only."
            logger.warning(msg)
            direction = "down"
            out_messages.append(dict(level=messages.WARNING, msg=msg))

    if not down_protein_list:
        if direction == "down":
            msg = "No downregulated proteins found. Check your input or select 'up' direction."
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No downregulated proteins found. Running analysis for 'up' direction only."
            logger.warning(msg)
            direction = "up"
            out_messages.append(dict(level=messages.WARNING, msg=msg))

    if direction == "up" or direction == "both":
        up_enriched, up_filtered_groups = enrichr_helper(
            up_protein_list, protein_sets, organism, "up"
        )
        if isinstance(up_enriched, dict):  # error occurred
            return up_enriched

    if direction == "down" or direction == "both":
        down_enriched, down_filtered_groups = enrichr_helper(
            down_protein_list, protein_sets, organism, "down"
        )
        if isinstance(down_enriched, dict):  # error occurred
            return down_enriched

    if direction == "both":
        filtered_groups = up_filtered_groups + down_filtered_groups
        enriched = merge_up_down_regulated_proteins_results(
            up_enriched, down_enriched, mapped=True
        )
    else:
        enriched = up_enriched if direction == "up" else down_enriched
        filtered_groups = (
            up_filtered_groups if direction == "up" else down_filtered_groups
        )

    if filtered_groups:
        msg = "Some proteins could not be mapped to gene symbols and were excluded from the analysis"
        out_messages.append(dict(level=messages.WARNING, msg=msg))
        return dict(
            results=enriched,
            filtered_groups=filtered_groups,
            messages=out_messages,
        )

    return {
        "results": enriched,
        "messages": out_messages,
    }


def go_analysis_offline(proteins, protein_sets_path, background=None, direction="both"):
    """
    A method that performs offline overrepresentation analysis for a given set of proteins
    against a given set of protein sets using the GSEApy package.
    For the analysis a hypergeometric test is used.

    :param proteins: proteins to be analyzed
    :type proteins: list, series or dataframe
    :param protein_sets_path: path to file containing protein sets. The identifers
        in the protein_sets should be the same type as the backgrounds and the proteins.

        This could be any of the following file types: .gmt, .txt, .csv, .json
        - .txt:
            Set_name: Protein1, Protein2, ...
            Set_name2: Protein2, Protein3, ...
        - .csv:
            Set_name, Protein1, Protein2, ...
            Set_name2, Protein2, Protein3, ...
        - .json:
            {Set_name: [Protein1, Protein2, ...], Set_name2: [Protein2, Protein3, ...]}
    :type protein_sets_path: str
    :param background: background proteins to be used for the analysis. If no
        background is provided, all proteins in protein sets are used.
        The background is defined by your experiment.
    :type background: str or None
    :param direction: direction of enrichment analysis.
        Possible values: up, down, both
        - up: Log2FC is > 0
        - down: Log2FC is < 0
        - both: functional enrichment info is retrieved for upregulated and downregulated
        proteins separately, but the terms are aggregated for the resulting dataframe
    :type direction: str
    :return: dictionary with results dataframe
    :rtype: dict
    """
    # enhancement: proteins could also be a number input (or an uploaded file)
    # enhancement: make sure ID type for all inputs match
    out_messages = []
    if (
        not isinstance(proteins, pd.DataFrame)
        or proteins.shape[1] != 2
        or not "Protein ID" in proteins.columns
        or not proteins.iloc[:, 1].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and direction of expression change column (e.g. log2FC)"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    expression_change_col = proteins.drop("Protein ID", axis=1).iloc[:, 0]
    up_protein_list = list(proteins.loc[expression_change_col > 0, "Protein ID"])
    down_protein_list = list(proteins.loc[expression_change_col < 0, "Protein ID"])

    if not up_protein_list:
        if direction == "up":
            msg = "No upregulated proteins found. Check your input or select 'down' direction."
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])
        elif direction == "both" and len(down_protein_list) == 0:
            msg = "No proteins found. Check your input."
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No upregulated proteins found. Running analysis for 'down' direction only."
            logger.warning(msg)
            direction = "down"
            out_messages.append(dict(level=messages.WARNING, msg=msg))

    if not down_protein_list:
        if direction == "down":
            msg = "No downregulated proteins found. Check your input or select 'up' direction."
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No downregulated proteins found. Running analysis for 'up' direction only."
            logger.warning(msg)
            direction = "up"
            out_messages.append(dict(level=messages.WARNING, msg=msg))

    protein_sets = read_protein_or_gene_sets_file(protein_sets_path)
    if (
        isinstance(protein_sets, dict) and "messages" in protein_sets
    ):  # file could not be read successfully
        return protein_sets

    if background == "" or background is None:
        logger.info("No background provided, using all proteins in protein sets")
        background = None
    else:
        file_extension = os.path.splitext(background)[1]
        if file_extension == ".csv":
            background = pd.read_csv(
                background, sep="\t", low_memory=False, header=None
            )
            # if multiple columns, use first
            background = background.iloc[:, 0].tolist()
        elif file_extension == ".txt":
            with open(background, "r") as f:
                background = [line.strip() for line in f]
        else:
            msg = "Invalid file type for background. Must be .csv, .txt or no upload"
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    if direction == "up" or direction == "both":
        logger.info("Starting analysis for up-regulated proteins")
        # gene set and gene list identifiers need to match
        try:
            up_enriched = gseapy.enrich(
                gene_list=up_protein_list,
                gene_sets=protein_sets,
                background=background,
                outdir=None,
                verbose=True,
            ).results
        except ValueError as e:
            msg = "Something went wrong with the analysis. Please check your inputs."
            return dict(messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))])

        logger.info("Finished analysis for up-regulated proteins")

    if direction == "down" or direction == "both":
        logger.info("Starting analysis for down-regulated proteins")
        # gene set and gene list identifiers need to match
        try:
            down_enriched = gseapy.enrich(
                gene_list=down_protein_list,
                gene_sets=protein_sets,
                background=background,
                outdir=None,
                verbose=True,
            ).results
        except ValueError as e:
            msg = "Something went wrong with the analysis. Please check your inputs."
            return dict(messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))])

        logger.info("Finished analysis for down-regulated proteins")

    if direction == "both":
        enriched = merge_up_down_regulated_proteins_results(
            up_enriched, down_enriched, mapped=False
        )
    else:
        enriched = up_enriched if direction == "up" else down_enriched

    return {"results": enriched}
