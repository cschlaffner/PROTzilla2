from protzilla.data_preprocessing.plots import create_bar_plot, create_pie_plot

from ..utilities.transform_dfs import long_to_wide


def by_samples_missing(intensity_df, percentage):
    """
    This function filters proteins based on its amount of nan values.
    If the percentage of existing values is below a threshold (percentage), the protein is filtered out.

    :param df: the intensity dataframe that should be filtered
        in long format
    :type df: pd.DataFrame
    :param percentage: float ranging from 0 to 1. Defining the
        relative share of samples the proteins should be present in inorder to be kept.
    :type percentage: float

    :return: returns the filtered df as a Dataframe and a dict with a listof Protein IDs
        that were discarded and a list of Protein IDs
        that were kept
    :rtype: Tuple[pandas DataFrame, dict]
    """

    min_threshold = percentage * len(intensity_df.Sample.unique())
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


def _build_pie_bar_plot(df, result_df, current_out, graph_type):
    if graph_type == "Pie chart":
        fig = create_pie_plot(
            values_of_sectors=[
                len(current_out["remaining_proteins"]),
                len(current_out["filtered_proteins"]),
            ],
            names_of_sectors=["Proteins kept", "Proteins filtered"],
            heading="Number of Filtered Proteins",
        )
    elif graph_type == "Bar chart":
        fig = create_bar_plot(
            values_of_sectors=[
                len(current_out["remaining_proteins"]),
                len(current_out["filtered_proteins"]),
            ],
            names_of_sectors=["Proteins kept", "Proteins filtered"],
            heading="Number of Filtered Proteins",
        )
    return [fig]


def by_samples_missing_plot(df, result_df, current_out, graph_type):
    return _build_pie_bar_plot(df, result_df, current_out, graph_type)
