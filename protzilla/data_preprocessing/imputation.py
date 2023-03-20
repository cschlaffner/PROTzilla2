import numpy as np
import pandas as pd
from plotly.graph_objs import Figure
from sklearn.impute import KNNImputer, SimpleImputer

from protzilla.data_preprocessing.plots import (
    create_bar_plot,
    create_box_plots,
    create_histograms,
    create_pie_plot,
)
from protzilla.utilities.transform_dfs import long_to_wide, wide_to_long


def by_knn(
    intensity_df: pd.DataFrame,
    number_of_neighbours=5,
    **kwargs  # quantile, default is median
) -> tuple[pd.DataFrame, dict]:
    """
    A function to perform value imputation based on KNN
    (k-nearest neighbors). Imputes missing values for each
    sample based on intensity-wise similar samples.
    Two samples are close if the features that neither is
    missing are close.
    CAVE: Proteins that have NaN in all samples will be
    filtered out if not previously filtered out!

    Implements an instance of the sklearn.impute KNNImputer
    class.
    https://scikit-learn.org/stable/modules/generated/sklearn.impute.KNNImputer.html
    :param intensity_df: the dataframe that should be filtered in\
    long format
    :type intensity_df: pandas DataFrame
    :param number_of_neighbours: number of neighbouring samples used for\
    imputation. Default: 5
    :type number_of_neighbours: int
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

    imputer = KNNImputer(n_neighbors=number_of_neighbours)
    transformed_df = imputer.fit_transform(transformed_df, **kwargs)
    transformed_df = pd.DataFrame(transformed_df, columns=columns, index=index)

    # Turn the wide format into the long format
    imputed_df = wide_to_long(transformed_df, intensity_df)

    return imputed_df, dict()


def by_simple_imputer(
    intensity_df: pd.DataFrame,
    strategy="mean",
) -> tuple[pd.DataFrame, dict]:
    """
    A class to perform protein-wise imputations
    on your dataframe. Imputes missing values for each protein
    taking into account data from each protein.

    Imputation methods include imputation by mean, median and
    mode. Implements the sklearn.SimpleImputer class.
    https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html
    CAVE: If there are no intensities for a protein,
    no data will be imputed. This function automatically filters
    out such proteins from the DataFrame beforehand.

    :param intensity_df: the dataframe that should be filtered in\
    long format
    :type intensity_df: pandas DataFrame
    :param strategy: Defines the imputation strategy. Can be "mean",\
    "median" or "most_frequent" (for mode).
    :type strategy: str
    :return: returns an imputed dataframe in typical protzilla long format\
    and an empty dict
    :rtype: pd.DataFrame, int
    """
    assert strategy in ["mean", "median", "most_frequent"]
    transformed_df = long_to_wide(intensity_df)
    transformed_df.dropna(axis=1, how="all", inplace=True)

    index = transformed_df.index
    columns = transformed_df.columns

    imputer = SimpleImputer(missing_values=np.nan, strategy=strategy)
    transformed_df = imputer.fit_transform(transformed_df)
    transformed_df = pd.DataFrame(transformed_df, columns=columns, index=index)

    # Turn the wide format into the long format
    imputed_df = wide_to_long(transformed_df, intensity_df)
    return imputed_df, dict()


def by_min_per_sample(
    intensity_df: pd.DataFrame,
    shrinking_value=0.5,
) -> tuple[pd.DataFrame, dict]:
    """
    A class to perform  minimal value imputation on the level
    of samples of your dataframe. Imputes missing values for each
    protein taking into account data from each sample.

    Sets missing intensity values to the smallest measured value
    for each sample. The user can also assign a shrinking factor to
    take a fraction of that minimum value for imputation.
    CAVE: Data for samples without any intensity values will not
    be filtered out and NaN values could remain in the dataframe.
    If not wanted, make sure to filter 0 intensity samples in the
    filtering step.

    :param intensity_df: the dataframe that should be filtered in\
    long format
    :type intensity_df: pandas DataFrame
    :param shrinking_value: a factor to alter the minimum value\
    used for imputation. With a shrinking factor of 0.1 for\
    example, a tenth of the minimum value found will be used for\
    imputation. Default: 0.5 (half of the minimum value)
    :type shrinking_value: float
    :return: returns an imputed dataframe in typical protzilla long format\
    and an empty dict
    :rtype: pd.DataFrame, dict
    """
    intensity_df_copy = intensity_df.copy(deep=True)
    intensity_name = intensity_df_copy.columns[3]
    samples = intensity_df_copy["Sample"].unique().tolist()
    for sample in samples:
        location = intensity_df_copy[intensity_name].loc[
            intensity_df_copy["Sample"] == sample,
        ]
        if location.isnull().all():
            continue
        else:
            location.fillna(location.min() * shrinking_value, inplace=True)
            intensity_df_copy[intensity_name].update(location)
    return intensity_df_copy, dict()


def by_min_per_protein(
    intensity_df: pd.DataFrame,
    shrinking_value=0.5,
) -> tuple[pd.DataFrame, dict]:
    """
    A function to impute missing values for each protein
    by taking into account data from each protein.
    Sets missing value to the smallest measured value for each
    protein column. The user can also assign a shrinking factor to
    take a fraction of that minimum value for imputation.
    CAVE: All proteins without any values will be filtered out.

    :param intensity_df: the dataframe that should be filtered in\
    long format
    :type intensity_df: pandas DataFrame
    :param shrinking_value: a factor to alter the minimum value\
    used for imputation. With a shrinking factor of 0.1 for\
    example, a tenth of the minimum value found will be used for\
    imputation. Default: 0.5 (half of the minimum value)
    :type shrinking_value: float
    :return: returns an imputed dataframe in typical protzilla long format\
    and an empty dict
    :rtype: pd.DataFrame, dict
    """
    transformed_df = long_to_wide(intensity_df)
    transformed_df.dropna(axis=1, how="all", inplace=True)
    columns = transformed_df.columns

    # Iterate over proteins to impute minimal value
    for column in columns:
        transformed_df[column].fillna(
            transformed_df[column].min() * shrinking_value, inplace=True
        )
    # this implementation seems to work with all protein columns that
    # contain data if used with 0 intensity protein filtering
    # it would work perfectly
    # CAVE: By use of the shrinking value all NaN's are turned to 0
    # - we thus decided to filter them out beforehand.

    # Turn the wide format into the long format
    imputed_df = wide_to_long(transformed_df, intensity_df)

    return imputed_df, dict()


def by_min_per_dataset(
    intensity_df: pd.DataFrame,
    shrinking_value=0.5,
) -> tuple[pd.DataFrame, dict]:
    """
    A function to impute missing values for each protein
    by taking into account data from the entire dataframe.
    Sets missing value to the smallest measured value in
    the dataframe. The user can also assign a shrinking factor to
    take a fraction of that minimum value for imputation.

    :param intensity_df: the dataframe that should be filtered in\
    long format
    :type intensity_df: pandas DataFrame
    :param shrinking_value: a factor to alter the minimum value\
    used for imputation. With a shrinking factor of 0.1 for\
    example, a tenth of the minimum value found will be used for\
    imputation. Default: 0.5 (half of the minimum value)
    :type shrinking_value: float
    :return: returns an imputed dataframe in typical protzilla long format\
    and an empty dict
    :rtype: pd.DataFrame, dict
    """
    intensity_df_copy = intensity_df.copy(deep=True)
    intensity_name = intensity_df_copy.columns[3]
    intensity_df_copy[intensity_name].fillna(
        intensity_df_copy[intensity_name].min() * shrinking_value,
        inplace=True,
    )
    return intensity_df_copy, dict()


def by_knn_plot(df, result_df, graph_types, group_by):
    return _build_box_hist_plot(df, result_df, graph_types, group_by)


def by_simple_imputer_plot(df, result_df, graph_types, group_by):
    return _build_box_hist_plot(df, result_df, graph_types, group_by)


def by_min_per_sample_plot(df, result_df, graph_types, group_by):
    return _build_box_hist_plot(df, result_df, graph_types, group_by)


def by_min_per_protein_plot(df, result_df, graph_types, group_by):
    return _build_box_hist_plot(df, result_df, graph_types, group_by)


def by_min_per_dataset_plot(df, result_df, graph_types, group_by):
    return _build_box_hist_plot(df, result_df, graph_types, group_by)


def number_of_imputed_values(input_df, result_df):
    return abs(result_df.isnull().sum().sum() - input_df.isnull().sum().sum())


def _build_box_hist_plot(df, result_df, graph_types, group_by) -> list[Figure]:
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
