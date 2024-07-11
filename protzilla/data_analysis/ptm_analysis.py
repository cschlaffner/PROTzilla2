import logging
from math import log

import numpy as np
import pandas as pd
import re

from protzilla.utilities.transform_dfs import long_to_wide


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


def ptms_per_sample(peptide_df: pd.DataFrame) -> dict:
    """
    This function calculates the amount of every PTMs per sample.

    :param peptide_df: the pandas dataframe containing the peptide information

    :return: dict containing a dataframe one row per sample and one column per PTM that occurs in the peptide_df,
    with the cells containing the amount of the PTM in the sample
    """

    modification_df = peptide_df[["Sample", "Modifications"]]

    modification_df = pd.concat(
        [modification_df["Sample"],
         (modification_df['Modifications'].str.get_dummies(sep=","))], axis=1)

    for column, data in modification_df.iteritems():
        amount, name = from_string(column)
        if amount > 1:
            modification_df[column] = modification_df[column].multiply(amount)
            modification_df = modification_df.rename(columns={column: name})

    modification_df = modification_df.groupby(["Sample"]).sum()

    modification_df = modification_df.groupby(modification_df.columns, axis=1).sum()

    modification_df = modification_df.reset_index()

    return dict(ptm_df=modification_df)


def ptms_per_protein_and_sample(peptide_df: pd.DataFrame) -> dict:
    """
    This function calculates the amount of every PTM per sample and protein.

    :param peptide_df: the pandas dataframe containing the peptide information

    :return: dict containing a dataframe one row per sample and one column per protein,
    with the cells containing a list of PTMs that occur in the peptide_df for the protein and sample and
    their amount in the protein and sample
    """

    modification_df = peptide_df[["Sample", "Protein ID", "Modifications"]]

    modification_df = modification_df[["Sample", "Protein ID"]].join(
        modification_df['Modifications'].str.get_dummies(sep=",")
    )

    for column, data in modification_df.iteritems():
        amount, name = from_string(column)
        if amount > 1:
            modification_df[column] = modification_df[column].multiply(amount)
            modification_df = modification_df.rename(columns={column: name})

    modification_df = modification_df.groupby(["Sample", "Protein ID"]).sum()

    modification_df = modification_df.groupby(modification_df.columns, axis=1).sum()

    modification_df = modification_df.reset_index()

    modi = (
        modification_df.drop(["Sample", "Protein ID"], axis=1).apply(lambda x: ('(' + x.astype(str) + ') ' + x.name + ", ")))

    for column, data in modi.iteritems():
        modi[column] = np.where(modification_df[column] > 0, modi[column], "")

    modification_df["Modifications"] = modi.apply(''.join, axis=1)
    modification_df = modification_df[['Sample', 'Protein ID', 'Modifications']]

    modification_df = long_to_wide(modification_df, "Modifications").fillna("").reset_index()

    return dict(ptm_df=modification_df)


def from_string(mod_string: str) -> tuple[int, str]:
    """
    This function extracts the amount and name of a modification from its listing in the evidence file.

    :param mod_string: a string containing the amount and name of the modification

    :return: tuple containing the amount and name of the modification
    """

    re_search = re.search(r'\d+', mod_string)
    amount = int(re_search.group()) if re_search else 1
    name = re.search(r'\D+', mod_string).group()
    name = name[1:] if name[0] == " " else name

    return amount, name
