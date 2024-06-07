import logging

import pandas as pd
import re


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
        peptide_df=filtered_peptides,
        messages=[{
            "level": logging.INFO if len(filtered_peptides) > 0 else logging.WARNING,
            "msg": f"Selected {len(filtered_peptides)} entry's from the peptide dataframe."
        }],
    )


def ptms_per_sampel(peptide_df: pd.DataFrame) -> dict:
    """
    This function calculates the amount of every PTMs per sample.

    :param peptide_df: the pandas dataframe containing the peptide information
    """

    modifications = pd.Series(sum(peptide_df["Modifications"].str.split(","), [])).unique()
    sampels = peptide_df["Sample"].unique()

    all_mod_counts = pd.DataFrame(sampels).rename(columns={0: "Sample"})

    for mod in modifications:
        filtered = peptide_df[peptide_df["Modifications"].str.contains(re.escape(mod))]

        mod_counts_without_zero = filtered.groupby('Sample')["Modifications"].size()
        mod_counts = mod_counts_without_zero.reindex(sampels).fillna(0)

        all_mod_counts[mod] = mod_counts.values


    return dict(ptm_df=all_mod_counts)