import logging

import numpy as np
import pandas as pd
from scipy import stats

from protzilla.data_analysis.differential_expression_helper import _map_log_base, apply_multiple_testing_correction, \
    merge_differential_expression_and_significant_df, preprocess_grouping, normalize_ptm_df
from protzilla.utilities.transform_dfs import long_to_wide


def kruskal_wallis_test_on_intensity_data(
        protein_df: pd.DataFrame,
        metadata_df: pd.DataFrame,
        grouping: str,
        selected_groups: list = None,
        log_base: str = None,
        alpha=0.05,
        multiple_testing_correction_method: str = "Benjamini-Hochberg",
) -> dict:
    """
    Perform Kruskal Wallis test on all proteins in the given intensity data frame.

    @param protein_df: A protein dataframe in typical PROTzilla long format.
    @param metadata_df: The metadata data frame containing the grouping information.
    @param grouping: The column name in the metadata data frame that contains the grouping information,
        that should be used.
    @param selected_groups: groups to test against each other
    @param log_base: The base of the logarithm that was used to transform the data.
    @param alpha: The significance level for the test.
    @param multiple_testing_correction_method: The method for multiple testing correction.

    :return: a dict containing
        - a df differentially_expressed_proteins_df in long format containing all test results
        - a df significant_proteins_df, containing the proteins of differentially_expressed_column_df,
            that are significant after multiple testing correction
        - a df corrected_p_values, containing the p_values after application of multiple testing correction
        - a df h_statistic_df, containing the u-statistic per protein
        - a float corrected_alpha, containing the alpha value after application of multiple testing correction
            (depending on the selected multiple testing correction method corrected_alpha may be equal to alpha)
        - a list messages (optional), containing messages for the user
    """
    wide_df = long_to_wide(protein_df)

    outputs = kruskal_wallis_test_on_columns(
        df=wide_df,
        metadata_df=metadata_df,
        grouping=grouping,
        selected_groups=selected_groups,
        log_base=log_base,
        alpha=alpha,
        multiple_testing_correction_method=multiple_testing_correction_method,
        columns_name="Protein ID",
    )
    differentially_expressed_proteins_df, significant_proteins_df = (
        merge_differential_expression_and_significant_df(
            intensity_df=protein_df,
            diff_exp_df=outputs["differential_expressed_columns_df"],
            sig_df=outputs["significant_columns_df"]
        ))

    return dict(
        differentially_expressed_proteins_df=differentially_expressed_proteins_df,
        significant_proteins_df=significant_proteins_df,
        corrected_p_values_df=outputs["corrected_p_values_df"],
        h_statistic_df=outputs["h_statistic_df"],
        corrected_alpha=outputs["corrected_alpha"],
        messages=outputs["messages"],
    )

def kruskal_wallis_test_on_ptm_data(
        ptm_df: pd.DataFrame,
        metadata_df: pd.DataFrame,
        grouping: str,
        selected_groups: list = None,
        alpha=0.05,
        multiple_testing_correction_method: str = "Benjamini-Hochberg",
) -> dict:
    """
    Perform Kruskal Wallis test on all PTMs in the given PTM data frame.

    @param ptm_df: The data frame containing the PTM data in columns and a
        "Sample" column that can be mapped to the metadata, to assign the groups.
    @param metadata_df: The metadata data frame containing the grouping information.
    @param grouping: The column name in the metadata data frame that contains the grouping information,
        that should be used.
    @param selected_groups: groups to test against each other
    @param alpha: The significance level for the test.
    @param multiple_testing_correction_method: The method for multiple testing correction.

    :return: a dict containing
        - a df differentially_expressed_ptm_df in wide format containing all test results
        - a df significant_ptm_df, containing the ptm of differentially_expressed_column_df,
            that are significant after multiple testing correction
        - a df corrected_p_values, containing the p_values after application of multiple testing correction,
        - a df h_statistic_df, containing the t-statistic per protein,
        - a float corrected_alpha, containing the alpha value after application of multiple testing correction (depending on the selected multiple testing correction method corrected_alpha may be equal to alpha),
        - a list messages, containing messages for the user
    """

    normalized_ptm_df = normalize_ptm_df(ptm_df)

    output = kruskal_wallis_test_on_columns(
        df=normalized_ptm_df,
        metadata_df=metadata_df,
        grouping=grouping,
        selected_groups=selected_groups,
        log_base=None,
        alpha=alpha,
        multiple_testing_correction_method=multiple_testing_correction_method,
        columns_name="PTM",
    )

    return dict(
        differentially_expressed_ptm_df=output["differential_expressed_columns_df"],
        significant_ptm_df=output["significant_columns_df"],
        corrected_p_values_df=output["corrected_p_values_df"],
        h_statistic_df=output["h_statistic_df"],
        corrected_alpha=output["corrected_alpha"],
        messages=output["messages"],
    )


def kruskal_wallis_test_on_columns(
        df: pd.DataFrame,
        metadata_df: pd.DataFrame,
        grouping: str,
        selected_groups: list = None,
        log_base: str = None,
        alpha=0.05,
        multiple_testing_correction_method: str = "Benjamini-Hochberg",
        columns_name: str = "Protein ID",
) -> dict:
    """
    Perform Kruskal Wallis test on all columns of the data frame.

    @param df: The data frame containing the data in columns and a
    "Sample" column that can be mapped to the metadata, to assign the groups.
    @param metadata_df: The metadata data frame containing the grouping information.
    @param grouping: The column name in the metadata data frame that contains the grouping information,
    that should be used.
    @param selected_groups: groups to test against each other
    @param log_base: The base of the logarithm that was used to transform the data.
    @param alpha: The significance level for the test.
    @param multiple_testing_correction_method: The method for multiple testing correction.
    @param columns_name: The semantics of the column names. This is used to name the columns in the output data frames.

    :return: a dict containing
        - a df differentially_expressed_column_df in wide format containing the test results
        - a df significant_columns_df, containing the columns of differentially_expressed_column_df,
            that are significant after multiple testing correction
        - a df corrected_p_values, containing the p_values after application of multiple testing correction,
        - a df h_statistic_df, containing the t-statistic per protein,
        - a float corrected_alpha, containing the alpha value after application of multiple testing correction (depending on the selected multiple testing correction method corrected_alpha may be equal to alpha),
        - a list messages, containing messages for the user
    """
    selected_groups, messages = preprocess_grouping(metadata_df, grouping, selected_groups)

    df_with_groups = pd.merge(
        left=df,
        right=metadata_df[["Sample", grouping]],
        on="Sample",
        copy=False,
    )
    log_base = _map_log_base(log_base)  # now log_base in [2, 10, None]

    valid_columns = []
    p_values = []
    h_statistics = []
    invalid_columns = []
    data_columns = df.columns[~df.columns.isin(["Sample", grouping])]

    for column in data_columns:
        all_group_data = []
        for group in selected_groups:
            all_group_data.append(
                df_with_groups[df_with_groups[grouping] == group][column]
            )
        try:
            h_statistic, p_value = stats.kruskal(*all_group_data)
        except ValueError:
            invalid_columns.append(column)
            continue

        if not np.isnan(p_value):
            valid_columns.append(column)
            p_values.append(p_value)
            h_statistics.append(h_statistic)
        else:
            invalid_columns.append(column)

    corrected_p_values, corrected_alpha = apply_multiple_testing_correction(
        p_values=p_values,
        method=multiple_testing_correction_method,
        alpha=alpha,
    )

    corrected_p_values_df = pd.DataFrame(
        list(zip(valid_columns, corrected_p_values)),
        columns=[columns_name, "corrected_p_value"],
    )
    h_statistic_df = pd.DataFrame(
        list(zip(valid_columns, h_statistics)),
        columns=[columns_name, "h_statistic"],
    )

    combined_df = pd.DataFrame(
        list(zip(valid_columns, corrected_p_values, h_statistics)),
        columns=[columns_name, "corrected_p_value", "h_statistic"],
    )

    significant_columns_df = combined_df[
        combined_df["corrected_p_value"] <= corrected_alpha
        ]

    if invalid_columns:
        messages.append(dict(level=logging.INFO, msg=f"Invalid columns: {invalid_columns}"))

    return dict(
        differential_expressed_columns_df=combined_df,
        significant_columns_df=significant_columns_df,
        corrected_p_values_df=corrected_p_values_df,
        h_statistic_df=h_statistic_df,
        corrected_alpha=corrected_alpha,
        messages=messages,
    )
