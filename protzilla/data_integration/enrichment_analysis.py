import os
from time import sleep, time
import pandas as pd
import numpy as np
from restring import restring
import gseapy as gp
from django.contrib import messages

from ..constants.paths import RUNS_PATH

def go_analysis_with_STRING(
    proteins, protein_set_dbs, organism, background, directions, run_name=None
):
    '''dev notes

    organism can be any taxon id, could add a mapping here (name to id)
    
    '''

    # proteins should be df with two columns: Protein ID and numeric ranking column
    if (
        not isinstance(proteins, pd.DataFrame)
        or proteins.shape[1] != 2
        or not "Protein ID" in proteins.columns
        or not proteins.iloc[:, 1].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and numeric ranking column (e.g. log2FC))"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])
    
    expression_change_col = proteins.loc[:, proteins.columns != "Protein ID"][0]
    proteins.set_index("Protein ID", inplace=True)
    up_protein_list   = list(proteins[expression_change_col > 0].index)
    down_protein_list = list(proteins[expression_change_col < 0].index)

    string_params = {
        "species": organism,
        "caller_ID": "PROTzilla",
    }

    # change working direcory to run folder for enrichment analysis
    # or make tmp folder
    if run_name:
        os.mkdir(RUNS_PATH / run_name / "enrichment_results")
        os.chdir(RUNS_PATH / run_name / "enrichment_results")
    else:
        os.mkdir("tmp_enrichment_results")
        os.chdir("tmp_enrichment_results")

    # maybe add mapping to string API for identifiers

    up_df = restring.get_functional_enrichment(up_protein_list, **string_params)
    restring.write_functional_enrichment_tables(up_df, prefix="UP_")
    
    # only wait 1 sec overall?
    sleep(1)

    down_df = restring.get_functional_enrichment(down_protein_list, **string_params) 
    restring.write_functional_enrichment_tables(down_df, prefix="DOWN_")


    dirs = ["test_wd/pg_norm_dep_with_just_t"]

    # this has to be for loop per type
    # has PATH attribute
    db = restring.aggregate_results(directories=dirs, kind="Component")

    df = restring.tableize_aggregated(db)
    df.to_csv("results.csv")
    res = restring.summary(db)
    res.to_csv("summary.csv")

    if run_name is None: 
        # delete tmp folder
        os.chdir("..")
        os.rmdir("tmp_enrichment_results")

    return {}



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
        gene_sets=protein_sets,
        background=background,  # "hsapiens_gene_ensembl",
        outdir=None,
        verbose=True,
    )

    return {"enrichment_df": enr.results.sort_values(by="Adjusted P-value")}


def go_analysis_with_enrichr(proteins, protein_set_dbs, organism, background, cutoff):
    return {}
