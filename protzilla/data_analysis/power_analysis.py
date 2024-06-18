import logging

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.power import TTestIndPower


def variance_protein_group_calculation(
    intensity_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    protein_id: str,
    group1: str,
    group2: str,
    intensity_name: str = None,
) -> float:
    """
    Function to calculate the variance of a protein group for the two classes and return the maximum variance.

    :param intensity_df: The dataframe containing the protein group intensities.
    :param metadata_df: The dataframe containing the metadata.
    :param protein_id: The protein ID.
    :param group1: The name of the first group.
    :param group2: The name of the second group.
    :param intensity_name: The name of the column containing the protein group intensities.
    :return: The variance of the protein group.
    """

    if intensity_name is None:
        intensity_name = "Intensity"

    protein_group = intensity_df[intensity_df["Protein ID"] == protein_id]

    protein_group = pd.merge(
        left=protein_group,
        right=metadata_df[["Sample", "Group"]],
        on="Sample",
        copy=False,
    )


    group1_intensities = protein_group[protein_group["Group"] == group1][intensity_name].values
    group2_intensities = protein_group[protein_group["Group"] == group2][intensity_name].values

    variance_group1 = np.var(group1_intensities, ddof=1)
    variance_group2 = np.var(group2_intensities, ddof=1)

    max_variance = max(variance_group1, variance_group2)

    return max_variance

def sample_size_calculation(
    differentially_expressed_proteins_df: pd.DataFrame,
    significant_proteins_df: pd.DataFrame,
    significant_proteins_only: bool,
    metadata_df: pd.DataFrame,
    fc_threshold: float,
    alpha: float,
    power: float,
    group1: str,
    group2: str,
    selected_protein_group: str,
    intensity_name: str = None
) -> pd.DataFrame:
    """
    Function to calculate the required sample size for each significant protein to achieve the required power .

    :param significant_proteins_df: The dataframe containing the significant proteins from t-test output.
    :param alpha: The significance level.
    :param power: The power of the test.
    :param group1: The name of the first group.
    :param group2: The name of the second group.
    :param intensity_name: The name of the column containing the protein group intensities.
    :return: The required sample size.
    """

    if selected_protein_group not in significant_proteins_df['Protein ID'].values and selected_protein_group not in differentially_expressed_proteins_df['Protein ID'].values:
        raise ValueError("Please select a valid protein group.")
    protein_group = selected_protein_group
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    variance_protein_group = variance_protein_group_calculation(
        intensity_df=differentially_expressed_proteins_df,
        metadata_df=metadata_df,
        protein_id=protein_group,
        group1=group1,
        group2=group2,
        intensity_name=intensity_name,
    )

    required_sample_size = (2 * ((z_alpha + z_beta)/ fc_threshold) ** 2 * variance_protein_group)

    print(required_sample_size)

    return required_sample_size



