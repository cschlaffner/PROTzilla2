from ..utilities.transform_dfs import long_to_wide


def by_low_frequency(intensity_df, threshold):
    min_threshold = threshold * len(intensity_df.Sample.unique())
    transformed_df = long_to_wide(intensity_df)

    remaining_proteins = transformed_df.dropna(axis=1, thresh=min_threshold).columns

    removed_proteins_df = transformed_df.drop(remaining_proteins, axis=1)

    filtered_proteins_list = removed_proteins_df.columns.unique().tolist()

    # TODO: might be redundant to remaining_proteins
    return (
        intensity_df[~(intensity_df["Protein ID"].isin(filtered_proteins_list))],
        dict(filtered_proteins=filtered_proteins_list),
    )
