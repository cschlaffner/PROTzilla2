import pandas as pd

from protzilla.data_preprocessing.plots import create_bar_plot, create_pie_plot


def by_pep_value(
    peptide_df: pd.DataFrame, threshold: float
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

def by_samples_missing(
    protein_df: pd.DataFrame | None,
    peptide_df: pd.DataFrame | None,
    percentage: float = 0.5,
) -> dict:
    """
    This function filters proteins based on the amount of samples with nan values, if the percentage of nan values
    is below a threshold (percentage).

    :param protein_df: the protein dataframe that should be filtered
    :param peptide_df: the peptide dataframe that should be filtered in accordance to the intensity dataframe (optional)
    :param percentage: ranging from 0 to 1. Defining the relative share of samples the proteins need to be present in,
        in order for the protein to be kept.
    :return: returns the filtered df as a Dataframe and a dict with a list of Protein IDs that were discarded
        and a list of Protein IDs that were kept
    """

    filter_threshold: int = percentage * len(protein_df.Sample.unique())
    transformed_df = long_to_wide(protein_df)

    remaining_proteins_list = transformed_df.dropna(
        axis=1, thresh=filter_threshold
    ).columns.tolist()
    filtered_proteins_list = (
        transformed_df.drop(remaining_proteins_list, axis=1).columns.unique().tolist()
    )
    filtered_df = protein_df[
        (protein_df["Protein ID"].isin(remaining_proteins_list))
    ]
    filtered_peptide_df = None
    if peptide_df is not None:
        filtered_peptide_df = peptide_df[
            (peptide_df["Protein ID"].isin(remaining_proteins_list))
        ]
    return dict(
        protein_df=filtered_df,
        peptide_df=filtered_peptide_df,
        filtered_proteins=filtered_proteins_list,
        remaining_proteins=remaining_proteins_list,
    )


def _build_pie_bar_plot(remaining_proteins, filtered_proteins, graph_type):
    if graph_type == "Pie chart":
        fig = create_pie_plot(
            values_of_sectors=[
                len(remaining_proteins),
                len(filtered_proteins),
            ],
            names_of_sectors=["Proteins kept", "Proteins filtered"],
            heading="Number of Filtered Proteins",
        )
    elif graph_type == "Bar chart":
        fig = create_bar_plot(
            values_of_sectors=[
                len(remaining_proteins),
                len(filtered_proteins),
            ],
            names_of_sectors=["Proteins kept", "Proteins filtered"],
            heading="Number of Filtered Proteins",
            y_title="Number of Proteins",
        )
    return [fig]