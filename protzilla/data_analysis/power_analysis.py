import math

import numpy as np
import pandas as pd
from scipy import stats
import plotly.express as px
import plotly.graph_objs as go
import protzilla.constants.colors as colorscheme

from ..constants.colors import PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE
from protzilla.utilities import default_intensity_column


def variance_protein_group_calculation_max(
    intensity_df: pd.DataFrame,
    protein_id: str,
    group1: str,
    group2: str,
    intensity_name: str = None,
) -> float:
    """
    Function to calculate the variance of a protein group for the two classes and return the maximum variance.

    :param intensity_df: The dataframe containing the protein group intensities.
    :param protein_id: The protein ID.
    :param group1: The name of the first group.
    :param group2: The name of the second group.
    :param intensity_name: The name of the column containing the protein group intensities.
    :return: The variance of the protein group.
    """
    intensity_name = default_intensity_column(intensity_df, intensity_name)
    protein_group = intensity_df[intensity_df["Protein ID"] == protein_id]

    group1_intensities = protein_group[protein_group["Group"] == group1][
        intensity_name
    ].values
    group2_intensities = protein_group[protein_group["Group"] == group2][
        intensity_name
    ].values

    variance_group1 = np.var(group1_intensities, ddof=1)
    variance_group2 = np.var(group2_intensities, ddof=1)

    max_variance = max(variance_group1, variance_group2)

    return max_variance


def sample_size_calculation(
    differentially_expressed_proteins_df: pd.DataFrame,
    significant_proteins_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    fc_threshold: float,
    alpha: float,
    power: float,
    group1: str,
    group2: str,
    selected_protein_group: str,
    individual_column: str,
    intensity_name: str = None,
) -> dict:
    """
    Function to calculate the required sample size for a selected protein to achieve the desired statistical power.
    If metadata_df contains a column that identifies individuals, the function first calculates the mean intensity for
    each individual (based on replicates) within the dataset. These individual means are used to determine the variance
    for the sample size calculation formula.

    :param differentially_expressed_proteins_df: The dataframe containing the differentially expressed proteins from t-test output.
    :param significant_proteins_df: The dataframe containing the significant proteins from t-test output.
    :param metadata_df: The dataframe containing the clinical data.
    :param fc_threshold: The fold change threshold.
    :param alpha: The significance level. The value for alpha is taken from the t-test by default.
    :param power: The power of the test.
    :param group1: The name of the first group.
    :param group2: The name of the second group.
    :param selected_protein_group: The selected protein group for which the required sample size is to be calculated.
    :param individual_column: The name of the column in metadata_df containing the individual ID.
    :param intensity_name: The name of the column containing the protein group intensities.
    :return: The required sample size.
    """

    if (
        selected_protein_group not in significant_proteins_df["Protein ID"].values
        and selected_protein_group
        not in differentially_expressed_proteins_df["Protein ID"].values
    ):
        raise ValueError("Please select a valid protein group.")
    protein_group = selected_protein_group
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    intensity_name = default_intensity_column(
        differentially_expressed_proteins_df, intensity_name
    )
    filtered_protein_group_df = differentially_expressed_proteins_df[
        differentially_expressed_proteins_df["Protein ID"] == protein_group
    ]

    if individual_column != "None" and individual_column in metadata_df.columns:
        # filtered_protein_group_df["Individual"] = filtered_protein_group_df["Sample"].apply(lambda x: x[:4])
        filtered_protein_group_merged_df = pd.merge(
            filtered_protein_group_df,
            metadata_df[["Sample", individual_column]],
            on="Sample",
        )
        # filtered_protein_group_df.join(metadata_df[["Sample", individual_column]].set_index("Sample"), on="Sample")

        filtered_protein_group_df = (
            filtered_protein_group_merged_df.groupby(
                ["Protein ID", "Group", individual_column]
            )[intensity_name]
            .mean()
            .reset_index()
        )

    variance_protein_group = variance_protein_group_calculation_max(
        intensity_df=filtered_protein_group_df,
        protein_id=protein_group,
        group1=group1,
        group2=group2,
        intensity_name=intensity_name,
    )

    required_sample_size = (
        2 * ((z_alpha + z_beta) / fc_threshold) ** 2 * variance_protein_group
    )  # Equation (1) in Cairns, David A., et al., 2008, Sample size determination in clinical proteomic profiling experiments using mass spectrometry for class comparison
    required_sample_size = math.ceil(required_sample_size)
    print(required_sample_size)

    return dict(required_sample_size=required_sample_size)


def power_calculation(
    differentially_expressed_proteins_df: pd.DataFrame,
    significant_proteins_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    alpha: float,
    fc_threshold: float,
    group1: str,
    group2: str,
    selected_protein_group: str,
    individual_column: str,
    intensity_name: str = None,
) -> dict:
    """
    Function to calculate the power of the t-test for a selected protein group.
    If metadata_df contains a column that identifies individuals, the function first calculates the mean intensity for
    each individual (based on replicates) within the dataset. These individual means are used to determine the variance
    for the power calculation formula.
    If both groups have different numbers of samples, the sample size for the power formula is calculated according
    to the equation 2.3.1 from Cohen 1988, Statistical Power Analysis for the Behavioral Sciences.

    :param differentially_expressed_proteins_df: The dataframe containing the differentially expressed proteins from t-test output.
    :param significant_proteins_df: The dataframe containing the significant proteins from t-test output.
    :param metadata_df: The dataframe containing the clinical data.
    :param alpha: The significance level. The value for alpha is taken from the t-test by default.
    :param fc_threshold: The fold change threshold.
    :param group1: The name of the first group.
    :param group2: The name of the second group.
    :param selected_protein_group: The selected protein group for which the power is to be calculated.
    :param individual_column: The name of the column in metadata_df containing the individual ID.
    :param intensity_name: The name of the column containing the protein group intensities.
    :return: The power of the test.
    """
    if (
        selected_protein_group not in significant_proteins_df["Protein ID"].values
        and selected_protein_group
        not in differentially_expressed_proteins_df["Protein ID"].values
    ):
        raise ValueError("Please select a valid protein group.")
    protein_group = selected_protein_group
    z_alpha = stats.norm.ppf(1 - alpha / 2)

    intensity_name = default_intensity_column(
        differentially_expressed_proteins_df, intensity_name
    )
    filtered_protein_group_df = differentially_expressed_proteins_df[
        differentially_expressed_proteins_df["Protein ID"] == protein_group
    ]
    if individual_column != "None" and individual_column in metadata_df.columns:
        filtered_protein_group_merged_df = pd.merge(
            filtered_protein_group_df,
            metadata_df[["Sample", individual_column]],
            on="Sample",
        )
        # filtered_protein_group_df.join(metadata_df[["Sample", individual_column]].set_index("Sample"), on="Sample")

        filtered_protein_group_df = (
            filtered_protein_group_merged_df.groupby(
                ["Protein ID", "Group", individual_column]
            )[intensity_name]
            .mean()
            .reset_index()
        )
        filtered_protein_group_df = filtered_protein_group_df.rename(
            columns={individual_column: "Sample"}
        )

    variance_protein_group = variance_protein_group_calculation_max(
        intensity_df=filtered_protein_group_df,
        protein_id=protein_group,
        group1=group1,
        group2=group2,
        intensity_name=intensity_name,
    )

    """
    filtered_df = differentially_expressed_proteins_df[differentially_expressed_proteins_df["Protein ID"] == protein_group]
    filtered_df["Person"] = filtered_df["Sample"].apply(
        lambda x: x[:7])

    variance = filtered_df.groupby(['Person', 'Group'])['Normalised iBAQ'].var().reset_index()

    filtered_df["Measurement"] = filtered_df["Sample"].apply(
        lambda x: int(x[-2:]))
    """

    group_count_df = filtered_protein_group_df.groupby(["Group", "Protein ID"])[
        "Sample"
    ].count()
    sample_size_group1 = group_count_df[group1][0]
    sample_size_group2 = group_count_df[group2][0]
    sample_size = (2 * sample_size_group1 * sample_size_group2) / (
        sample_size_group1 + sample_size_group2
    )  # Equation 2.3.1 from Cohen 1988, Statistical Power Analysis for the Behavioral Sciences
    z_beta = (
        fc_threshold * np.sqrt(sample_size / (2 * variance_protein_group)) - z_alpha
    )
    power = float(round(stats.norm.cdf(z_beta), 2))

    return dict(power=power)


def sample_size_calculation_for_all_proteins(
    differentially_expressed_proteins_df: pd.DataFrame,
    significant_proteins_df: pd.DataFrame,
    significant_proteins_only: str,
    metadata_df: pd.DataFrame,
    fc_threshold: float,
    alpha: float,
    power: float,
    group1: str,
    group2: str,
    individual_column: str,
    select_all_proteins: bool,
    selected_protein_groups: list,
    intensity_name: str = None,
) -> dict:
    """
    Function to calculate the required sample size for all proteins in the dataset to achieve the required power.

    :param differentially_expressed_proteins_df: The dataframe containing the differentially expressed proteins from t-test output.
    :param significant_proteins_df: The dataframe containing the significant proteins from t-test output.
    :param significant_proteins_only: A boolean indicating whether only significant proteins should be considered.
    :param metadata_df: The dataframe containing the clinical data.
    :param fc_threshold: The fold change threshold.
    :param alpha: The significance level. The value for alpha is taken from the t-test by default.
    :param power: The power of the test.
    :param group1: The name of the first group.
    :param group2: The name of the second group.
    :param individual_column: The name of the column in metadata_df containing the individual ID.
    :param select_all_proteins: A boolean indicating whether all proteins should be considered.
    :param selected_protein_groups: A list of selected protein groups, if not all proteins should be considered.
    :param intensity_name: The name of the column containing the protein group intensities.

    :return:
        - required_sample_size_for_all_proteins: The maximum required sample size for all proteins.
        - a violin plot showing the distribution of required sample sizes for all proteins.
        - a df differentially_expressed_proteins_df from t-test output with added sample size column.
        - a df significant_proteins_df from t-test output with added sample size column.
        - a df sample_size_dataframe containing the sample sizes for all proteins.
    """

    if select_all_proteins and significant_proteins_only == "No":
        protein_groups_for_calculation = differentially_expressed_proteins_df[
            "Protein ID"
        ].unique()
    elif select_all_proteins and significant_proteins_only == "Yes":
        protein_groups_for_calculation = significant_proteins_df["Protein ID"].unique()
    else:
        protein_groups_for_calculation = selected_protein_groups

    required_sample_sizes = []

    for protein_group in protein_groups_for_calculation:
        required_sample_size = sample_size_calculation(
            differentially_expressed_proteins_df=differentially_expressed_proteins_df,
            significant_proteins_df=significant_proteins_df,
            metadata_df=metadata_df,
            fc_threshold=fc_threshold,
            alpha=alpha,
            power=power,
            group1=group1,
            group2=group2,
            selected_protein_group=protein_group,
            individual_column=individual_column,
            intensity_name=intensity_name,
        )["required_sample_size"]

        required_sample_sizes.append(required_sample_size)

        required_sample_size_for_all_proteins = max(required_sample_sizes)

    colors = colorscheme.PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE

    fig = go.Figure(
        go.Violin(
            name="" * len(required_sample_sizes),
            y=required_sample_sizes,
            line_color=colors[1],
            meanline_visible=True,
            box_visible=True,
            scalemode="width",
            spanmode="hard",
            span=[0, required_sample_size_for_all_proteins],
            hoverinfo="y",
        )
    )

    fig.update_layout(
        title="Distribution of Required Sample Sizes for All Proteins",
        yaxis_title="Required Sample Size",
        showlegend=False,
    )
    sample_size_dataframe = pd.DataFrame(protein_groups_for_calculation)
    sample_size_dataframe.columns = ["Protein ID"]
    sample_size_dataframe["Sample Size"] = required_sample_sizes

    if select_all_proteins and significant_proteins_only == "No":
        differentially_expressed_proteins_df = pd.merge(
        differentially_expressed_proteins_df,
        sample_size_dataframe,
        on="Protein ID",
    )
    elif select_all_proteins and significant_proteins_only == "Yes":
        significant_proteins_df = pd.merge(
        significant_proteins_df,
        sample_size_dataframe,
        on="Protein ID",
    )

    return dict(
        required_sample_size_for_all_proteins=required_sample_size_for_all_proteins,
        plots=[fig],
        differentially_expressed_proteins_df=differentially_expressed_proteins_df,
        significant_proteins_df=significant_proteins_df,
        sample_size_dataframe=sample_size_dataframe,
    )

def power_calculation_for_all_proteins(
    differentially_expressed_proteins_df: pd.DataFrame,
    significant_proteins_df: pd.DataFrame,
    significant_proteins_only: str,
    metadata_df: pd.DataFrame,
    fc_threshold: float,
    alpha: float,
    group1: str,
    group2: str,
    individual_column: str,
    select_all_proteins: bool,
    selected_protein_groups: list,
    intensity_name: str = None,
) -> dict:
    """
    Function to calculate the power of the t-test for all proteins in the dataset.

    :param differentially_expressed_proteins_df: The dataframe containing the differentially expressed proteins from t-test output.
    :param significant_proteins_df: The dataframe containing the significant proteins from t-test output.
    :param significant_proteins_only: A boolean indicating whether only significant proteins should be considered.
    :param metadata_df: The dataframe containing the clinical data.
    :param fc_threshold: The fold change threshold.
    :param alpha: The significance level. The value for alpha is taken from the t-test by default.
    :param group1: The name of the first group.
    :param group2: The name of the second group.
    :param individual_column: The name of the column in metadata_df containing the individual ID.
    :param select_all_proteins: A boolean indicating whether all proteins should be considered.
    :param selected_protein_groups: A list of selected protein groups, if not all proteins should be considered.
    :param intensity_name: The name of the column containing the protein group intensities.

    :return:
        - power_for_all_proteins: The minimum power of all proteins.
        - a df differentially_expressed_proteins_df from t-test output with added power column.
        - a df significant_proteins_df from t-test output with added power column.
        - a df power_dataframe containing the power for all proteins.
    """
    if select_all_proteins and significant_proteins_only == "No":
        protein_groups_for_calculation = differentially_expressed_proteins_df[
            "Protein ID"
        ].unique()
    elif select_all_proteins and significant_proteins_only == "Yes":
        protein_groups_for_calculation = significant_proteins_df["Protein ID"].unique()
    else:
        protein_groups_for_calculation = selected_protein_groups

    power_list = []

    for protein_group in protein_groups_for_calculation:
        power = power_calculation(
            differentially_expressed_proteins_df=differentially_expressed_proteins_df,
            significant_proteins_df=significant_proteins_df,
            metadata_df=metadata_df,
            fc_threshold=fc_threshold,
            alpha=alpha,
            group1=group1,
            group2=group2,
            selected_protein_group=protein_group,
            individual_column=individual_column,
            intensity_name=intensity_name,
        )["power"]

        power_list.append(power)

        power_for_all_proteins = min(power_list)

    colors = colorscheme.PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE

    fig = go.Figure(
        go.Violin(
            name="" * len(power_list),
            y=power_list,
            line_color=colors[1],
            meanline_visible=True,
            box_visible=True,
            scalemode="width",
            spanmode="hard",
            span=[power_for_all_proteins, 1],
            hoverinfo="y"
        )
    )

    fig.update_layout(
        title="Distribution of Power for All Proteins",
        yaxis_title="Power",
        showlegend=False,
    )
    power_dataframe = pd.DataFrame(protein_groups_for_calculation)
    power_dataframe.columns = ["Protein ID"]
    power_dataframe["Power"] = power_list

    if select_all_proteins and significant_proteins_only == "No":
        differentially_expressed_proteins_df = pd.merge(
        differentially_expressed_proteins_df,
        power_dataframe,
        on="Protein ID",
    )
    elif select_all_proteins and significant_proteins_only == "Yes":
        significant_proteins_df = pd.merge(
        significant_proteins_df,
        power_dataframe,
        on="Protein ID",
    )

    return dict(
        power_for_all_proteins=power_for_all_proteins,
        plots=[fig],
        differentially_expressed_proteins_df=differentially_expressed_proteins_df,
        significant_proteins_df=significant_proteins_df,
        power_dataframe=power_dataframe,
    )
