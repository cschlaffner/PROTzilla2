import pandas as pd

from protzilla.data_preprocessing.plots import create_bar_plot, create_pie_plot


def by_pep_value(
    protein_df: pd.DataFrame, peptide_df: pd.DataFrame, threshold: float
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

    filtered_peptides = peptide_df[peptide_df["PEP"] < threshold]
    peptide_df.drop(filtered_peptides.index, inplace=True)
    peptide_df.reset_index(drop=True, inplace=True)
    filtered_peptides.reset_index(drop=True, inplace=True)
    filtered_peptides_list = filtered_peptides["Sequence"].unique().tolist()

    return dict(
        protein_df=protein_df,
        peptide_df=peptide_df,
        filtered_peptides=filtered_peptides_list,
    )


def by_pep_value_plot(method_inputs, method_outputs, graph_type):
    value_dict = dict(
        values_of_sectors=[
            len(method_outputs["peptide_df"]),
            len(method_outputs["filtered_peptides"]),
        ],
        names_of_sectors=["Samples kept", "Samples filtered"],
        heading="Number of Filtered Samples",
    )

    if graph_type == "Pie chart":
        fig = create_pie_plot(**value_dict)
    elif graph_type == "Bar chart":
        fig = create_bar_plot(**value_dict)
    return [fig]
