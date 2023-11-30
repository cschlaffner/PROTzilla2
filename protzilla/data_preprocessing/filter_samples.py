import pandas as pd

from protzilla.data_preprocessing.plots import create_bar_plot, create_pie_plot
from protzilla.utilities import default_intensity_column


def by_protein_intensity_sum(
    intensity_df: pd.DataFrame, deviation_threshold: float
) -> tuple[pd.DataFrame, dict]:
    """
    This function filters samples based on the sum of the protein intensities.

    :param intensity_df: the intensity dataframe that should be filtered
    :param deviation_threshold: defining the maximally allowed deviation from the median (in standard deviations)
        to keep a sample
    :return: the filtered df as a Dataframe and a dict with a list of Sample IDs that have been filtered
    """
    intensity_name = default_intensity_column(intensity_df)
    sample_protein_sum = intensity_df.groupby("Sample")[intensity_name].sum()

    median = sample_protein_sum.median()
    sd = sample_protein_sum.std()

    filtered_samples_list = sample_protein_sum[
        ~sample_protein_sum.between(
            (median - deviation_threshold * sd),
            (median + deviation_threshold * sd),
        )
    ].index.tolist()
    return intensity_df[~(intensity_df["Sample"].isin(filtered_samples_list))], dict(
        filtered_samples=filtered_samples_list
    )


def by_protein_count(
    intensity_df: pd.DataFrame, deviation_threshold: float
) -> tuple[pd.DataFrame, dict]:
    """
    This function filters samples based on their deviation of amount of proteins with a non-nan value from
    the median across all samples.

    :param intensity_df: the intensity dataframe that should be filtered
    :param deviation_threshold: float, defining the allowed deviation (in standard deviations) from the median number
        of non-nan values to keep a sample
    :return: the filtered df as a Dataframe and a dict with a list of Sample IDs that have been filtered
    """
    intensity_name = default_intensity_column(intensity_df)
    sample_protein_count = (
        intensity_df[~intensity_df[intensity_name].isnull()]
        .groupby("Sample")["Protein ID"]
        .nunique()
    )

    median = sample_protein_count.median()
    sd = sample_protein_count.std()

    filtered_samples_list = sample_protein_count[
        ~sample_protein_count.between(
            (median - deviation_threshold * sd),
            (median + deviation_threshold * sd),
        )
    ].index.tolist()
    return intensity_df[~(intensity_df["Sample"].isin(filtered_samples_list))], dict(
        filtered_samples=filtered_samples_list
    )


def by_proteins_missing(
    intensity_df: pd.DataFrame, percentage: float
) -> tuple[pd.DataFrame, dict]:
    """
    This function filters samples based on the amount of proteins with nan values, if the percentage of nan values
    is below a threshold (percentage).

    :param intensity_df: the intensity dataframe that should be filtered
    :param percentage: ranging from 0 to 1. Defining the relative share of proteins that were detected in the
        sample in inorder to be kept.
    :return: the filtered df as a Dataframe and a dict with a list of Sample IDs that have been filtered
    """

    intensity_name = default_intensity_column(intensity_df)
    total_protein_count = intensity_df["Protein ID"].nunique()
    sample_protein_count = (
        intensity_df[~intensity_df[intensity_name].isnull()]
        .groupby("Sample")["Protein ID"]
        .nunique()
    )
    filtered_samples_list = sample_protein_count[
        ~sample_protein_count.ge(total_protein_count * percentage)
    ].index.tolist()
    return intensity_df[~(intensity_df["Sample"].isin(filtered_samples_list))], dict(
        filtered_samples=filtered_samples_list
    )


def by_protein_intensity_sum_plot(df, result_df, current_out, graph_type):
    return _build_pie_bar_plot(df, result_df, current_out, graph_type)


def by_proteins_missing_plot(df, result_df, current_out, graph_type):
    return _build_pie_bar_plot(df, result_df, current_out, graph_type)


def by_protein_count_plot(df, result_df, current_out, graph_type):
    return _build_pie_bar_plot(df, result_df, current_out, graph_type)


def _build_pie_bar_plot(df, result_df, current_out, graph_type):
    if graph_type == "Pie chart":
        fig = create_pie_plot(
            values_of_sectors=[
                len(result_df["Sample"].unique()),
                len(current_out["filtered_samples"]),
            ],
            names_of_sectors=["Samples kept", "Samples filtered"],
            heading="Number of Filtered Samples",
        )
    if graph_type == "Bar chart":
        fig = create_bar_plot(
            values_of_sectors=[
                len(result_df["Sample"].unique()),
                len(current_out["filtered_samples"]),
            ],
            names_of_sectors=["Samples kept", "Samples filtered"],
            heading="Number of Filtered Samples",
        )
    return [fig]
