import os
import json
import csv
import logging
import time
import shutil
import pandas as pd
import numpy as np
from restring import restring
import gseapy as gp
from django.contrib import messages

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
    """

    # TODO: set logging level for whole django app in beginning
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
        restring.write_functional_enrichment_tables(up_df, prefix="UP_")
        logging.info("Finished analysis for up-regulated proteins")

    if direction == "down" or direction == "both":
        logging.info("Starting analysis for down-regulated proteins")

        down_df = get_functional_enrichment_with_delay(
            down_protein_list, **string_params
        )
        restring.write_functional_enrichment_tables(down_df, prefix="DOWN_")
        logging.info("Finished analysis for down-regulated proteins")

    # change working directory back to current enrichment folder
    os.chdir("..")

    logging.info("Summarizing enrichment results")
    results = []
    summaries = []
    for term in protein_set_dbs:
        db = restring.aggregate_results(
            directories=[details_folder_name], kind=term, PATH=enrichment_folder_path
        )
        result = restring.tableize_aggregated(db)
        result.to_csv(f"{term}_results.csv")
        results.append(result)
        summary = restring.summary(db)
        summary.to_csv(f"{term}_summary.csv")
        summaries.append(summary)

    # switch back to original working directory
    os.chdir(start_dir)

    # delete tmp folder if it was created
    if os.path.basename(results_path) == "tmp_enrichment_results":
        shutil.rmtree(results_path)

    if len(out_messages) > 0:
        return dict(messages=out_messages, results=results, summaries=summaries)

    return {"results": results, "summaries": summaries}


def go_analysis_offline(proteins, protein_sets_path, background=None):
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
    """
    # enhancement: proteins could also be a number input (or an uploaded file)
    # dependency: refactoring/designing of more complex input choices

    # enhancement: make sure ID type for all inputs match

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

    # gene set and gene list identifiers need to match
    enr = gp.enrich(
        gene_list=proteins,
        gene_sets=protein_sets,
        background=background,
        outdir=None,
        verbose=True,
    )

    return {"results": enr.results}


def go_analysis_with_enrichr(proteins, protein_sets, organism):
    # This needs to have gene identifiers

    # enhancement: protein_sets are categorical for now, could also be custom file upload later
    #       background parameter would work then (with uploaded file)
    # dependency: refactoring/designing of more complex input choices

    # enhancement: make sure ID type for all inputs match
    enr = gp.enrichr(
        gene_list=proteins,
        gene_sets=protein_sets,
        organism=organism,
        outdir=None,
        verbose=True,
    )
    return {"results": enr.results}
