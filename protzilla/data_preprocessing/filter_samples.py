import pandas as pd

from protzilla.data_preprocessing.plots import create_bar_plot, create_pie_plot


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


def by_proteins_missing(intensity_df: pd.DataFrame, percentage):
    intensity_name = intensity_df.columns.values.tolist()[3]

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
