import pandas as pd


def long_to_wide(intensity_df: pd.DataFrame):
    """
        This function transforms the dataframe to a wide format that
        can be more easily handled by packages such as sklearn.
        Each sample gets one row with all observations as columns.

        :param intensity_df: the dataframe that should be changed in\
        long format
        :type intensity_df: pd.DataFrame
        :return: returns dataframe in wide format suitable for use by\
        packages such as sklearn
        :rtype: pd.DataFrame
        """
    values_name = intensity_df.columns[3]
    return pd.pivot(
        intensity_df, index="Sample", columns="Protein ID", values=values_name
    )
    # df = pd.pivot(
    #     intensity_df, index="Sample", columns="Protein ID", values=values_name
    # )
    # # df.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)
    # return df


def wide_to_long(wide_df: pd.DataFrame, original_long_df: pd.DataFrame):
    """
    This functions transforms the dataframe from a wide
    format to the typical protzilla long format.

    :param wide_df: the dataframe in wide format that\
    should be changed
    :type wide_df: pd.DataFrame
    :param original_long_df: the original long protzilla format\
    dataframe, that was the source of the wide format dataframe
    :type orginal_long_df: pd.DataFrame
    :return: returns dataframe in typical protzilla long format
    :rtype: pd.DataFrame
    """
    # Read out info from original dataframe
    intensity_name = original_long_df.columns[3]
    gene_info = original_long_df["Gene"]
    # Turn the wide format into the long format
    intensity_df = pd.melt(
        wide_df.reset_index(),
        id_vars="Sample",
        var_name="Protein ID",
        value_name=intensity_name,
    )
    intensity_df.sort_values(
        # by=["Protein ID", "Sample"], ignore_index=True, inplace=True # TODO: swap "Protein ID", "Sample"
        by=["Sample", "Protein ID"],
        ignore_index=True,
        inplace=True,  # TODO: swap "Protein ID", "Sample"
    )
    intensity_df.insert(2, "Gene", gene_info)  # TODO: insert at 2 instead of 1

    return intensity_df
