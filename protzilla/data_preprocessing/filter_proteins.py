from protzilla.data_preprocessing.plots import create_bar_plot, create_pie_plot
from ..utilities.transform_dfs import long_to_wide


def by_low_frequency(intensity_df, threshold):
    """
    This function filters proteins with a low frequency of occurrence from
    a protein dataframe based on a set threshold. The threshold is defined
    by the relative amount of samples a protein is detected in.

    :param intensity_df: the dataframe that should be filtered\
    in long format
    :type intensity_df: pd.DataFrame
    :param threshold: float ranging from 0 to 1. Defining the\
    relative share of samples the proteins should be present in\
    order to be included. Example 0.5 - all proteins with intensities\
    equal to zero in at least 50% of samples are discarded. Default: 0.5
    :type threshold: float
    :return: returns a Dataframe with the samples that meet the\
    filtering criteria, a dict with a list with names of samples\
    that were discarded and a list with names of samples\
    that were kept
    :rtype: Tuple[pandas DataFrame, dict]
    """
    min_threshold = threshold * len(intensity_df.Sample.unique())
    transformed_df = long_to_wide(intensity_df)

    remaining_proteins = transformed_df.dropna(axis=1, thresh=min_threshold).columns

    removed_proteins_df = transformed_df.drop(remaining_proteins, axis=1)

    filtered_proteins_list = removed_proteins_df.columns.unique().tolist()

    # TODO: might be redundant to remaining_proteins
    return (
        intensity_df[~(intensity_df["Protein ID"].isin(filtered_proteins_list))],
        dict(
            filtered_proteins=filtered_proteins_list,
            remaining_proteins=remaining_proteins.tolist(),
        ),
    )


def by_low_frequency_plot(df, result_df, current_out, graph_type):
    if graph_type == "Pie chart":
        fig = create_pie_plot(
            values_of_sectors=[
                len(current_out["remaining_proteins"]),
                len(current_out["filtered_proteins"]),
            ],
            names_of_sectors=["Proteins kept", "Proteins filtered"],
            heading="Number of Filtered Proteins",
        )
    if graph_type == "Bar chart":
        fig = create_bar_plot(
            values_of_sectors=[
                len(current_out["remaining_proteins"]),
                len(current_out["filtered_proteins"]),
            ],
            names_of_sectors=["Proteins kept", "Proteins filtered"],
            heading="Number of Filtered Proteins",
        )
    return [fig]
