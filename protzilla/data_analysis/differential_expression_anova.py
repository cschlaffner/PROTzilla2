import logging
import math

import pandas as pd
from scipy import stats

from protzilla.utilities import default_intensity_column

from .differential_expression_helper import apply_multiple_testing_correction


def anova(
    intensity_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    multiple_testing_correction_method: str,
    alpha: float,
    grouping: str,
    selected_groups: list = None,
    intensity_name: str = None,
) -> dict:
    """
    A function that uses ANOVA to test the difference between two or more
    groups defined in the clinical data. The ANOVA test is conducted on
    the level of each protein. The p-values are corrected for multiple
    testing.

    :param intensity_df: the dataframe that should be tested in long
        format
    :param metadata_df: the dataframe that contains the clinical data
    :param grouping: the column name of the grouping variable in the
        metadata_df
    :param selected_groups: groups to test against each other
    :type selected_groups: list, if None or empty: first two groups will be selected
    :param multiple_testing_correction_method: the method for multiple
        testing correction
    :param alpha: the alpha value for anova
    :param intensity_name: name of the column containing the protein group intensities
    :return: a dataframe in typical protzilla long format
        with the differentially expressed proteins and a dict, containing
        the corrected p-values and the log2 fold change, the alpha used
        and the corrected alpha, as well as filtered out proteins.
    """

    assert grouping in metadata_df.columns, f"{grouping} not found in metadata_df"
    messages = []
    # Check if the selected groups are present in the metadata_df

    # Select all groups if none or less than two were selected
    if not selected_groups or isinstance(selected_groups, str):
        selected_groups = metadata_df[grouping].unique()
        selected_groups_str = "".join([" " + str(group) for group in selected_groups])
        messages.append(
            {
                "level": logging.INFO,
                "msg": f"Auto-selected the groups {selected_groups_str} for comparison because none or only one group was selected.",
            }
        )
    elif len(selected_groups) >= 2:
        for group in selected_groups:
            if group not in metadata_df[grouping].unique():
                messages.append(
                    {
                        "level": logging.ERROR,
                        "msg": f"Group {group} not found in metadata_df.",
                    }
                )
                return {"messages": messages}

    # Merge the intensity and metadata dataframes in order to assign to each Sample
    # their corresponding group
    intensity_df = pd.merge(
        left=intensity_df,
        right=metadata_df[["Sample", grouping]],
        on="Sample",
        copy=False,
    )

    # Perform ANOVA and calculate p-values for each protein
    proteins = intensity_df["Protein ID"].unique()
    intensity_name = default_intensity_column(intensity_df, intensity_name)
    p_values = []
    valid_protein_groups = []
    for protein in proteins:
        protein_df = intensity_df[intensity_df["Protein ID"] == protein]
        all_group_intensities = []
        for group in selected_groups:
            all_group_intensities.append(
                protein_df[protein_df[grouping] == group][intensity_name].to_numpy()
            )
        p = stats.f_oneway(*all_group_intensities)[1]
        if not math.isnan(p):
            p_values.append(p)
            valid_protein_groups.append(protein)
        elif not any(message["level"] == logging.WARNING for message in messages):
            messages.append(
                {
                    "level": logging.WARNING,
                    "msg": "Due do missing or identical values, the p-values for some protein groups could not be calculated. These groups were omitted from the analysis. "
                    "To prevent this, please add filtering and imputation steps to your workflow before running the analysis.",
                }
            )

    # Apply multiple testing correction and create a dataframe with corrected p-values
    corrected_p_values, corrected_alpha = apply_multiple_testing_correction(
        p_values, multiple_testing_correction_method, alpha
    )
    corrected_p_values_df = pd.DataFrame(
        list(zip(valid_protein_groups, corrected_p_values)),
        columns=["Protein ID", "corrected_p_values"],
    )
    if corrected_alpha is None:
        corrected_alpha = alpha

    # Merge the corrected p-values with the original data
    # and filter out non-significant proteins
    tested_df = intensity_df.merge(corrected_p_values_df, on="Protein ID")
    filtered_df = tested_df.loc[tested_df["corrected_p_values"] < corrected_alpha]
    filtered_df.drop("corrected_p_values", axis=1, inplace=True)

    # Create mapping from sample to group
    sample_group_df = filtered_df[["Sample", grouping]].drop_duplicates()
    sample_group_df.set_index("Sample", inplace=True)
    return {
        "filtered_df": filtered_df,
        "corrected_p_values_df": corrected_p_values_df,
        "corrected_alpha": corrected_alpha,
        "sample_group_df": sample_group_df,
        "messages": messages,
    }
