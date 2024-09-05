import math

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.power import TTestIndPower


def check_sample_size_calculation_with_libfunc(
    differentially_expressed_proteins_df: pd.DataFrame,
    significant_proteins_df: pd.DataFrame,
    fc_threshold: float,
    alpha: float,
    power: float,
    group1: str,
    group2: str,
    selected_protein_group: str,
    intensity_name: str = None,
) -> dict:
    """
    Function to calculate the required sample size for a selected protein to achieve the required power .

    :param differentially_expressed_proteins_df: The dataframe containing the differentially expressed proteins from t-test output.
    :param significant_proteins_df: The dataframe containing the significant proteins from t-test output.
    :param fc_threshold: The fold change threshold.
    :param alpha: The significance level. The value for alpha is taken from the t-test by default.
    :param power: The power of the test.
    :param group1: The name of the first group.
    :param group2: The name of the second group.
    :param selected_protein_group: The selected protein group for which the required sample size is to be calculated.
    :param intensity_name: The name of the column containing the protein group intensities.
    :return: The required sample size.
    """

    if (
        selected_protein_group not in significant_proteins_df["Protein ID"].values
        and selected_protein_group
        not in differentially_expressed_proteins_df["Protein ID"].values
    ):
        raise ValueError("Please select a valid protein group.")

    protein_group = differentially_expressed_proteins_df[
        differentially_expressed_proteins_df["Protein ID"] == selected_protein_group
    ]

    group1_intensities = np.log2(
        protein_group[protein_group["Group"] == group1]["Normalised iBAQ"].values
    )
    group2_intensities = np.log2(
        protein_group[protein_group["Group"] == group2]["Normalised iBAQ"].values
    )
    variance_group1 = np.var(group1_intensities, ddof=1)
    variance_group2 = np.var(group2_intensities, ddof=1)

    sd_pooled = math.sqrt((variance_group1 + variance_group2) / 2)
    abs(group1_intensities.mean() - group2_intensities.mean())
    effect_size = (group1_intensities.mean() - group2_intensities.mean()) / sd_pooled

    obj = TTestIndPower()
    required_sample_size = obj.solve_power(
        effect_size=effect_size,
        alpha=alpha,
        power=power,
        nobs1=None,
        ratio=1.0,
        alternative="two-sided",
    )
    print(required_sample_size)

    required_sample_size = math.ceil(required_sample_size)

    return dict(required_sample_size=required_sample_size)
    # required_sample_size = 2.27; pooled_sd = 0.23; effect_size = 4.39, mean_diff = 1.014

    # impl: required_sample_size = 0.814; fc_threshold = 1.014; variance = 0.0534


def check_sample_size_calculation_implemented(
    differentially_expressed_proteins_df: pd.DataFrame,
    significant_proteins_df: pd.DataFrame,
    fc_threshold: float,
    alpha: float,
    power: float,
    group1: str,
    group2: str,
    selected_protein_group: str,
    intensity_name: str = None,
) -> dict:
    """
    Function to calculate the required sample size for a selected protein to achieve the required power .

    :param differentially_expressed_proteins_df: The dataframe containing the differentially expressed proteins from t-test output.
    :param significant_proteins_df: The dataframe containing the significant proteins from t-test output.
    :param fc_threshold: The fold change threshold.
    :param alpha: The significance level. The value for alpha is taken from the t-test by default.
    :param power: The power of the test.
    :param group1: The name of the first group.
    :param group2: The name of the second group.
    :param selected_protein_group: The selected protein group for which the required sample size is to be calculated.
    :param intensity_name: The name of the column containing the protein group intensities.
    :return: The required sample size.
    """

    if (
        selected_protein_group not in significant_proteins_df["Protein ID"].values
        and selected_protein_group
        not in differentially_expressed_proteins_df["Protein ID"].values
    ):
        raise ValueError("Please select a valid protein group.")

    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    protein_group = differentially_expressed_proteins_df[
        differentially_expressed_proteins_df["Protein ID"] == selected_protein_group
    ]

    group1_intensities = protein_group[protein_group["Group"] == group1][
        "Normalised iBAQ"
    ].values
    group2_intensities = protein_group[protein_group["Group"] == group2][
        "Normalised iBAQ"
    ].values
    fc_threshold = abs(group1_intensities.mean() - group2_intensities.mean())
    variance_group1 = np.var(group1_intensities, ddof=1)
    variance_group2 = np.var(group2_intensities, ddof=1)

    pooled_variance = (variance_group1 + variance_group2) / 2
    required_sample_size = (
        2 * ((z_alpha + z_beta) / fc_threshold) ** 2 * pooled_variance
    )
    required_sample_size = math.ceil(required_sample_size)
    print(required_sample_size)

    return dict(required_sample_size=required_sample_size)


def check_sample_size_calculation_implemented_without_log(
    differentially_expressed_proteins_df: pd.DataFrame,
    significant_proteins_df: pd.DataFrame,
    fc_threshold: float,
    alpha: float,
    power: float,
    group1: str,
    group2: str,
    selected_protein_group: str,
    intensity_name: str = None,
) -> dict:
    """
    Function to calculate the required sample size for a selected protein to achieve the required power .

    :param differentially_expressed_proteins_df: The dataframe containing the differentially expressed proteins from t-test output.
    :param significant_proteins_df: The dataframe containing the significant proteins from t-test output.
    :param fc_threshold: The fold change threshold.
    :param alpha: The significance level. The value for alpha is taken from the t-test by default.
    :param power: The power of the test.
    :param group1: The name of the first group.
    :param group2: The name of the second group.
    :param selected_protein_group: The selected protein group for which the required sample size is to be calculated.
    :param intensity_name: The name of the column containing the protein group intensities.
    :return: The required sample size.
    """

    if (
        selected_protein_group not in significant_proteins_df["Protein ID"].values
        and selected_protein_group
        not in differentially_expressed_proteins_df["Protein ID"].values
    ):
        raise ValueError("Please select a valid protein group.")

    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    protein_group = differentially_expressed_proteins_df[
        differentially_expressed_proteins_df["Protein ID"] == selected_protein_group
    ]

    group1_intensities = protein_group[protein_group["Group"] == group1][
        "Normalised iBAQ"
    ].values
    group2_intensities = protein_group[protein_group["Group"] == group2][
        "Normalised iBAQ"
    ].values
    fc_threshold = abs(group1_intensities.mean() - group2_intensities.mean())
    variance_group1 = np.var(group1_intensities, ddof=1)
    variance_group2 = np.var(group2_intensities, ddof=1)

    pooled_variance = (variance_group1 + variance_group2) / 2
    required_sample_size = (
        2 * ((z_alpha + z_beta) / fc_threshold) ** 2 * pooled_variance
    )
    required_sample_size = math.ceil(required_sample_size)
    print(required_sample_size)

    return dict(required_sample_size=required_sample_size)
