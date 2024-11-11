import logging
import time

import gseapy
import numpy as np
import pandas as pd
from restring import restring

from protzilla.constants.protzilla_logging import logger
from protzilla.data_integration.database_query import biomart_database
from protzilla.utilities.utilities import clean_uniprot_id

# Import enrichment analysis gsea methods to remove redundant function definition
from .enrichment_analysis_gsea import gsea, gsea_preranked
from .enrichment_analysis_helper import (
    map_to_STRING_ids,
    read_background_file,
    read_protein_or_gene_sets_file,
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
    A method that merges the results for up- and downregulated proteins for the restring
    enrichment results. If a category and Term combination is present in both dataframes,
    the one with the higher p-value is kept. The unique proteins (inputGenes column) and the
    unique genes (preferredNames column) of the two input dataframes are merged and the
    number_of_genes column is updated accordingly.

    :param up_df: dataframe with enrichment results for upregulated proteins
    :type up_df: pandas.DataFrame
    :param down_df: dataframe with enrichment results for downregulated proteins
    :type down_df: pandas.DataFrame

    :return: merged dataframe
    :rtype: pandas.DataFrame
    """
    logger.info("Merging results for up- and downregulated proteins")
    up_df.set_index(["category", "term"], inplace=True)
    down_df.set_index(["category", "term"], inplace=True)
    enriched = up_df.copy()
    for gene_set, term in down_df.index:
        if (gene_set, term) in enriched.index:
            if (
                down_df.loc[(gene_set, term), "p_value"]
                > enriched.loc[(gene_set, term), "p_value"]
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


def GO_analysis_with_STRING(
    proteins_df,
    organism,
    gene_sets_restring=None,
    differential_expression_col=None,
    differential_expression_threshold=0,
    background_path=None,
    direction="both",
):
    """
    This method performs online functional enrichment analysis using the STRING DB API
    via the restring package. Results for up- and downregulated proteins are aggregated
    and written into a result dataframe.

    :param proteins_df: dataframe with protein IDs and expression change column
        (e.g. log2 fold change). The expression change column is used to determine
        up- and downregulated proteins. The magnitude of the expression change is
        not used.
    :type proteins_df: pandas.DataFrame
    :param gene_sets_restring: list of knowledge databases to use for enrichment
        Possible values: KEGG, Component, Function, Process and RCTM
    :type gene_sets_restring: list
    :param organism: organism to use for enrichment as NCBI taxon identifier
        (e.g. Human is 9606)
    :type organism: int
    :param differential_expression_col: name of the column in the proteins dataframe that contains values for
        direction of expression change.
    :type differential_expression_col: str
    :param differential_expression_threshold: threshold for differential expression.
        Proteins with values above this threshold are considered upregulated, proteins with
        differential_expression_colvalues below this threshold are considered downregulated.
        If "log" is in the name of differential_expression_col, the threshold is applied symmetrically:
        e.g. log2_fold_change > threshold, the protein is upregulated, if log2_fold_change < -threshold,
        the protein is downregulated.
    :type differential_expression_threshold: float
    :param background_path: path to txt or csv file with background proteins (one protein ID per line).
        If no background is provided, the entire proteome is used as background.
    :type background_path: str or None
    :param direction: direction of enrichment analysis.
        Possible values: up, down, both
        - up: upregulated proteins only
        - down: downregulated proteins only
        - both: functional enrichment info is retrieved for upregulated and downregulated
        proteins separately, but the terms are aggregated for the result dataframe
    :type direction: str

    :return: dictionary with enrichment dataframe
    :rtype: dict
    """

    out_messages = []
    if (
        not isinstance(proteins_df, pd.DataFrame)
        or "Protein ID" not in proteins_df.columns
        or differential_expression_col not in proteins_df.columns
        or not proteins_df[differential_expression_col].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and direction of expression change column (e.g. log2FC)"
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

    # remove all columns but "Protein ID" and differential_expression_col column
    proteins_df = proteins_df[["Protein ID", differential_expression_col]]
    proteins_df.drop_duplicates(subset="Protein ID", inplace=True)
    expression_change_col = proteins_df[differential_expression_col]

    # split protein list according to direction of expression change and threshold
    if "log" in differential_expression_col:
        up_threshold = differential_expression_threshold
        down_threshold = -differential_expression_threshold
    else:
        up_threshold = differential_expression_threshold
        down_threshold = differential_expression_threshold
    up_protein_list = list(
        proteins_df.loc[expression_change_col > up_threshold, "Protein ID"]
    )
    down_protein_list = list(
        proteins_df.loc[expression_change_col < down_threshold, "Protein ID"]
    )

    if len(up_protein_list) == 0:
        if direction == "up":
            msg = "No upregulated proteins found. Check your input or select 'down' direction."
            return dict(messages=[dict(level=logging.ERROR, msg=msg)])
        elif direction == "both" and len(down_protein_list) == 0:
            msg = "No proteins found for given threshold. Check your input. "
            return dict(messages=[dict(level=logging.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No upregulated proteins found. Running analysis for 'down' direction only."
            logger.warning(msg)
            direction = "down"
            out_messages.append(dict(level=logging.WARNING, msg=msg))

    if len(down_protein_list) == 0:
        if direction == "down":
            msg = "No downregulated proteins found. Check your input or select 'up' direction."
            return dict(messages=[dict(level=logging.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No downregulated proteins found. Running analysis for 'up' direction only."
            logger.warning(msg)
            direction = "up"
            out_messages.append(dict(level=logging.WARNING, msg=msg))

    if not gene_sets_restring:
        gene_sets_restring = ["KEGG", "Component", "Function", "Process", "RCTM"]
        msg = "No knowledge databases selected. Using all knowledge databases."
        out_messages.append(dict(level=logging.INFO, msg=msg))
    elif not isinstance(gene_sets_restring, list):
        gene_sets_restring = [gene_sets_restring]

    statistical_background = read_background_file(background_path)
    if (
        isinstance(statistical_background, dict)
        and "messages" in statistical_background
    ):
        return statistical_background
    if statistical_background is None:
        logger.info("No background provided, using entire proteome")
    else:
        # split and clean statistical background
        background_ids = set()
        for protein_group in statistical_background:
            background_ids.update(map(clean_uniprot_id, protein_group.split(";")))
        statistical_background = list(background_ids)
        # STRING IDs are required for background
        statistical_background = map_to_STRING_ids(statistical_background, organism)

    string_params = {
        "species": organism,
        "statistical_background": statistical_background,
    }

    # enhancement: add mapping to string API for identifiers before this (dont forget background)
    if direction == "up" or direction == "both":
        logger.info("Starting analysis for upregulated proteins")

        up_cleaned_ids = set()
        for protein_group in up_protein_list:
            up_cleaned_ids.update(map(clean_uniprot_id, protein_group.split(";")))

        up_df = get_functional_enrichment_with_delay(
            list(up_cleaned_ids), **string_params
        )
        if up_df.empty or not up_df.values.any() or "ErrorMessage" in up_df.columns:
            msg = "Error getting enrichment results. Check your input and make sure the organism id is correct."
            out_messages.append(
                dict(level=logging.ERROR, msg=msg, trace=up_df.to_string())
            )
            return dict(messages=out_messages)

        # remove unwanted protein set databases
        up_df.reset_index(inplace=True)
        up_df = up_df[up_df["category"].isin(gene_sets_restring)]
        logger.info("Finished analysis for upregulated proteins")

    if direction == "down" or direction == "both":
        logger.info("Starting analysis for downregulated proteins")

        down_cleaned_ids = set()
        for protein_group in down_protein_list:
            down_cleaned_ids.update(map(clean_uniprot_id, protein_group.split(";")))

        down_df = get_functional_enrichment_with_delay(
            list(down_cleaned_ids), **string_params
        )
        if (
            down_df.empty
            or not down_df.values.any()
            or "ErrorMessage" in down_df.columns
        ):
            msg = "Error getting enrichment results. Check your input and make sure the organism id is correct."
            out_messages.append(
                dict(level=logging.ERROR, msg=msg, trace=down_df.to_string())
            )
            return dict(messages=out_messages)

        # remove unwanted protein set databases
        down_df.reset_index(inplace=True)
        down_df = down_df[down_df["category"].isin(gene_sets_restring)]
        logger.info("Finished analysis for downregulated proteins")

    logger.info("Summarizing enrichment results")
    if direction == "both":
        merged_df = merge_up_down_regulated_dfs_restring(up_df, down_df)
    else:
        merged_df = up_df if direction == "up" else down_df
    merged_df.rename(columns={"category": "Gene_set"}, inplace=True)

    if len(out_messages) > 0:
        return dict(messages=out_messages, enrichment_df=merged_df)

    return {"enrichment_df": merged_df}


def merge_up_down_regulated_dfs_gseapy(up_enriched, down_enriched):
    """
    A method that merges the results for up- and downregulated proteins for the GSEApy
    enrichment results. If a Gene_set and Term combination is present in both dataframes,
    the one with the higher adjusted p-value is kept. Proteins were mapped to uppercase gene
    symbols and need to be merged. Genes are merged and the overlap column
    is updated according to the number of genes.


    :param up_enriched: dataframe with enrichment results for upregulated proteins
    :type up_enriched: pandas.DataFrame
    :param down_enriched: dataframe with enrichment results for downregulated proteins
    :type down_enriched: pandas.DataFrame

    :return: merged dataframe
    :rtype: pandas.DataFrame
    """

    logger.info("Merging results for up- and downregulated proteins")
    up_enriched.set_index(["Gene_set", "Term"], inplace=True)
    down_enriched.set_index(["Gene_set", "Term"], inplace=True)
    enriched = up_enriched.copy()
    for gene_set, term in down_enriched.index:
        if (gene_set, term) in enriched.index:
            if (
                down_enriched.loc[(gene_set, term), "Adjusted P-value"]
                > enriched.loc[(gene_set, term), "Adjusted P-value"]
            ):
                enriched.loc[(gene_set, term)] = down_enriched.loc[(gene_set, term)]

            # merge proteins, genes and overlap columns
            proteins = set(up_enriched.loc[(gene_set, term), "Proteins"].split(";"))
            proteins.update(down_enriched.loc[(gene_set, term), "Proteins"].split(";"))
            enriched.loc[(gene_set, term), "Proteins"] = ";".join(list(proteins))

            genes = set(up_enriched.loc[(gene_set, term), "Genes"].split(";"))
            genes.update(down_enriched.loc[(gene_set, term), "Genes"].split(";"))
            enriched.loc[(gene_set, term), "Genes"] = ";".join(list(genes))

            total = str(up_enriched.loc[(gene_set, term), "Overlap"]).split("/")[1]
            enriched.loc[(gene_set, term), "Overlap"] = f"{len(genes)}/{total}"
        else:
            enriched.loc[(gene_set, term), :] = down_enriched.loc[(gene_set, term), :]

    return enriched.reset_index()


def gseapy_enrichment(
    protein_list,
    protein_sets,
    direction,
    gene_mapping_df,
    organism=None,
    background=None,
    offline=False,
):
    """
    A helper method for the enrichment analysis with GSEApy. It maps the proteins to uppercase gene symbols
    and performs the enrichment analysis with GSEApy. Enrichment is run offline, when offline is True,
    else it is run via Enrichr API. It returns the enrichment results and the groups that
    were filtered out because no gene symbol could be found.

    :param protein_list: protein groups that should be analysed
    :type protein_list: list
    :param protein_sets: protein sets to perform the enrichment analysis with
    :type protein_sets: list
    :param direction: direction of regulation ("up" or "down")
    :type direction: str
    :param gene_mapping_df: dataframe with protein IDs and gene symbols
    :type gene_mapping_df: pandas.DataFrame
    :param organism: organism to be used for the analysis, must be one of the following
        supported by Enrichr: "human", "mouse", "yeast", "fly", "fish", "worm"
    :type organism: str
    :param background: background for the enrichment analysis
    :type background: list or None
    :param offline: whether to run the enrichment offline
    :type offline: bool

    :return: enrichment results, filtered groups, error message if occurred {level, msg, trace(optional)}
    :rtype: tuple[pandas.DataFrame, list, dict]
    """
    gene_to_protein_groups = (
        gene_mapping_df.groupby("Gene")["Protein ID"].apply(list).to_dict()
    )
    protein_group_to_genes = (
        gene_mapping_df.groupby("Protein ID")["Gene"].apply(list).to_dict()
    )
    genes = set()
    filtered_groups = set()
    for group in protein_list:
        if group in protein_group_to_genes:
            genes.update(protein_group_to_genes[group])
        else:
            filtered_groups.add(group)

    if not genes:
        msg = (
            "No gene symbols could be found for the proteins. Please check your input."
        )
        return None, None, dict(level=logging.ERROR, msg=msg)

    logger.info(f"Starting analysis for {direction}regulated proteins")

    error_msg = "Something went wrong with the analysis. Please check your inputs."
    if offline:
        try:
            enriched = gseapy.enrich(
                gene_list=list(genes),
                gene_sets=protein_sets,
                background=background,
                no_plot=True,
                outdir=None,
                verbose=True,
            ).results
        except ValueError as e:
            return (
                None,
                None,
                dict(level=logging.ERROR, msg=error_msg, trace=str(e)),
            )
    else:
        try:
            enriched = gseapy.enrichr(
                gene_list=list(genes),
                gene_sets=protein_sets,
                background=background,
                organism=organism,
                outdir=None,
                verbose=True,
            ).results
        except ValueError as e:
            return (
                None,
                None,
                dict(level=logging.ERROR, msg=error_msg, trace=str(e)),
            )

    enriched["Proteins"] = enriched["Genes"].apply(
        lambda x: ";".join(
            ";".join(gene_to_protein_groups[gene]) for gene in x.split(";")
        )
    )
    logger.info(f"Finished analysis for {direction}regulated proteins")
    return enriched, list(filtered_groups), None


def GO_analysis_with_Enrichr(
    proteins_df,
    organism,
    differential_expression_col,
    gene_mapping_df,
    differential_expression_threshold=0,
    direction="both",
    gene_sets_path=None,
    gene_sets_enrichr=None,
    background_path=None,
    background_number=None,
    background_biomart=None,
    **kwargs,
):
    """
    A method that performs online over-representation analysis for a given set of proteins
    against a given set of gene sets using the GSEApy package which accesses
    the Enrichr API. Uniprot Protein IDs in proteins are converted to uppercase HGNC gene symbols.
    If no match is found, the protein is excluded from the analysis. All excluded proteins
    are returned in a list.
    The enrichment is performed against a background provided as a path (recommended), number or
    name of a biomart dataset. If no background is provided, all genes in the gene sets are used as
    the background. Up- and downregulated proteins are analyzed separately and the results are merged.
    When gene sets from Enrichr are used, the background parameters are ignored. All genes in the gene sets
    will be used instead.

    :param proteins_df: proteins to be analyzed
    :type proteins_df: dataframe
    :param differential_expression_col: name of the column in the proteins dataframe that contains values for
        direction of expression change.
    :type differential_expression_col: str
    :param gene_mapping_df: dataframe with protein IDs and gene symbols
    :type gene_mapping_df: pandas.DataFrame
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
    :param organism: organism to be used for the analysis, must be one of the following
        supported by Enrichr: "human", "mouse", "yeast", "fly", "fish", "worm"
    :type organism: str
    :param differential_expression_threshold: threshold for differential expression.
        Proteins with values above this threshold are considered upregulated, proteins with
        differential_expression_col values below this threshold are considered downregulated.
        If "log" is in the name of differential_expression_col, the threshold is applied symmetrically:
        e.g. log2_fold_change > threshold, the protein is upregulated, if log2_fold_change < -threshold,
        the protein is downregulated.
    :type differential_expression_threshold: float
    :param direction: direction of enrichment analysis.
        Possible values: up, down, both
        - up: upregulated proteins only
        - down: downregulated proteins only
        - both: functional enrichment info is retrieved for upregulated and downregulated
        proteins separately, but the terms are aggregated for the resulting dataframe
    :type direction: str
    :param background_path: path to file with background proteins, .csv or .txt, one protein per line
    :type background_path: str or None
    :param background_number: number of background genes to use (not recommended),
        assumes that all genes could be found in background
    :type background_number: int or None
    :param background_biomart: name of biomart dataset to use as background
    :type background_biomart: str or None

    :return: dictionary with results and filtered groups
    :rtype: dict
    """
    out_messages = []
    if (
        not isinstance(proteins_df, pd.DataFrame)
        or not "Protein ID" in proteins_df.columns
        or not differential_expression_col in proteins_df.columns
        or not proteins_df[differential_expression_col].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and direction of expression change column (e.g. log2FC)"
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

    if gene_sets_path:
        gene_sets = read_protein_or_gene_sets_file(gene_sets_path)
        if isinstance(gene_sets, dict) and "messages" in gene_sets:  # an error occurred
            return gene_sets
    elif gene_sets_enrichr:
        if isinstance(gene_sets_enrichr, str):
            gene_sets = [gene_sets_enrichr]
        else:
            gene_sets = gene_sets_enrichr
    else:
        msg = "No gene sets provided"
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

    # we need to map the biomart dataset name to the internal name
    database = biomart_database("ENSEMBL_MART_ENSEMBL")
    for dataset in database.datasets:
        if database.datasets[dataset].display_name == background_biomart:
            background_biomart = dataset
            break
    # if gene sets from Enrichr are used, ignore background parameter because gseapy does not support it
    if gene_sets_enrichr and (
        background_path or background_number or background_biomart
    ):
        msg = "Background parameter is not supported when using Enrichr gene sets and will be ignored"
        out_messages.append(dict(level=logging.INFO, msg=msg))
        background = background_path = background_number = background_biomart = None

    if background_path:
        background = read_background_file(background_path)
        if (
            isinstance(background, dict) and "messages" in background
        ):  # an error occurred
            return background
    elif background_number:
        background = background_number
    elif background_biomart:
        # we need to map the biomart dataset name to the internal name
        database = biomart_database("ENSEMBL_MART_ENSEMBL")
        for dataset in database.datasets:
            if database.datasets[dataset].display_name == background_biomart:
                background = dataset
                break

        background = background_biomart
    else:
        background = None
        msg = "No background provided, using all genes in gene sets"
        out_messages.append(dict(level=logging.WARNING, msg=msg))

    # remove all columns but "Protein ID" and differential_expression_col column
    proteins_df = proteins_df[["Protein ID", differential_expression_col]]
    proteins_df.drop_duplicates(subset="Protein ID", inplace=True)
    expression_change_col = proteins_df[differential_expression_col]

    # split protein list according to direction of expression change and threshold
    if "log" in differential_expression_col:
        up_threshold = differential_expression_threshold
        down_threshold = -differential_expression_threshold
    else:
        up_threshold = differential_expression_threshold
        down_threshold = differential_expression_threshold
    up_protein_list = list(
        proteins_df.loc[expression_change_col > up_threshold, "Protein ID"]
    )
    down_protein_list = list(
        proteins_df.loc[expression_change_col < down_threshold, "Protein ID"]
    )

    if not up_protein_list:
        if direction == "up":
            msg = "No upregulated proteins found. Check your input or select 'down' direction."
            return dict(messages=[dict(level=logging.ERROR, msg=msg)])
        elif direction == "both" and not down_protein_list:
            msg = "No proteins found for given threshold. Check your input. "
            return dict(messages=[dict(level=logging.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No upregulated proteins found. Running analysis for 'down' direction only."
            logger.warning(msg)
            direction = "down"
            out_messages.append(dict(level=logging.WARNING, msg=msg))

    if not down_protein_list:
        if direction == "down":
            msg = "No downregulated proteins found. Check your input or select 'up' direction."
            return dict(messages=[dict(level=logging.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No downregulated proteins found. Running analysis for 'up' direction only."
            logger.warning(msg)
            direction = "up"
            out_messages.append(dict(level=logging.WARNING, msg=msg))

    if direction == "up" or direction == "both":
        up_enriched, up_filtered_groups, error_msg = gseapy_enrichment(
            up_protein_list,
            gene_sets,
            direction="up",
            gene_mapping_df=gene_mapping_df,
            organism=organism,
            background=background,
        )
        if error_msg:
            out_messages.append(error_msg)
            return dict(messages=out_messages)

    if direction == "down" or direction == "both":
        down_enriched, down_filtered_groups, error_msg = gseapy_enrichment(
            down_protein_list,
            gene_sets,
            direction="down",
            gene_mapping_df=gene_mapping_df,
            organism=organism,
            background=background,
        )
        if error_msg:
            out_messages.append(error_msg)
            return dict(messages=out_messages)

    if direction == "both":
        filtered_groups = up_filtered_groups + down_filtered_groups
        enriched = merge_up_down_regulated_dfs_gseapy(up_enriched, down_enriched)
    else:
        enriched = up_enriched if direction == "up" else down_enriched
        filtered_groups = (
            up_filtered_groups if direction == "up" else down_filtered_groups
        )

    if filtered_groups:
        msg = "Some proteins could not be mapped to gene symbols and were excluded from the analysis"
        out_messages.append(dict(level=logging.WARNING, msg=msg))
        return dict(
            enrichment_df=enriched,
            filtered_groups=filtered_groups,
            messages=out_messages,
        )

    return {
        "enrichment_df": enriched,
        "messages": out_messages,
    }


def GO_analysis_offline(
    proteins_df,
    gene_sets_path,
    differential_expression_col,
    gene_mapping_df,
    differential_expression_threshold=0,
    direction="both",
    background_path=None,
    background_number=None,
    **kwargs,
):
    """
    A method that performs offline over-representation analysis for a given set of proteins
    against a given set of gene sets using the GSEApy package.
    Uniprot Protein IDs in proteins are converted to uppercase HGNC gene symbols.
    If no match is found, the protein is excluded from the analysis. All excluded proteins
    are returned in a list.
    For the analysis a hypergeometric test is used against a background provided as a
    path (recommended) or a number of proteins. If no background is provided, all genes in
    the gene_sets are used as the background.
    Up- and downregulated proteins are analyzed separately and the results are merged.

    :param proteins_df: proteins to be analyzed
    :type proteins_df: dataframe
    :param differential_expression_col: name of the column in the proteins dataframe that contains values for
        direction of expression change.
    :type differential_expression_col: str
    :param gene_mapping_df: dataframe with protein IDs and gene symbols
    :type gene_mapping_df: pandas.DataFrame
    :param gene_sets_path: path to file containing gene sets. The identifiers
        in the gene_sets should be uppercase gene symbols.

        This could be any of the following file types: .gmt, .txt, .csv, .json
        - .txt: Setname or identifier followed by a tab-separated list of genes
            Set_name    Gene1    Gene2...
            Set_name    Gene2    Gene3...
        - .csv: Setname or identifier followed by a comma-separated list of genes
            Set_name, Gene1, Gene2, ...
            Set_name2, Gene2, Gene3, ...
        - .json:
            {Set_name: [Gene1, Gene2, ...], Set_name2: [Gene2, Gene3, ...]}
    :type gene_sets_path: str
    :param background_path: background genes to be used for the analysis.
        Should be provided as uppercase gene symbols. If no background is provided,
        all genes in gene sets are used. The background is defined by your experiment.
    :type background_path: str or None
    :param background_number: number of background genes to be used for the analysis (not recommended)
        assumes that all your genes could be found in background.
    :type background_number: int or None
    :param differential_expression_threshold: threshold for differential expression.
        Proteins with values above this threshold are considered upregulated, proteins with
        differential_expression_col values below this threshold are considered downregulated.
        If "log" is in the name of differential_expression_col, the threshold is applied symmetrically:
        e.g. log2_fold_change > threshold, the protein is upregulated, if log2_fold_change < -threshold,
        the protein is downregulated.
    :type differential_expression_threshold: float
    :param direction: direction of enrichment analysis.
        Possible values: up, down, both
        - up: upregulated proteins only
        - down: downregulated proteins only
        - both: functional enrichment info is retrieved for upregulated and downregulated
        proteins separately, but the terms are aggregated for the resulting dataframe
    :type direction: str

    :return: dictionary with results dataframe
    :rtype: dict
    """
    # enhancement: make sure ID type for all inputs match
    out_messages = []
    if (
        not isinstance(proteins_df, pd.DataFrame)
        or not "Protein ID" in proteins_df.columns
        or not differential_expression_col in proteins_df.columns
        or not proteins_df[differential_expression_col].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and direction of expression change column (e.g. log2FC)"
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

    # remove all columns but "Protein ID" and differential_expression_col column
    proteins_df = proteins_df[["Protein ID", differential_expression_col]]
    proteins_df.drop_duplicates(subset="Protein ID", inplace=True)
    expression_change_col = proteins_df[differential_expression_col]

    # split protein list according to direction of expression change and threshold
    if "log" in differential_expression_col:
        up_threshold = differential_expression_threshold
        down_threshold = -differential_expression_threshold
    else:
        up_threshold = differential_expression_threshold
        down_threshold = differential_expression_threshold
    up_protein_list = list(
        proteins_df.loc[expression_change_col > up_threshold, "Protein ID"]
    )
    down_protein_list = list(
        proteins_df.loc[expression_change_col < down_threshold, "Protein ID"]
    )

    if not up_protein_list:
        if direction == "up":
            msg = "No upregulated proteins found. Check your input or select 'down' direction."
            return dict(messages=[dict(level=logging.ERROR, msg=msg)])
        elif direction == "both" and len(down_protein_list) == 0:
            msg = "No proteins found for given threshold. Check your input. "
            return dict(messages=[dict(level=logging.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No upregulated proteins found. Running analysis for 'down' direction only."
            logger.warning(msg)
            direction = "down"
            out_messages.append(dict(level=logging.WARNING, msg=msg))

    if not down_protein_list:
        if direction == "down":
            msg = "No downregulated proteins found. Check your input or select 'up' direction."
            return dict(messages=[dict(level=logging.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No downregulated proteins found. Running analysis for 'up' direction only."
            logger.warning(msg)
            direction = "up"
            out_messages.append(dict(level=logging.WARNING, msg=msg))

    gene_sets = read_protein_or_gene_sets_file(gene_sets_path)
    if (
        isinstance(gene_sets, dict) and "messages" in gene_sets
    ):  # file could not be read successfully
        return gene_sets

    if background_path:
        background = read_background_file(background_path)
        if isinstance(background, dict):  # an error occurred
            return background
    elif background_number:
        background = background_number
    else:
        background = None

    if background is None:
        msg = "No valid background provided, using all proteins in protein sets"
        out_messages.append(dict(level=logging.INFO, msg=msg))

    if direction == "up" or direction == "both":
        up_enriched, up_filtered_groups, error_msg = gseapy_enrichment(
            up_protein_list,
            gene_sets,
            direction="up",
            gene_mapping_df=gene_mapping_df,
            background=background,
            offline=True,
        )
        if error_msg:
            out_messages.append(error_msg)
            return dict(messages=out_messages)

    if direction == "down" or direction == "both":
        down_enriched, down_filtered_groups, error_msg = gseapy_enrichment(
            down_protein_list,
            gene_sets,
            direction="down",
            gene_mapping_df=gene_mapping_df,
            background=background,
            offline=True,
        )
        if error_msg:
            out_messages.append(error_msg)
            return dict(messages=out_messages)

    if direction == "both":
        filtered_groups = up_filtered_groups + down_filtered_groups
        enriched = merge_up_down_regulated_dfs_gseapy(up_enriched, down_enriched)
    else:
        enriched = up_enriched if direction == "up" else down_enriched
        filtered_groups = (
            up_filtered_groups if direction == "up" else down_filtered_groups
        )

    out_dict = {"enrichment_df": enriched, "messages": out_messages}

    if filtered_groups:
        msg = "Some proteins could not be mapped to gene symbols and were excluded from the analysis"
        out_dict["messages"].append(dict(level=logging.WARNING, msg=msg))
        out_dict["filtered_groups"] = filtered_groups
        return out_dict
    return out_dict
