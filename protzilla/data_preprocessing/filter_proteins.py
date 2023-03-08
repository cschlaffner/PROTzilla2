from ..utilities.transform_dfs import long_to_wide
from protzilla.data_preprocessing.plots import create_pie_plot, create_bar_plot


def by_low_frequency(intensity_df, plot, threshold):
    min_threshold = threshold * len(intensity_df.Sample.unique())
    transformed_df = long_to_wide(intensity_df)

    remaining_proteins = transformed_df.dropna(axis=1, thresh=min_threshold).columns

    removed_proteins_df = transformed_df.drop(remaining_proteins, axis=1)

    filtered_proteins_list = removed_proteins_df.columns.unique().tolist()

    if plot == "pie":
        fig = create_pie_plot(
            values_of_sectors=[
                len(remaining_proteins),
                len(filtered_proteins_list),
            ],
            names_of_sectors=["Proteins kept", "Proteins filtered"],
            heading="Number of Filtered Proteins",
        )
    if plot == "bar":
        fig = create_bar_plot(
            values_of_sectors=[
                len(remaining_proteins),
                len(filtered_proteins_list),
            ],
            names_of_sectors=["Proteins kept", "Proteins filtered"],
            heading="Number of Filtered Proteins",
        )

    # TODO: might be redundant to remaining_proteins
    return (
        intensity_df[~(intensity_df["Protein ID"].isin(filtered_proteins_list))],
        [fig],
        dict(filtered_proteins=filtered_proteins_list),
    )
