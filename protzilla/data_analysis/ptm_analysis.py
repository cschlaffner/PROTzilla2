import logging

import pandas as pd


def filter_peptides_of_protein(
        peptide_df: pd.DataFrame, protein_ids: list[str],
) -> dict:
    """
    This function filters out all peptides with a PEP value (assigned to all samples
    together for each peptide) below a certain threshold.

    :param peptide_df: the pandas dataframe containing the peptide information
    :param protein_ids: the protein ID to filter the corresponding peptides for

    :return: dict of the filtered peptide dataframe
    """

    filtered_peptide_dfs = [pd.DataFrame] * len(protein_ids)
    for i, protein_id in enumerate(protein_ids):
        filtered_peptide_dfs[i] = peptide_df[peptide_df["Protein ID"].str.contains(protein_id)]
    filtered_peptides = pd.concat(filtered_peptide_dfs)

    return dict(
        peptide_df=filtered_peptides,
        messages=[{
            "level": logging.INFO if len(filtered_peptides) > 0 else logging.WARNING,
            "msg": f"Selected {len(filtered_peptides)} entry's from the peptide dataframe."
        }],
    )