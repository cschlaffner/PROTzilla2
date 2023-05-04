import pandas as pd
import numpy as np
from restring import restring
import gseapy as gp
from django.contrib import messages


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


def go_analysis_with_STRING(
    proteins, protein_set_dbs, organism, background, directions
):
    # proteins should be df with two columns: Protein ID and numeric ranking column
    if (
        not isinstance(proteins, pd.DataFrame)
        or proteins.shape[1] != 2
        or not "Protein ID" in proteins.columns
        or not proteins.iloc[:, 1].dtype == np.number
    ):
        msg = "Proteins must be a dataframe with Protein ID and numeric ranking column (e.g. log2FC))"
        return dict(messages=[dict(level=messages.ERROR, msg=msg)])

    dirs = ["test_wd/pg_norm_dep_with_just_t"]

    # this has to be for loop per type
    db = restring.aggregate_results(directories=dirs, kind="Component")

    df = restring.tableize_aggregated(db)
    df.to_csv("results.csv")
    res = restring.summary(db)
    res.to_csv("summary.csv")

    return {}
