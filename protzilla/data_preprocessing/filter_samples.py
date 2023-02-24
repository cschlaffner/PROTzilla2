import pandas as pd


def by_protein_intensity_sum(intensity_df: pd.DataFrame, threshold):
    intensity_name = intensity_df.columns.values.tolist()[3]

    sample_protein_sum = intensity_df.groupby("Sample")[intensity_name].sum()

    median = sample_protein_sum.median()
    sd = sample_protein_sum.std()

    filtered_samples_list = sample_protein_sum[
        ~sample_protein_sum.between(
            (median - threshold * sd),
            (median + threshold * sd),
        )
    ].index.tolist()
    return intensity_df[~(intensity_df["Sample"].isin(filtered_samples_list))], dict(
        filtered_samples=filtered_samples_list
    )


def by_protein_count(intensity_df: pd.DataFrame, threshold):
    intensity_name = intensity_df.columns.values.tolist()[3]

    sample_protein_count = (
        intensity_df[~intensity_df[intensity_name].isnull()]
        .groupby("Sample")["Protein ID"]
        .nunique()
    )

    median = sample_protein_count.median()
    sd = sample_protein_count.std()
    filtered_samples_list = sample_protein_count[
        ~sample_protein_count.between(
            (median - threshold * sd),
            (median + threshold * sd),
        )
    ].index.tolist()
    return intensity_df[~(intensity_df["Sample"].isin(filtered_samples_list))], dict(
        filtered_samples=filtered_samples_list
    )
