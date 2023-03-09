import pandas as pd
from protzilla.data_preprocessing.plots import create_box_plots, create_histograms


def by_median(
        intensity_df: pd.DataFrame,
        q=0.5,  # quartile, default is median
):
    """
    A function to perform a quartile/percentile normalisation on your
    dataframe. Normalises the data on the level of each sample.
    Divides each intensity by the chosen intensity quartile of the
    respective sample. By default, the median (50%-quartile) is used.

    :param intensity_df: the dataframe that should be filtered in\
    long format
    :type intensity_df: pandas DataFrame
    :param q: the chosen quartile of the sample intensities for\
    normalisation
    :type q: float
    :return: returns a scaled dataframe in typical protzilla long format
    :rtype: pandas DataFrame
    """

    # Suppress SettingWithCopyWarning:
    # It gets raised because of reassignment of values to a subset of a df
    # The alternative - making an explicit copy - could use more memory
    # https://realpython.com/pandas-settingwithcopywarning/
    pd.set_option("mode.chained_assignment", None)

    intensity_name = intensity_df.columns[3]
    scaled_df = pd.DataFrame()
    samples = intensity_df["Sample"].unique().tolist()

    for sample in samples:
        df_sample = intensity_df.loc[
            intensity_df["Sample"] == sample,
        ]
        quantile = df_sample[intensity_name].quantile(q=q)

        if quantile != 0:
            df_sample[f"Normalised {intensity_name}"] = df_sample[
                intensity_name
            ].div(quantile)
        else:
            try:  # TODO: think about what to do if median is zero
                raise ValueError(
                    "Careful, your median is zero - we recommend\
                    adapting your filtering strategy or using a higher\
                    quantile for normalisation."
                )
            except ValueError as error:
                print(error)
                df_sample[f"Normalised {intensity_name}"] = 0
        df_sample.drop(axis=1, labels=[intensity_name], inplace=True)
        scaled_df = pd.concat(
            [scaled_df, df_sample], ignore_index=True
        )

    pd.reset_option("mode.chained_assignment")

    return (
        scaled_df,
        dict(),
    )


def by_median_plot(graph_type, df, result_df, current_out):
    if graph_type == "box":
        fig = create_box_plots(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Normalisation",
            name_b="After Normalisation",
            heading="Distribution of Protein Intensities",
            x_title="",
            y_title="",
            group_by="Sample",
        )
    if graph_type == "histogram":
        fig = create_histograms(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Normalisation",
            name_b="After Normalisation",
            heading="Distribution of Protein Intensities",
            x_title="",
            y_title="",
        )
    return fig