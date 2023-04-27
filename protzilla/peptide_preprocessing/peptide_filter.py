import pandas as pd


def by_pep_value(peptide_df: pd.DataFrame, threshold: float):
    """
    This function filters out peptides with a PEP value below a certain threshold.

    :param peptide_df: the pandas dataframe containing the peptide information
    :type peptide_df: pd.Dataframe
    :param threshold: peptides with a PEP-value below this threshold will be filtered\
     out
    :type threshold: float

    :return: return the peptide_df without the peptides below the threshold, a dict with
    a dataframe containing the filtered out peptides {"filtered_peptides": df}
    :rtype: Tuple[pd.Dataframe, dict]
    """

    filtered_peptides = peptide_df[peptide_df["PEP"] < threshold]
    peptide_df.drop(filtered_peptides.index, inplace=True)
    peptide_df.reset_index(drop=True, inplace=True)
    filtered_peptides.reset_index(drop=True, inplace=True)

    return peptide_df, {"filtered_peptides": filtered_peptides}
