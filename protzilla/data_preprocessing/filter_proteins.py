import pandas as pd

from protzilla.data_preprocessing.plots import create_bar_plot, create_pie_plot
from ..utilities.transform_dfs import long_to_wide


def by_samples_missing(protein_df: pd.DataFrame, percentage: float) -> dict:
    """
    This function filters proteins based on the amount of samples with nan values, if the percentage of nan values
    is below a threshold (percentage).

    :param df: the intensity dataframe that should be filtered
    :param percentage: ranging from 0 to 1. Defining the relative share of samples the proteins need to be present
        in in order for the protein to be kept.
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
    filtered_df = protein_df[(protein_df["Protein ID"].isin(remaining_proteins_list))]
    return dict(
        protein_df=filtered_df,
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


def by_samples_missing_plot(method_inputs, method_outputs, graph_type):
    return _build_pie_bar_plot(
        method_outputs["remaining_proteins"],
        method_outputs["filtered_proteins"],
        graph_type,
    )
