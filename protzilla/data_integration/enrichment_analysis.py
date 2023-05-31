import csv
import json
import logging
import os
import time
import shutil
import pandas as pd
import numpy as np
from restring import restring
import gseapy as gp
from django.contrib import messages

from .database_query import biomart_query

from ..constants.paths import RUNS_PATH
from protzilla.utilities.random import random_string

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


def merge_restring_dfs(df_dict):
    """
    This method merges the dataframes returned by the restring package
    into a single dataframe.

    :param df_dict: dictionary with dataframes returned by the restring package
    :type df_dict: dict
    :return: merged dataframe
    :rtype: pandas.DataFrame
    """
    dfs = []
    for term, df in df_dict.items():
        df["Gene_set"] = term
        dfs.append(df.reset_index())
    return pd.concat(dfs, ignore_index=True)


def go_analysis_with_STRING(
    proteins,
    protein_set_dbs,
    organism,
    background=None,
    direction="both",
    run_name=None,
    folder_name=None,
):
    """
    This method performs online functional enrichment analysis using the STRING DB API
    via the restring package. It writes the results to a folder in an
    enrichment_results folder in the run folder or to a tmp folder (for testing).
    Results for up- and down-regulated proteins are then aggregated and written
    into summary and results dataframes. These are also written to the run folder.

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
    :param run_name: name of the run folder to write results to. If None, a tmp folder
        is used.
    :type run_name: str or None
    :param folder_name: name of the folder to write results to. If None, a random string
        is used. This is for testing purposes.
    :type folder_name: str or None
    :return: dictionary with summary and results dataframes
    :rtype: dict
    """

    # TODO 182: set logging level for whole django app in beginning
    logging.basicConfig(level=logging.INFO)
    out_messages = []

    if (
        not isinstance(proteins, pd.DataFrame)
        or proteins.shape[1] != 2
        or not "Protein ID" in proteins.columns
        or not proteins.iloc[:, 1].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and numeric ranking column (e.g. log2FC))"
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
            logging.warning(msg)
            direction = "down"
            out_messages.append(dict(level=messages.WARNING, msg=msg))

    if len(down_protein_list) == 0:
        if direction == "down":
            msg = "No downregulated proteins found. Check your input or select 'up' direction."
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No downregulated proteins found. Running analysis for 'up' direction only."
            logging.warning(msg)
            direction = "up"
            out_messages.append(dict(level=messages.WARNING, msg=msg))

    if protein_set_dbs is None or protein_set_dbs == "":
        protein_set_dbs = ["KEGG", "Component", "Function", "Process", "RCTM"]
        msg = "No protein set databases selected. Using all protein set databases."
        out_messages.append(dict(level=messages.INFO, msg=msg))
    elif not isinstance(protein_set_dbs, list):
        protein_set_dbs = [protein_set_dbs]

    if background == "" or background is None:
        logging.info("No background provided, using entire proteome")
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

    # change working direcory to run folder for enrichment analysis
    # or make tmp folder
    results_path = (
        RUNS_PATH / run_name / "enrichment_results"
        if run_name
        else os.path.join(os.getcwd(), "tmp_enrichment_results")
    )
    os.makedirs(results_path, exist_ok=True)

    # make folder for current enrichment analysis and details of analysis
    enrichment_folder_name = (
        f"enrichment_{random_string()}" if folder_name is None else folder_name
    )
    enrichment_folder_path = os.path.join(results_path, enrichment_folder_name)
    os.makedirs(enrichment_folder_path, exist_ok=True)

    details_folder_name = "enrichment_details"
    details_folder_path = os.path.join(enrichment_folder_path, details_folder_name)
    os.makedirs(details_folder_path, exist_ok=True)
    start_dir = os.getcwd()
    os.chdir(details_folder_path)

    # enhancement: add mapping to string API for identifiers before this (dont forget background)

    if direction == "up" or direction == "both":
        logging.info("Starting analysis for up-regulated proteins")

        up_df = get_functional_enrichment_with_delay(up_protein_list, **string_params)
        try:
            restring.write_functional_enrichment_tables(up_df, prefix="UP_")
        except KeyError as e:
            msg = "Error writing enrichment results. Check your input and make sure the organism id is correct."
            out_messages.append(dict(level=messages.ERROR, msg=msg, trace=str(e)))
            return dict(messages=out_messages)

        logging.info("Finished analysis for up-regulated proteins")

    if direction == "down" or direction == "both":
        logging.info("Starting analysis for down-regulated proteins")

        down_df = get_functional_enrichment_with_delay(
            down_protein_list, **string_params
        )
        try:
            restring.write_functional_enrichment_tables(down_df, prefix="DOWN_")
        except KeyError as e:
            msg = "Error writing enrichment results. Check your input and make sure the organism id is correct."
            out_messages.append(dict(level=messages.ERROR, msg=msg, trace=str(e)))
            return dict(messages=out_messages)
        logging.info("Finished analysis for down-regulated proteins")

    # change working directory back to current enrichment folder
    os.chdir("..")

    logging.info("Summarizing enrichment results")
    results = {}
    summaries = {}
    for term in protein_set_dbs:
        db = restring.aggregate_results(
            directories=[details_folder_name], kind=term, PATH=enrichment_folder_path
        )
        result = restring.tableize_aggregated(db)
        result.to_csv(f"{term}_results.csv")
        results[term] = result
        summary = restring.summary(db)
        summary.to_csv(f"{term}_summary.csv")
        summaries[term] = summary

    # combine all results and summaries
    if len(results) > 1:
        merged_results = merge_restring_dfs(results)
        merged_summary = merge_restring_dfs(summaries)
    else:
        merged_results = results[term]
        merged_summary = summaries[term]

    # switch back to original working directory
    os.chdir(start_dir)

    # delete tmp folder if it was created
    if os.path.basename(results_path) == "tmp_enrichment_results":
        shutil.rmtree(results_path)

    if len(out_messages) > 0:
        return dict(messages=out_messages, results=results, summaries=summaries)

    return {"result": merged_results, "summary": merged_summary}


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


def merge_up_down_regulated_proteins_results(up_enriched, down_enriched):
    logging.info("Merging results for up- and down-regulated proteins")
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
            proteins = set(up_enriched.loc[(gene_set, term), "Proteins"].split(","))
            proteins.update(down_enriched.loc[(gene_set, term), "Proteins"].split(","))
            enriched.loc[(gene_set, term), "Proteins"] = ",".join(list(proteins))

            genes = set(up_enriched.loc[(gene_set, term), "Genes"].split(";"))
            genes.update(down_enriched.loc[(gene_set, term), "Genes"].split(";"))
            enriched.loc[(gene_set, term), "Genes"] = ";".join(list(genes))

            enriched.loc[(gene_set, term), "Overlap"] = (
                str(len(genes))
                + "/"
                + str(up_enriched.loc[(gene_set, term), "Overlap"]).split("/")[1]
            )

        else:
            enriched.loc[(gene_set, term), :] = down_enriched.loc[(gene_set, term), :]

    return enriched.reset_index()


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
    :type protein_sets_path: list of str
    :param organism: organism to be used for the analysis, must be one of the following
        supported by Enrichr: "human", "mouse", "yeast", "fly", "fish", "worm"
    :type organism: str
    :param direction: direction of enrichment analysis.
        Possible values: up, down, both
        - up: Log2FC is > 0
        - down: Log2FC is < 0
        - both: functional enrichment info is retrieved for upregulated and downregulated
        proteins separately, but the terms are aggregated for the summary and results
    :type direction: str
    :return: dictionary with results and filtered groups
    :rtype: dict
    """
    # enhancement: protein_sets are categorical for now, could also be custom file upload later
    #       background parameter would work then (with uploaded file)
    # dependency: refactoring/designing of more complex input choices
    out_messages = []

    if (
        not isinstance(proteins, pd.DataFrame)
        or proteins.shape[1] != 2
        or not "Protein ID" in proteins.columns
        or not proteins.iloc[:, 1].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and numeric ranking column (e.g. log2FC))"
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
            logging.warning(msg)
            direction = "down"
            out_messages.append(dict(level=messages.WARNING, msg=msg))

    if len(down_protein_list) == 0:
        if direction == "down":
            msg = "No downregulated proteins found. Check your input or select 'up' direction."
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No downregulated proteins found. Running analysis for 'up' direction only."
            logging.warning(msg)
            direction = "up"
            out_messages.append(dict(level=messages.WARNING, msg=msg))

    if direction == "up" or direction == "both":
        logging.info("Starting analysis for up-regulated proteins")
        logging.info("Mapping Uniprot IDs to gene symbols")
        up_gene_mapping, up_filtered_groups = uniprot_ids_to_uppercase_gene_symbols(
            up_protein_list
        )

        try:
            up_enriched = gp.enrichr(
                gene_list=list(up_gene_mapping.keys()),
                gene_sets=protein_sets,
                organism=organism,
                outdir=None,
                verbose=True,
            ).results
        except ValueError as e:
            return dict(
                messages=[
                    dict(
                        level=messages.ERROR,
                        msg="Something went wrong with the analysis. Please check your inputs.",
                        trace=str(e),
                    )
                ]
            )

        up_enriched["Proteins"] = up_enriched["Genes"].apply(
            lambda x: ",".join([up_gene_mapping[gene] for gene in x.split(";")])
        )
        logging.info("Finished analysis for up-regulated proteins")

    if direction == "down" or direction == "both":
        logging.info("Starting analysis for down-regulated proteins")
        logging.info("Mapping Uniprot IDs to gene symbols")
        down_gene_mapping, down_filtered_groups = uniprot_ids_to_uppercase_gene_symbols(
            down_protein_list
        )

        try:
            down_enriched = gp.enrichr(
                gene_list=list(down_gene_mapping.keys()),
                gene_sets=protein_sets,
                organism=organism,
                outdir=None,
                verbose=True,
            ).results
        except ValueError as e:
            return dict(
                messages=[
                    dict(
                        level=messages.ERROR,
                        msg="Something went wrong with the analysis. Please check your inputs.",
                        trace=str(e),
                    )
                ]
            )

        down_enriched["Proteins"] = down_enriched["Genes"].apply(
            lambda x: ",".join([down_gene_mapping[gene] for gene in x.split(";")])
        )
        logging.info("Finished analysis for down-regulated proteins")

    if direction == "both":
        filtered_groups = up_filtered_groups + down_filtered_groups
        enriched = merge_up_down_regulated_proteins_results(up_enriched, down_enriched)
    else:
        enriched = up_enriched if direction == "up" else down_enriched
        filtered_groups = (
            up_filtered_groups if direction == "up" else down_filtered_groups
        )

    if len(filtered_groups) > 0:
        msg = "Some proteins could not be mapped to gene symbols and were excluded from the analysis"
        out_messages.append(dict(level=messages.WARNING, msg=msg))
        return dict(
            results=enriched,
            filtered_groups=filtered_groups,
            messages=out_messages,
        )

    return {"results": enriched, "filtered_groups": filtered_groups}


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
        proteins separately, but the terms are aggregated for the summary and results
    :type direction: str
    :return: dictionary with results dataframe
    :rtype: dict
    """
    # enhancement: proteins could also be a number input (or an uploaded file)
    # dependency: refactoring/designing of more complex input choices

    # enhancement: make sure ID type for all inputs match
    out_messages = []
    if (
        not isinstance(proteins, pd.DataFrame)
        or proteins.shape[1] != 2
        or not "Protein ID" in proteins.columns
        or not proteins.iloc[:, 1].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and numeric ranking column (e.g. log2FC))"
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
            logging.warning(msg)
            direction = "down"
            out_messages.append(dict(level=messages.WARNING, msg=msg))

    if len(down_protein_list) == 0:
        if direction == "down":
            msg = "No downregulated proteins found. Check your input or select 'up' direction."
            return dict(messages=[dict(level=messages.ERROR, msg=msg)])
        elif direction == "both":
            msg = "No downregulated proteins found. Running analysis for 'up' direction only."
            logging.warning(msg)
            direction = "up"
            out_messages.append(dict(level=messages.WARNING, msg=msg))

    if protein_sets_path == "":
        return dict(
            messages=[
                dict(
                    level=messages.ERROR,
                    msg="No file uploaded for protein sets.",
                )
            ]
        )

    file_extension = os.path.splitext(protein_sets_path)[1]
    if file_extension == ".csv":
        with open(protein_sets_path, "r") as f:
            reader = csv.reader(f)
            protein_sets = {}
            for row in reader:
                key = row[0]
                values = row[1:]
                protein_sets[key] = values

    elif file_extension == ".txt":
        with open(protein_sets_path, "r") as f:
            protein_sets = {}
            for line in f:
                key, value_str = line.strip().split(":")
                values = [v.strip() for v in value_str.split(",")]
                protein_sets[key] = values

    elif file_extension == ".json":
        with open(protein_sets_path, "r") as f:
            protein_sets = json.load(f)

    elif file_extension == ".gmt":
        # gseapy can handle gmt files
        protein_sets = protein_sets_path

    else:
        return dict(
            messages=[
                dict(
                    level=messages.ERROR,
                    msg="Invalid file type for protein sets. Must be .csv, .txt, .json or .gmt",
                )
            ]
        )

    if background == "" or background is None:
        logging.info("No background provided, using all proteins in protein sets")
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
            return dict(
                messages=[
                    dict(
                        level=messages.ERROR,
                        msg="Invalid file type for background. Must be .csv, .txt or no upload",
                    )
                ]
            )

    if direction == "up" or direction == "both":
        logging.info("Starting analysis for up-regulated proteins")
        # gene set and gene list identifiers need to match
        try:
            up_enriched = gp.enrich(
                gene_list=up_protein_list,
                gene_sets=protein_sets,
                background=background,
                outdir=None,
                verbose=True,
            ).results
        except ValueError as e:
            return dict(
                messages=[
                    dict(
                        level=messages.ERROR,
                        msg="Something went wrong with the analysis. Please check your inputs.",
                        trace=str(e),
                    )
                ]
            )
        logging.info("Finished analysis for up-regulated proteins")

    if direction == "down" or direction == "both":
        logging.info("Starting analysis for up-regulated proteins")
        # gene set and gene list identifiers need to match
        try:
            down_enriched = gp.enrich(
                gene_list=down_protein_list,
                gene_sets=protein_sets,
                background=background,
                outdir=None,
                verbose=True,
            ).results
        except ValueError as e:
            return dict(
                messages=[
                    dict(
                        level=messages.ERROR,
                        msg="Something went wrong with the analysis. Please check your inputs.",
                        trace=str(e),
                    )
                ]
            )
        logging.info("Finished analysis for up-regulated proteins")

    if direction == "both":
        enriched = merge_up_down_regulated_proteins_results(up_enriched, down_enriched)
    else:
        enriched = up_enriched if direction == "up" else down_enriched

    return {"results": enriched}
