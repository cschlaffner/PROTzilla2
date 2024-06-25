import pandas as pd

from protzilla.utilities import default_intensity_column


def long_to_wide(intensity_df: pd.DataFrame, value_name: str = None):
    """
    This function transforms the dataframe to a wide format that
    can be more easily handled by packages such as sklearn.
    Each sample gets one row with all observations as columns.

    :param intensity_df: the dataframe that should be transformed into
        long format
        :type intensity_df: pd.DataFrame

    :return: returns dataframe in wide format suitable for use by
        packages such as sklearn
    :rtype: pd.DataFrame
    """
    values_name = default_intensity_column(intensity_df) if value_name is None else value_name
    return pd.pivot(
        intensity_df, index="Sample", columns="Protein ID", values=values_name
    )


def wide_to_long(wide_df: pd.DataFrame, original_long_df: pd.DataFrame):
    """
    This functions transforms the dataframe from a wide
    format to the typical protzilla long format.

    :param wide_df: the dataframe in wide format that
        should be changed
    :type wide_df: pd.DataFrame
    :param original_long_df: the original long protzilla format
        dataframe, that was the source of the wide format dataframe
    :type orginal_long_df: pd.DataFrame

    :return: returns dataframe in typical protzilla long format
    :rtype: pd.DataFrame
    """
    # Read out info from original dataframe
    intensity_name = default_intensity_column(original_long_df)
    gene_info = original_long_df["Gene"]
    # Turn the wide format into the long format
    intensity_df = pd.melt(
        wide_df.reset_index(),
        id_vars="Sample",
        var_name="Protein ID",
        value_name=intensity_name,
    )
    intensity_df.sort_values(
        by=["Sample", "Protein ID"],
        ignore_index=True,
        inplace=True,
    )
    intensity_df.insert(2, "Gene", gene_info)

    return intensity_df


def is_long_format(df: pd.DataFrame):
    return set(df.columns[:3]) == {"Sample", "Protein ID", "Gene"}


def is_intensity_df(df: pd.DataFrame):
    """
    Checks if the dataframe is an intensity dataframe.
    An intensity dataframe should have the columns "Sample", "Protein ID" and
    and intensity column.

    :param df: the dataframe that should be checked
    :type df: pd.DataFrame

    :return: returns True if the dataframe is an intensity dataframe
    :rtype: bool
    """
    if not isinstance(df, pd.DataFrame):
        return False

    required_columns = {"Sample", "Protein ID"}
    if not required_columns.issubset(df.columns):
        return False

    intensity_names = [
        "Intensity",
        "iBAQ",
        "LFQ intensity",
        "MaxLFQ Total Intensity",
        "MaxLFQ Intensity",
        "Total Intensity",
        "MaxLFQ Unique Intensity",
        "Unique Spectral Count",
        "Unique Intensity",
        "Spectral Count",
        "Total Spectral Count",
    ]

    for column_name in df.columns:
        if any(intensity_name in column_name for intensity_name in intensity_names):
            return True

    return False
