import logging

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
from protzilla.utilities import default_intensity_column
from protzilla.utilities.transform_dfs import long_to_wide, wide_to_long


def flag_invalid_values(df: pd.DataFrame, messages: list) -> dict:
    """
    A function to check if there are any NaN values in the dataframe.
    Also checks if some Protein groups have completely identical values for each sample.
    If so, add a warning to the messages list.
    :param df: the dataframe that should be checked
    :return: True if there are NaN values in the dataframe, False otherwise
    """
    if df.isnull().values.any():
        columns_with_nan = df.columns[df.isna().any()].tolist()
        try:
            columns_with_nan.remove("Gene")
        except ValueError:
            pass

        if len(columns_with_nan) > 0:
            messages.append(
                {
                    "level": logging.WARNING,
                    "msg": f"Some NaN values remain in {columns_with_nan} of the imputed dataframe, indicating an unfiltered dataset and / or insufficient data. "
                    "Possible solutions to this include adding a filtering step before this imputation step in the preprocessing section to your workflow, "
                    "or using a different imputation method.",
                }
            )

    # Group by 'Protein ID' and check if all values in each group are identical
    identical_values_warning_given = False
    for protein_id, group in df.groupby("Protein ID"):
        if group.nunique().nunique() == 1 and not identical_values_warning_given:
            messages.append(
                {
                    "level": logging.WARNING,
                    "msg": f"Some Protein groups have completely identical values for each sample.",
                }
            )
            identical_values_warning_given = True

    return dict(protein_df=df, messages=messages)


def by_knn(
    protein_df: pd.DataFrame,
    number_of_neighbours: int = 5,
    **kwargs,  # quantile, default is median
) -> dict:
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

    :param protein_df: the dataframe that should be filtered in
        long format
    :type protein_df: pandas DataFrame
    :param number_of_neighbours: number of neighbouring samples used for
        imputation. Default: 5
    :type number_of_neighbours: int
    :param **kwargs: additional keyword arguments passed to
        KNNImputer.fit_transform
    :type kwargs: dict
    :return: returns an imputed dataframe in typical protzilla long format
        and a list of messages
    :rtype: pd.DataFrame
    """

    transformed_df = long_to_wide(protein_df)
    transformed_df.dropna(axis=1, how="all", inplace=True)
    index = transformed_df.index
    columns = transformed_df.columns

    imputer = KNNImputer(n_neighbors=number_of_neighbours)
    transformed_df = imputer.fit_transform(transformed_df, **kwargs)
    transformed_df = pd.DataFrame(transformed_df, columns=columns, index=index)

    # Turn the wide format into the long format
    imputed_df = wide_to_long(transformed_df, protein_df)

    return flag_invalid_values(imputed_df, [])


def by_simple_imputer(
    protein_df: pd.DataFrame,
    strategy: str = "mean",
) -> dict:
    """
    A function to perform protein-wise imputations
    on your dataframe. Imputes missing values for each protein
    taking into account data from each protein.

    Imputation methods include imputation by mean, median and
    mode. Implements the sklearn.SimpleImputer class.
    https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html
    CAVE: If there are no intensities for a protein,
    no data will be imputed. This function automatically filters
    out such proteins from the DataFrame beforehand.

    :param protein_df: the dataframe that should be filtered in
        long format
    :param strategy: Defines the imputation strategy. Can be "mean",
        "median" or "most_frequent" (for mode).

    :return: returns an imputed dataframe in typical protzilla long format
        a list of messages
    """
    assert strategy in ["mean", "median", "most_frequent"]
    transformed_df = long_to_wide(protein_df)
    transformed_df.dropna(axis=1, how="all", inplace=True)

    index = transformed_df.index
    columns = transformed_df.columns

    imputer = SimpleImputer(missing_values=np.nan, strategy=strategy)
    transformed_df = imputer.fit_transform(transformed_df)
    transformed_df = pd.DataFrame(transformed_df, columns=columns, index=index)

    # Turn the wide format into the long format
    imputed_df = wide_to_long(transformed_df, protein_df)
    return flag_invalid_values(imputed_df, [])


def by_min_per_sample(
    protein_df: pd.DataFrame,
    shrinking_value: float = 1,
) -> dict:
    """
    A function to perform  minimal value imputation on the level
    of samples of your dataframe. Imputes missing values for each
    protein taking into account data from each sample.

    Sets missing intensity values to the smallest measured value
    for each sample. The user can also assign a shrinking factor to
    take a fraction of that minimum value for imputation.
    CAVE: Data for samples without any intensity values will not
    be filtered out and NaN values could remain in the dataframe.
    If not wanted, make sure to filter 0 intensity samples in the
    filtering step.

    :param protein_df: the dataframe that should be filtered in
        long format
    :param shrinking_value: a factor to alter the minimum value
        used for imputation. With a shrinking factor of 0.1 for
        example, a tenth of the minimum value found will be used for
        imputation. Default: 1 (no shrinking)

    :return: returns an imputed dataframe in typical protzilla long format
        a list of messages
    """
    protein_df_copy = protein_df.copy(deep=True)
    intensity_name = default_intensity_column(protein_df_copy)
    samples = protein_df_copy["Sample"].unique().tolist()
    for sample in samples:
        location = protein_df_copy[intensity_name].loc[
            protein_df_copy["Sample"] == sample,
        ]
        if location.isnull().all():
            continue
        else:
            location.fillna(location.min() * shrinking_value, inplace=True)
            protein_df_copy[intensity_name].update(location)
    return flag_invalid_values(protein_df_copy, [])


def by_min_per_protein(
    protein_df: pd.DataFrame,
    shrinking_value: float = 1,
) -> dict:
    """
    A function to impute missing values for each protein
    by taking into account data from each protein.
    Sets missing value to the smallest measured value for each
    protein column. The user can also assign a shrinking factor to
    take a fraction of that minimum value for imputation.
    CAVE: All proteins without any values will be filtered out.

    :param protein_df: the dataframe that should be filtered in
        long format
    :param shrinking_value: a factor to alter the minimum value
        used for imputation. With a shrinking factor of 0.1 for
        example, a tenth of the minimum value found will be used for
        imputation. Default: 1 (no shrinking)

    :return: returns an imputed dataframe in typical protzilla long format
        a list of messages
    """
    transformed_df = long_to_wide(protein_df)
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
    imputed_df = wide_to_long(transformed_df, protein_df)

    return flag_invalid_values(imputed_df, [])


def by_min_per_dataset(
    protein_df: pd.DataFrame,
    shrinking_value: float = 1,
) -> dict:
    """
    A function to impute missing values for each protein
    by taking into account data from the entire dataframe.
    Sets missing value to the smallest measured value in
    the dataframe. The user can also assign a shrinking factor to
    take a fraction of that minimum value for imputation.

    :param protein_df: the dataframe that should be filtered in
        long format
    :param shrinking_value: a factor to alter the minimum value
        used for imputation. With a shrinking factor of 0.1 for
        example, a tenth of the minimum value found will be used for
        imputation. Default: 1 (no shrinking)

    :return: returns an imputed dataframe in typical protzilla long format
        a list of messages
    """
    protein_df_copy = protein_df.copy(deep=True)
    intensity_name = default_intensity_column(protein_df_copy)
    protein_df_copy[intensity_name].fillna(
        protein_df_copy[intensity_name].min() * shrinking_value,
        inplace=True,
    )
    return flag_invalid_values(protein_df_copy, [])


def by_normal_distribution_sampling(
    protein_df: pd.DataFrame,
    strategy: str = "perProtein",
    down_shift: float = 0,
    scaling_factor: float = 1,
) -> dict:
    """
    A function to perform imputation via sampling of a normal distribution
    defined by the existing datapoints and user-defined parameters for down-
    shifting and scaling. Imputes missing values for each protein  taking into
    account data from each protein or the whole dataset. The data is log-
    transformed before sampling from the normal distribution and transformed
    back afterwards, meaning only values > 0 are imputed.
    Will not impute if insufficient data is available for sampling.
    :param protein_df: the dataframe that should be filtered in
    long format
    :param strategy: which strategy to use for definition of the normal
    distribution to be sampled. Can be "perProtein", "perDataset" or "most_frequent"
    :param down_shift: a factor defining how many dataset standard deviations
    to shift the mean of the normal distribution used for imputation.
    Default: 0 (no shift)
    :param scaling_factor: a factor determining how the variance of the normal
    distribution used for imputation is scaled compared to dataset.
    Default: 1 (no scaling)
    :return: returns an imputed dataframe in typical protzilla long format\
    a list of messages
    """
    assert strategy in ["perProtein", "perDataset"]

    if strategy == "perProtein":
        transformed_df = long_to_wide(protein_df)
        # iterate over all protein groups
        for protein_grp in transformed_df.columns:
            number_of_nans = transformed_df[protein_grp].isnull().sum()

            if number_of_nans > len(transformed_df[protein_grp]) - 2:
                continue

            location_of_nans = transformed_df[protein_grp].isnull()
            indices_of_nans = location_of_nans[location_of_nans].index

            protein_grp_mean = np.log10(transformed_df[protein_grp]).mean(skipna=True)
            protein_grp_std = np.log10(transformed_df[protein_grp]).std(skipna=True)
            sampling_mean = protein_grp_mean + down_shift * protein_grp_std
            sampling_std = protein_grp_std * scaling_factor

            # calculate log-transformed values to be imputed
            log_impute_values = np.random.normal(
                loc=sampling_mean,
                scale=sampling_std,
                size=number_of_nans,
            )
            # transform log-transformed values to be imputed back to normal scale and round to nearest integer
            impute_values = 10**log_impute_values

            # zip indices of NaN values with values to be imputed together as a Series, such that fillna can be used
            impute_value_series = pd.Series(impute_values, index=indices_of_nans)
            transformed_df[protein_grp].fillna(impute_value_series, inplace=True)

        imputed_df = wide_to_long(transformed_df, protein_df)
        return flag_invalid_values(imputed_df, [])

    else:
        # determine column for protein intensities
        intensity_type = default_intensity_column(protein_df)

        number_of_nans = protein_df[intensity_type].isnull().sum()
        assert number_of_nans <= len(protein_df[intensity_type]) - 2

        location_of_nans = protein_df[intensity_type].isnull()
        indices_of_nans = location_of_nans[location_of_nans].index

        dataset_mean = np.log10(protein_df[intensity_type]).mean()
        dataset_std = np.log10(protein_df[intensity_type]).std()
        sampling_mean = max(0, dataset_mean + down_shift * dataset_std)
        sampling_std = dataset_std * scaling_factor

        # calculate log-transformed values to be imputed
        log_impute_values = abs(
            np.random.normal(
                loc=sampling_mean,
                scale=sampling_std,
                size=number_of_nans,
            )
        )
        # transform log-transformed values to be imputed back to normal scale and round to nearest integer
        impute_values = 10**log_impute_values

        # zip indices of NaN values with values to be imputed together as a Series, such that fillna can be used
        impute_value_series = pd.Series(impute_values, index=indices_of_nans)
        protein_df[intensity_type].fillna(impute_value_series, inplace=True)

        return flag_invalid_values(protein_df, [])


def by_knn_plot(
    method_inputs,
    method_outputs,
    graph_type,
    graph_type_quantities,
    group_by,
    visual_transformation,
):
    return _build_box_hist_plot(
        method_inputs["protein_df"],
        method_outputs["protein_df"],
        graph_type,
        graph_type_quantities,
        group_by,
        visual_transformation,
    )


def by_normal_distribution_sampling_plot(
    method_inputs,
    method_outputs,
    graph_type,
    graph_type_quantities,
    group_by,
    visual_transformation,
):
    return _build_box_hist_plot(
        method_inputs["protein_df"],
        method_outputs["protein_df"],
        graph_type,
        graph_type_quantities,
        group_by,
        visual_transformation,
    )


def by_simple_imputer_plot(
    method_inputs,
    method_outputs,
    graph_type,
    graph_type_quantities,
    group_by,
    visual_transformation,
):
    return _build_box_hist_plot(
        method_inputs["protein_df"],
        method_outputs["protein_df"],
        graph_type,
        graph_type_quantities,
        group_by,
        visual_transformation,
    )


def by_min_per_sample_plot(
    method_inputs,
    method_outputs,
    graph_type,
    graph_type_quantities,
    group_by,
    visual_transformation,
):
    return _build_box_hist_plot(
        method_inputs["protein_df"],
        method_outputs["protein_df"],
        graph_type,
        graph_type_quantities,
        group_by,
        visual_transformation,
    )


def by_min_per_protein_plot(
    method_inputs,
    method_outputs,
    graph_type,
    graph_type_quantities,
    group_by,
    visual_transformation,
):
    return _build_box_hist_plot(
        method_inputs["protein_df"],
        method_outputs["protein_df"],
        graph_type,
        graph_type_quantities,
        group_by,
        visual_transformation,
    )


def by_min_per_dataset_plot(
    method_inputs,
    method_outputs,
    graph_type,
    graph_type_quantities,
    group_by,
    visual_transformation,
):
    return _build_box_hist_plot(
        method_inputs["protein_df"],
        method_outputs["protein_df"],
        graph_type,
        graph_type_quantities,
        group_by,
        visual_transformation,
    )


def number_of_imputed_values(input_df, result_df):
    return abs(result_df.isnull().sum().sum() - input_df.isnull().sum().sum())


def _build_box_hist_plot(
    df: pd.DataFrame,
    result_df: pd.DataFrame,
    graph_type: str = "Boxplot",
    graph_type_quantities: str = "Pie chart",
    group_by: str = "None",
    visual_transformation: str = "linear",
) -> list[Figure]:
    """
    This function creates two visualisations:

    1. graph visualising the distributional
    differences between the protein intensities prior to
    and after imputation. Default is set to display a grouped
    graph (see group_by parameter).

    2. a graph summarising the amount of
    filtered proteins.
    """

    intensity_name_df = df.columns[3]
    intensity_name_result_df = result_df.columns[3]

    imputed_df = result_df.copy()

    imputed_df[intensity_name_result_df] = list(
        map(
            lambda x, y: y if np.isnan(x) else np.nan,
            df[intensity_name_df],
            result_df[intensity_name_result_df],
        )
    )

    if graph_type == "Boxplot":
        fig1 = create_box_plots(
            dataframe_a=df,
            dataframe_b=imputed_df,
            name_a="Original Values",
            name_b="Imputed Values",
            heading="Distribution of Protein Intensities",
            group_by=group_by,
            visual_transformation=visual_transformation,
            y_title="Intensity",
        )
    elif graph_type == "Histogram":
        fig1 = create_histograms(
            dataframe_a=df,
            dataframe_b=imputed_df,
            name_a="Original Values",
            name_b="Imputed Values",
            heading="Distribution of Protein Intensities",
            visual_transformation=visual_transformation,
            overlay=True,
            x_title="Protein Intensities",
            y_title="Frequency of Protein Intensities",
        )

    values_of_sectors = [
        abs(len(df)),
        number_of_imputed_values(df, result_df),
    ]
    if graph_type_quantities == "Bar chart":
        fig2 = create_bar_plot(
            names_of_sectors=["Non-imputed values", "Imputed values"],
            values_of_sectors=values_of_sectors,
            heading="Number of Imputed Values",
            y_title="Number of Values",
        )
    elif graph_type_quantities == "Pie chart":
        fig2 = create_pie_plot(
            names_of_sectors=["Non-imputed values", "Imputed values"],
            values_of_sectors=values_of_sectors,
            heading="Number of Imputed Values",
        )
    return [fig1, fig2]
