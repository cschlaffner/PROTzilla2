import os
import logging
from time import sleep, time
import pandas as pd
import numpy as np
from restring import restring
import gseapy as gp
from django.contrib import messages

from ..constants.paths import RUNS_PATH
from protzilla.utilities.random import random_string

def go_analysis_with_STRING(
    proteins, protein_set_dbs, organism, background, directions, run_name=None
):
    '''dev notes
    organism can be any taxon id, could add a mapping here (name to id)
    think about output format and plots
    '''
    #TODO: set logging level for whole django app in beginning
    logging.basicConfig(level=logging.NOTSET)

    # proteins should be df with two columns: Protein ID and numeric ranking column
    if (
        not isinstance(proteins, pd.DataFrame)
        or proteins.shape[1] != 2
        or not "Protein ID" in proteins.columns
        or not proteins.iloc[:, 1].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and numeric ranking column (e.g. log2FC))"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])
    
    expression_change_col = proteins.drop("Protein ID", axis=1).iloc[:, 0].to_frame()
    proteins.set_index("Protein ID", inplace=True)
    up_protein_list   = list(proteins[expression_change_col > 0].index)
    down_protein_list = list(proteins[expression_change_col < 0].index)

    if background == "":
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
    results_folder = RUNS_PATH / run_name / "enrichment_results" if run_name else "tmp_enrichment_results"
    os.makedirs(results_folder, exist_ok=True)

    # make folder for current enrichment analysis and details of analysis
    enrichment_folder_name = f"enrichment_{random_string()}"
    enrichment_folder_path = os.path.join(results_folder, enrichment_folder_name)
    os.makedirs(enrichment_folder_path)

    details_folder_name = "enrichment_details"
    details_folder_path = os.path.join(enrichment_folder_path, details_folder_name)
    os.makedirs(details_folder_path)
    os.chdir(details_folder_path)

    # maybe add mapping to string API for identifiers before this (dont forget background)

    if "up" in directions or "both" in directions:
        logging.info("Starting analysis for up-regulated proteins")
        
        up_df = restring.get_functional_enrichment(up_protein_list, **string_params)
        restring.write_functional_enrichment_tables(up_df, prefix="UP_")
        logging.info("Finished analysis for up-regulated proteins")
        # only wait 1 sec overall?
        sleep(1)
    
    if "down" in directions or "both" in directions:
        logging.info("Starting analysis for down-regulated proteins")
        
        down_df = restring.get_functional_enrichment(down_protein_list, **string_params) 
        restring.write_functional_enrichment_tables(down_df, prefix="DOWN_")
        logging.info("Finished analysis for down-regulated proteins")

    # change working directory back to current enrichment folder
    os.chdir("..")

    logging.info("Summarizing enrichment results")
    results = []
    summaries = []
    for term in protein_set_dbs:
        db = restring.aggregate_results(directories=[details_folder_name], kind=term, PATH=enrichment_folder_path)
        result = restring.tableize_aggregated(db)
        result.to_csv(f"{term}_results.csv")
        results.append(result)
        summary = restring.summary(db)
        summary.to_csv(f"{term}_summary.csv")
        summaries.append(summary)

    if results_folder == "tmp_enrichment_results": 
        # delete tmp folder
        os.chdir("..")
        os.rmdir("tmp_enrichment_results")

    return {"results": results, "summaries": summaries}



def go_analysis_offline(proteins, protein_set_dbs, background, cutoff):
    """dev notes
    proteins: could be list of somewhere filtered proteins, could be dataframe with multiple columns and we just want to use first,
    TODO: check what kind of IDs are allowed here

    protein_sets: make upload? gmt file or dictionary

    background: None defaults to all input proteins, list of proteins, or dataframe with multiple columns and we just want to use first?


    cutoff: cutoff for p-value
    """

    enr = gp.enrich(
        gene_list=proteins,
        gene_sets=protein_set_dbs,
        background=background,  # "hsapiens_gene_ensembl",
        outdir=None,
        verbose=True,
    )

    return {"enrichment_df": enr.results.sort_values(by="Adjusted P-value")}


def go_analysis_with_enrichr(proteins, protein_set_dbs, organism, background, cutoff):
    return {}
