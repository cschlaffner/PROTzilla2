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


def by_totalsum(intensity_df: pd.DataFrame):
    """
    A function to perform normalisation using the total sum
    of sample intensities on your dataframe.
    Normalises the data on the level of each sample.
    Divides each intensity by the total sum of sample intensities.

    :param intensity_df: the dataframe that should be filtered in\
    long format
    :type intensity_df: pandas DataFrame
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
        totalsum = df_sample[intensity_name].sum()

        if totalsum != 0:
            df_sample[f"Normalised {intensity_name}"] = df_sample[
                intensity_name
            ].div(totalsum)
        else:
            # TODO: think about what to do if sum is zero
            try:
                raise ValueError(
                    "Careful, your total sum is zero. Try using other\
                    filtering strategies such as filtering non- or low\
                    intensity samples."
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


def by_reference_protein(
        intensity_df: pd.DataFrame,
        reference_protein_id: str = None,
):
    """
    A function to perform protein-intensity normalisation in reference
    to a selected protein on your dataframe.
    Normalises the data on the level of each sample.
    Divides each intensity by the intensity of the chosen reference
    protein in each sample. Samples where this value is zero will be
    removed and returned separately.

    :param intensity_df: the dataframe that should be filtered in\
    long format
    :type intensity_df: pandas DataFrame
    :param reference_protein_id: Protein ID of the protein to normalise by
    type reference_protein_id: str
    :return: returns a scaled dataframe in typical protzilla long format \
    and a list of the indices of the dropped samples
    :rtype: Tuple[pandas DataFrame, list]
    """
    scaled_df = pd.DataFrame()
    dropped_samples = []
    intensity_name = intensity_df.columns[3]
    protein_groups = intensity_df["Protein ID"].unique().tolist()
    for group in protein_groups:
        if reference_protein_id in group.split(";"):
            reference_protein_group = group
            break
    else:
        try:
            raise ValueError("The protein was not found")
        except ValueError as error:
            print(error)
        return scaled_df, pd.DataFrame(
            dropped_samples, columns=["Dropped Samples"]
        )

    samples = intensity_df["Sample"].unique().tolist()
    for sample in samples:
        df_sample = intensity_df.loc[intensity_df["Sample"] == sample]

        reference_intensity = df_sample.loc[
            df_sample["Protein ID"].values == reference_protein_group,
            intensity_name,
        ].values[0]
        if not (reference_intensity > 0):
            dropped_samples.append(sample)
            continue

        df_sample.loc[:, f"Normalised {intensity_name}"] = df_sample.loc[
                                                           :, intensity_name
                                                           ].div(reference_intensity)
        df_sample.drop(axis=1, labels=[intensity_name], inplace=True)

        scaled_df = pd.concat(
            [scaled_df, df_sample], ignore_index=True
        )

    return (
        scaled_df,
        dict(dropped_samples=dropped_samples),
    )


def by_median_plot(df, result_df, current_out, graph_type, group_by):
    if graph_type == "Boxplot":
        fig = create_box_plots(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Normalisation",
            name_b="After Normalisation",
            heading="Distribution of Protein Intensities",
            x_title="",
            y_title="",
            group_by=group_by,
        )
    if graph_type == "Histogram":
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


def by_totalsum_plot(df, result_df, current_out, graph_type, group_by):
    if graph_type == "Boxplot":
        fig = create_box_plots(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Normalisation",
            name_b="After Normalisation",
            heading="Distribution of Protein Intensities",
            x_title="",
            y_title="",
            group_by=group_by,
        )
    if graph_type == "Histogram":
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


def by_reference_protein_plot(df, result_df, current_out, graph_type, group_by):
    if graph_type == "Boxplot":
        fig = create_box_plots(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Normalisation",
            name_b="After Normalisation",
            heading="Distribution of Protein Intensities",
            x_title="",
            y_title="",
            group_by=group_by,
        )
    if graph_type == "Histogram":
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
