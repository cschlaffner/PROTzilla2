import logging
import traceback

import pandas as pd
from sklearn.preprocessing import StandardScaler

from protzilla.data_preprocessing.plots import create_box_plots, create_histograms
from protzilla.utilities import default_intensity_column


def by_z_score(protein_df: pd.DataFrame) -> dict:
    """
    A function to run the sklearn StandardScaler class on your dataframe.
    Normalises the data on the level of each sample.
    Scales the data to zero mean and unit variance. This is often also
    called z-score normalisation/transformation.

    :param protein_df: the dataframe that should be filtered in
        long format
    :type protein_df: pd.DataFrame

    :return: returns a scaled dataframe in typical protzilla long format and an empty
        dictionary
    :rtype: Tuple[pandas DataFrame, dict]
    """

    # Suppress SettingWithCopyWarning:
    # It gets raised because of reassignment of values to a subset of a df
    # The alternative - making an explicit copy - could use more memory
    # https://realpython.com/pandas-settingwithcopywarning/
    pd.set_option("mode.chained_assignment", None)

    intensity_name = default_intensity_column(protein_df)
    scaled_df = pd.DataFrame()
    samples = protein_df["Sample"].unique().tolist()

    for sample in samples:
        df_sample = protein_df.loc[protein_df["Sample"] == sample,]
        scaler = StandardScaler().fit(df_sample[[intensity_name]])
        df_sample[f"Normalised {intensity_name}"] = scaler.transform(
            df_sample[[intensity_name]]
        )
        df_sample.drop(axis=1, labels=[intensity_name], inplace=True)
        scaled_df = pd.concat([scaled_df, df_sample], ignore_index=True)

    pd.reset_option("mode.chained_assignment")
    return dict(protein_df=scaled_df)


def by_median(
    protein_df: pd.DataFrame,
    percentile=0.5,  # quartile, default is median
) -> dict:
    """
    A function to perform a quartile/percentile normalisation on your
    dataframe. Normalises the data on the level of each sample.
    Divides each intensity by the chosen intensity quartile of the
    respective sample. By default, the median (50%-quartile) is used.

    :param protein_df: the dataframe that should be filtered in
        long format
    :type protein_df: pandas DataFrame
    :param percentile: the chosen quartile of the sample intensities for
        normalisation
    :type percentile: float

    :return: returns a scaled dataframe in typical protzilla long format
        and a dict, containing all zeroed samples due to quantile being 0
    :rtype: Tuple[pandas DataFrame, dict]
    """

    # Suppress SettingWithCopyWarning:
    # It gets raised because of reassignment of values to a subset of a df
    # The alternative - making an explicit copy - could use more memory
    # https://realpython.com/pandas-settingwithcopywarning/
    pd.set_option("mode.chained_assignment", None)

    assert 0 <= percentile <= 1

    intensity_name = default_intensity_column(protein_df)
    scaled_df = pd.DataFrame()
    samples = protein_df["Sample"].unique().tolist()
    zeroed_samples = []

    for sample in samples:
        df_sample = protein_df.loc[protein_df["Sample"] == sample,]
        quantile = df_sample[intensity_name].quantile(q=percentile)

        if quantile != 0:
            df_sample[f"Normalised {intensity_name}"] = df_sample[intensity_name].div(
                quantile
            )
        else:
            # TODO 428
            try:
                raise ValueError(
                    "\nCareful, your median is zero - we recommend\
                    \nadapting your filtering strategy or using a higher\
                    \nquantile for normalisation."
                )
            except ValueError:
                traceback.print_exc()
                df_sample[f"Normalised {intensity_name}"] = 0
                zeroed_samples.append(sample)
        df_sample.drop(axis=1, labels=[intensity_name], inplace=True)
        scaled_df = pd.concat([scaled_df, df_sample], ignore_index=True)

    pd.reset_option("mode.chained_assignment")

    return dict(
        protein_df=scaled_df,
        zeroed_samples=zeroed_samples,
    )


def by_totalsum(protein_df: pd.DataFrame) -> dict:
    """
    A function to perform normalisation using the total sum
    of sample intensities on your dataframe.
    Normalises the data on the level of each sample.
    Divides each intensity by the total sum of sample intensities.

    :param protein_df: the dataframe that should be filtered in
        long format
    :type protein_df: pandas DataFrame

    :return: returns a scaled dataframe in typical protzilla long format
        and a dict, containing all zeroed samples due to sum being 0
    :rtype: Tuple[pandas DataFrame, dict]
    """

    # Suppress SettingWithCopyWarning:
    # It gets raised because of reassignment of values to a subset of a df
    # The alternative - making an explicit copy - could use more memory
    # https://realpython.com/pandas-settingwithcopywarning/
    pd.set_option("mode.chained_assignment", None)

    intensity_name = default_intensity_column(protein_df)
    scaled_df = pd.DataFrame()
    samples = protein_df["Sample"].unique().tolist()
    zeroed_samples_list = []

    for sample in samples:
        df_sample = protein_df.loc[protein_df["Sample"] == sample,]
        totalsum = df_sample[intensity_name].sum()

        if totalsum != 0:
            df_sample[f"Normalised {intensity_name}"] = df_sample[intensity_name].div(
                totalsum
            )
        else:
            # TODO 428
            try:
                raise ValueError(
                    "\nCareful, your total sum is zero. Try using other\
                    \nfiltering strategies such as filtering non- or low\
                    \nintensity samples."
                )
            except ValueError:
                traceback.print_exc()
                df_sample[f"Normalised {intensity_name}"] = 0
                zeroed_samples_list.append(sample)

        df_sample.drop(axis=1, labels=[intensity_name], inplace=True)

        scaled_df = pd.concat([scaled_df, df_sample], ignore_index=True)

    pd.reset_option("mode.chained_assignment")
    return dict(protein_df=scaled_df, zeroed_samples=zeroed_samples_list)


def by_reference_protein(
    protein_df: pd.DataFrame,
    reference_protein: str,
) -> dict:
    """
    A function to perform protein-intensity normalisation in reference
    to a selected protein on your dataframe.
    Normalises the data on the level of each sample.
    Divides each intensity by the intensity of the chosen reference
    protein in each sample. Samples where this value is zero will be
    removed and returned separately.

    :param protein_df: the dataframe that should be filtered in
        long format
    :type protein_df: pandas DataFrame
    :param reference_protein: Protein ID of the protein to normalise by
        type reference_protein_id: str
    :return: returns a scaled dataframe in typical protzilla long format
        and dict with a list of the indices of the dropped samples
    :rtype: Tuple[pandas DataFrame, dict]
    """
    scaled_df = pd.DataFrame()
    dropped_samples = []
    intensity_name = default_intensity_column(protein_df)
    protein_groups = protein_df["Protein ID"].unique().tolist()
    for group in protein_groups:
        if reference_protein in group.split(";"):
            reference_protein_group = group
            break
    else:
        msg = "The protein was not found"
        return dict(
            protein_df=scaled_df,
            dropped_samples=None,
            messages=[dict(level=logging.ERROR, msg=msg)],
        )

    samples = protein_df["Sample"].unique().tolist()
    for sample in samples:
        df_sample = protein_df.loc[protein_df["Sample"] == sample]

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

        scaled_df = pd.concat([scaled_df, df_sample], ignore_index=True)

    return dict(protein_df=scaled_df, dropped_samples=dropped_samples)


def by_z_score_plot(
        method_inputs,
        method_outputs,
        graph_type,
        group_by,
        visual_transformation
):
    return _build_box_hist_plot(
        method_inputs["protein_df"],
        method_outputs["protein_df"],
        graph_type,
        group_by,
        visual_transformation
    )


def by_median_plot(
        method_inputs,
        method_outputs,
        graph_type,
        group_by,
        visual_transformation
):
    return _build_box_hist_plot(
        method_inputs["protein_df"],
        method_outputs["protein_df"],
        graph_type, group_by,
        visual_transformation
    )


def by_totalsum_plot(
        method_inputs,
        method_outputs,
        graph_type,
        group_by,
        visual_transformation
):
    return _build_box_hist_plot(
        method_inputs["protein_df"],
        method_outputs["protein_df"],
        graph_type, group_by,
        visual_transformation
    )


def by_reference_protein_plot(
        method_inputs,
        method_outputs,
        graph_type,
        group_by,
        visual_transformation
):
    return _build_box_hist_plot(
        method_inputs["protein_df"],
        method_outputs["protein_df"],
        graph_type,
        group_by,
        visual_transformation
    )


def _build_box_hist_plot(df, result_df, graph_type, group_by, visual_transformation):
    if graph_type == "Boxplot":
        fig = create_box_plots(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Normalisation",
            name_b="After Normalisation",
            heading="Distribution of Protein Intensities",
            x_title="",
            y_title="Intensity",
            group_by=group_by,
            visual_transformation=visual_transformation,
        )
    if graph_type == "Histogram":
        fig = create_histograms(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Normalisation",
            name_b="After Normalisation",
            heading="Distribution of Protein Intensities",
            x_title="Protein Intensities",
            y_title="Frequency of Protein Intensities",
            visual_transformation=visual_transformation,
        )
    return [fig]
