import logging
import time

import pandas as pd

from protzilla.data_analysis.ptm_quantification.flexiquant import flexiquant_lf


def multiflex_lf(
    peptide_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    reference_group: str,
    num_init: int = 30,
    mod_cutoff: float = 0.5,
    remove_outliers: bool = True,
    imputation_cosine_similarity: float = 0.98,
    deseq2_normalization: bool = True,
    colormap: int = 1,
):
    """
    Quantifies the extent of protein modifications in proteomics data by using robust linear regression to compare modified and unmodified peptide precursors
    and facilitates the analysis of modification dynamics and coregulated modifications across large datasets without the need for preselecting specific proteins.

    Parts of the implementation have been adapted from https://gitlab.com/SteenOmicsLab/multiflex-lf.
    """

    # get current system time to track the runtime
    time.time()

    # create dataframe input for multiflex-lf
    df_intens_matrix_all_proteins = pd.DataFrame(
        {
            "ProteinID": peptide_df["Protein ID"],
            "PeptideID": peptide_df["Sequence"],
            "Sample": peptide_df["Sample"],
            "Intensity": peptide_df["Intensity"],
        }
    )

    # add Group column to input
    df_intens_matrix_all_proteins = pd.merge(
        df_intens_matrix_all_proteins, metadata_df[["Sample", "Group"]], on="Sample"
    )

    # check if reference identifier exists in Group column
    if str(reference_group) not in set(
        df_intens_matrix_all_proteins["Group"].astype(str)
    ):
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg=f"Reference group {reference_group} not found in metadata.",
                )
            ],
        )

    df_intens_matrix_all_proteins = (
        df_intens_matrix_all_proteins.dropna(subset=["Intensity"])
        .groupby(["ProteinID", "PeptideID", "Group", "Sample"])["Intensity"]
        .apply(max)
        .unstack(level=["Group", "Sample"])
        .T
    )
    df_intens_matrix_all_proteins = df_intens_matrix_all_proteins.set_index(
        [
            df_intens_matrix_all_proteins.index.get_level_values("Group"),
            df_intens_matrix_all_proteins.index.get_level_values("Sample"),
        ]
    )
    df_intens_matrix_all_proteins = df_intens_matrix_all_proteins.sort_index(
        axis=0
    ).sort_index(axis=1)

    # dataframe for the calculated RM scores of all proteins and peptides
    pd.DataFrame()

    # create a list of all proteins in the dataset
    list_proteins = (
        df_intens_matrix_all_proteins.columns.get_level_values("ProteinID")
        .unique()
        .sort_values()
    )

    for protein in list_proteins:
        flexiquant_lf(
            peptide_df, metadata_df, reference_group, protein, num_init, mod_cutoff
        )
