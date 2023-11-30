import numpy as np
import pandas as pd

from protzilla.data_preprocessing.plots import create_box_plots, create_histograms
from protzilla.utilities import default_intensity_column


def by_log(intensity_df: pd.DataFrame, log_base="log10"):
    """
    This function log-transforms intensity
    DataFrames. Supports log-transformation to the base
    of 2 or 10.

    :param intensity_df: a protein data frame in long format
    :type intensity_df: pd.DataFrame
    :param log_base: String of the used log method "log10" (base 10)
        or "log2" (base 2). Default: "log10"
    :type log_base: str

    :return: returns a pandas DataFrame in typical protzilla
        long format with the transformed data and an empty dict.
    :rtype: Tuple[pandas DataFrame, dict]
    """
    intensity_name = default_intensity_column(intensity_df)
    transformed_df = intensity_df.copy()

    # TODO 41 drop data when intensity is 0 and return them in dict
    if log_base == "log2":
        transformed_df[intensity_name] = np.log2(transformed_df[intensity_name])
    elif log_base == "log10":
        transformed_df[intensity_name] = np.log10(transformed_df[intensity_name])
    else:
        raise ValueError("Unknown log_base. Known log methods are 'log2' and 'log10'.")
    return transformed_df, dict()


def by_log_plot(df, result_df, out, graph_type, group_by):
    return _build_box_hist_plot(df, result_df, graph_type, group_by)


def _build_box_hist_plot(df, result_df, graph_type, group_by):
    if graph_type == "Boxplot":
        fig = create_box_plots(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Transformation",
            name_b="After Transformation",
            heading="Distribution of Protein Intensities",
            group_by=group_by,
        )
    if graph_type == "Histogram":
        fig = create_histograms(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Transformation",
            name_b="After Transformation",
            heading="Distribution of Protein Intensities",
        )
    return [fig]
