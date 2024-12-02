from pyexpat.errors import messages
import logging

import numpy as np
import pandas as pd

from protzilla.data_preprocessing.plots import create_box_plots, create_histograms
from protzilla.utilities import default_intensity_column


def by_log(protein_df: pd.DataFrame, peptide_df: pd.DataFrame | None, log_base="log10") -> dict:
    """
    This function log-transforms intensity
    DataFrames. Supports log-transformation to the base
    of 2 or 10.

    :param protein_df: a protein data frame in long format
    :type protein_df: pd.DataFrame
    :param peptide_df: a peptide data frame, that is to be transformed the same way as the protein data frame
    :param log_base: String of the used log method "log10" (base 10)
        or "log2" (base 2). Default: "log10"
    :type log_base: str

    :return: returns a pandas DataFrame in typical protzilla
        long format with the transformed data and an empty dict.
    :rtype: Tuple[pandas DataFrame, dict]
    """
    msg = []
    intensity_name = default_intensity_column(protein_df)
    transformed_df = protein_df.copy()
    transformed_peptide_df = peptide_df.copy() if peptide_df is not None else None
    zero_intensity_index = transformed_df[transformed_df[intensity_name] <= 0].index
    untransformable_data_df = transformed_df.loc[zero_intensity_index]
    transformed_df.drop(zero_intensity_index, inplace=True)
    transformed_df.reset_index(drop=True, inplace=True)

    if transformed_peptide_df is not None:
        zero_intensity_peptide_index = transformed_peptide_df[transformed_peptide_df["Intensity"] <= 0].index
        untransformable_peptide_data_df = transformed_peptide_df.loc[zero_intensity_peptide_index]
        transformed_peptide_df.drop(zero_intensity_peptide_index, inplace=True)
        transformed_peptide_df.reset_index(drop=True, inplace=True)
        if not untransformable_peptide_data_df.empty:
            msg.append(dict(
                msg=f"Warning: {len(untransformable_peptide_data_df)} data points of peptide data with zero or negative intensity values were found and will be dropped. "
                f"Please adapt your preprocessing pipeline if this is unexpected.",
                level=logging.WARNING
            )
        )


    if not untransformable_data_df.empty:
        msg.append(dict(
            msg=f"Warning: {len(untransformable_data_df)} data points of {len(untransformable_data_df['Protein ID'])} distinct protein groups with zero or negative intensity values were found and will be dropped. "
            f"Please adapt your preprocessing pipeline if this is unexpected.",
            level=logging.WARNING
            )
        )

    if log_base == "log2":
        transformed_df[intensity_name] = np.log2(transformed_df[intensity_name])
        if transformed_peptide_df is not None:
            transformed_peptide_df["Intensity"] = np.log2(
                transformed_peptide_df["Intensity"]
            )
    elif log_base == "log10":
        transformed_df[intensity_name] = np.log10(transformed_df[intensity_name])
        if transformed_peptide_df is not None:
            transformed_peptide_df["Intensity"] = np.log10(
                transformed_peptide_df["Intensity"]
            )
    else:
        raise ValueError("Unknown log_base. Known log methods are 'log2' and 'log10'.")
    return dict(protein_df=transformed_df, peptide_df=transformed_peptide_df, messages=msg)


def by_log_plot(method_inputs, method_outputs, graph_type, group_by):
    return _build_box_hist_plot(
        method_inputs["protein_df"], method_outputs["protein_df"], graph_type, group_by
    )


def _build_box_hist_plot(df, result_df, graph_type, group_by):
    if graph_type == "Boxplot":
        fig = create_box_plots(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Transformation",
            name_b="After Transformation",
            heading="Distribution of Protein Intensities",
            group_by=group_by,
            y_title="Intensity",
        )
    if graph_type == "Histogram":
        fig = create_histograms(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Transformation",
            name_b="After Transformation",
            heading="Distribution of Protein Intensities",
            x_title="Protein Intensities",
            y_title="Frequency of Protein Intensities",
        )
    return [fig]
