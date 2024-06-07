import logging

import pandas as pd


def filter_peptides_of_protein(
        peptide_df: pd.DataFrame, protein_id: str | None = None,
) -> dict:
    """
    This function filters out all peptides with a PEP value (assigned to all samples
    together for each peptide) below a certain threshold.

    :param peptide_df: the pandas dataframe containing the peptide information
    :param protein_id: the protein ID to filter the corresponding peptides for

    :return: dict of the filtered peptide dataframe
    """

    filtered_peptides = peptide_df[peptide_df["Protein ID"].str.contains(protein_id)]

    return dict(
        single_protein_peptide_df=filtered_peptides,
        messages=[{
            "level": logging.INFO if len(filtered_peptides) > 0 else logging.WARNING,
            "msg": f"Selected {len(filtered_peptides)} entry's from the peptide dataframe."
        }],
    )


def single_protein_ptm_analysis(single_protein_peptide_df: pd.DataFrame) -> dict:
    return dict()