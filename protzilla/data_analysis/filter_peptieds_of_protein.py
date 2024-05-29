import pandas as pd


def by_select_protein(
        peptide_df: pd.DataFrame, protein_id: list[str] | None = None,
) -> dict:
    """
    This function filters out all peptides with a PEP value (assigned to all samples
    together for each peptide) below a certain threshold.

    :param protein_df: ms-dataframe, piped through so next methods get proper input
    :type protein_df: pd.Dataframe
    :param peptide_df: the pandas dataframe containing the peptide information
    :type peptide_df: pd.Dataframe
    :param threshold: peptides with a PEP-value below this threshold will be filtered
        out
    :type threshold: float

    :return: dict of intensity-df, piped through, and of peptide_df without the peptides
        below the threshold and of a list with filtered-out peptides (Sequences)
    :rtype: Tuple[pd.Dataframe, dict(pd.Dataframe, list)]
    """

    filtered_peptides = peptide_df[peptide_df["Protein ID"].isin(list(protein_id))]

    return dict(
        single_protein_peptide_df=filtered_peptides,
    )
