import pandas as pd
import numpy as np
from protzilla.data_preprocessing.plots import create_box_plots, create_histograms, create_bar_plot, create_pie_plot
from protzilla.utilities.transform_dfs import long_to_wide, wide_to_long
from sklearn.impute import KNNImputer


def by_knn(intensity_df: pd.DataFrame, n_neighbors=5,
           **kwargs  # quantile, default is median
):
    """
    A function to perform value imputation based on KNN
    (k-nearest neighbors). Imputes missing values for each
    sample based on intensity-wise similar samples.
    Two samples are close if the features that neither is
    missing are close.
    CAVE: Proteins that have NaN in alle samples will be
    filtered out if not previously filtered out!

    Implements an instance of the sklearn.impute KNNImputer
    class.
    https://scikit-learn.org/stable/modules/generated/sklearn.impute.KNNImputer.html
    :param intensity_df: the dataframe that should be filtered in\
    long format
    :type intensity_df: pandas DataFrame
    :param n_neighbors: number of neighbouring samples used for\
    imputation. Default: 5
    :type n_neighbors: int
    :param **kwargs: additional keyword arguments passed to\
        KNNImputer.fit_transform
    :type kwargs: dict
    :return: returns an imputed dataframe in typical protzilla long format\
    and an empty dict
    :rtype: pd.DataFrame
    """

    transformed_df = long_to_wide(intensity_df)
    transformed_df.dropna(axis=1, how="all", inplace=True)
    index = transformed_df.index
    columns = transformed_df.columns

    imputer = KNNImputer(n_neighbors=n_neighbors)
    transformed_df = imputer.fit_transform(transformed_df, **kwargs)
    transformed_df = pd.DataFrame(
        transformed_df, columns=columns, index=index
    )

    # Turn the wide format into the long format
    imputed_df = wide_to_long(
        transformed_df, intensity_df
    )

    return imputed_df, dict()


def by_knn_plot(df, result_df, current_out, graph_types, group_by):
    return _build_box_hist_plot(df, result_df, current_out, graph_types, group_by)


def number_of_imputed_values(input_df, result_df):
    # TODO: test this
    return abs(result_df.isnull().sum().sum() - input_df.isnull().sum().sum())


def _build_box_hist_plot(df, result_df, current_out, graph_types, group_by):
    """
        This function creates two visualisations:

        1. graph visualising the distributional
        differences between the protein intensities prior to
        and after imputation. Default is set to display a grouped
        graph (see group_by parameter).

        2. a graph summarising the amount of
        filtered proteins.

    """
    if "Boxplot" in graph_types:
        fig1 = create_box_plots(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Imputation",
            name_b="After Imputation",
            heading="Distribution of Protein Intensities",
            group_by=group_by,
        )
    if "Histogram" in graph_types:
        fig1 = create_histograms(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Imputation",
            name_b="After Imputation",
            heading="Distribution of Protein Intensities",
        )

    values_of_sectors = [
        abs(len(df)),
        number_of_imputed_values(df, result_df),
    ]
    if "Bar chart" in graph_types:
        fig2 = create_bar_plot(
            names_of_sectors=["Non-imputed values", "Imputed values"],
            values_of_sectors=values_of_sectors,
            heading="Number of Imputed Values",
        )
    if "Pie chart" in graph_types:
        fig2 = create_pie_plot(
            names_of_sectors=["Non-imputed values", "Imputed values"],
            values_of_sectors=values_of_sectors,
            heading="Number of Imputed Values",
        )
    return [fig1, fig2]
