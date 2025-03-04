import logging
from functools import partial
from multiprocessing import Pool, cpu_count
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

from protzilla.constants.colors import PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE
from protzilla.constants.ms_constants import DataKeys, FragmentationType
from protzilla.data_analysis.spectrum_prediction.spectrum import (
    SpectrumExporter,
    SpectrumPredictorFactory,
)
from protzilla.data_analysis.spectrum_prediction.spectrum_prediction_utils import (
    GenericTextSeparator,
    OutputFormats,
    PredictionModels,
)


def predict(
    model_name: PredictionModels,
    peptide_df: pd.DataFrame,
    output_format: OutputFormats,
    collision_energy: Optional[float],
    fragmentation_type: Optional[FragmentationType],
    column_seperator: Optional[GenericTextSeparator],
    output_dir: Optional[str] = None,
    file_name: Optional[str] = "predicted_spectra",
):
    """
    Predicts the spectra for the given peptides using the specified model.
    :param model_name: the model to use
    :param peptide_df: the result of the evidence import, containing the peptide sequences, charges and m/z values
    :param output_format: output format of the spectral predictions
    :param collision_energy: the collision energy for which to predict the spectra
    :param fragmentation_type: the type of ms fragmentation for which to predict the spectra
    :param column_seperator: the column separator to use in case the output format is generic text
    :param output_dir: the directory to save the output to, this will just be shown to the user in the return message so he knows where to find the output
    :return: a dictionary containing the output file, metadata and peaks dataframes of the predicted spectra and a message
    """
    if file_name is None or file_name == "":
        raise ValueError("The file name must not be empty.")
    peptide_df = peptide_df.rename(
        columns={
            "Sequence": DataKeys.PEPTIDE_SEQUENCE,
            "Charge": DataKeys.PRECURSOR_CHARGE,
            "m/z": DataKeys.PRECURSOR_MZ,
        },
        errors="ignore",  # as the evidence import already renames some columns to the DataKeys, this is necessary
    )
    prediction_df = (
        peptide_df[
            [
                DataKeys.PEPTIDE_SEQUENCE,
                DataKeys.PRECURSOR_CHARGE,
                DataKeys.PRECURSOR_MZ,
            ]
        ]
        .drop_duplicates()
        .copy()
    )
    predictor = SpectrumPredictorFactory.create_predictor(model_name)
    if DataKeys.COLLISION_ENERGY in predictor.required_keys:
        assert collision_energy is not None, "Collision energy is required."
        prediction_df[DataKeys.COLLISION_ENERGY] = collision_energy
    if DataKeys.FRAGMENTATION_TYPE in predictor.required_keys:
        assert fragmentation_type is not None, "Fragmentation type is required."
        prediction_df[DataKeys.FRAGMENTATION_TYPE] = fragmentation_type
    predictor.load_prediction_df(prediction_df)
    predicted_spectra = predictor.predict()
    if output_format == OutputFormats.CSV_TSV:
        output = SpectrumExporter.export_to_generic_text(
            predicted_spectra, file_name, column_seperator
        )
    elif output_format == OutputFormats.MSP:
        output = SpectrumExporter.export_to_msp(predicted_spectra, file_name)
    elif output_format == OutputFormats.MGF:
        output = SpectrumExporter.export_to_mgf(predicted_spectra, file_name)

    metadata_dfs = []
    peaks_dfs = []
    for spectrum in predicted_spectra:
        metadata_df, peaks_df = spectrum.to_mergeable_df()
        metadata_dfs.append(metadata_df)
        peaks_dfs.append(peaks_df)

    combined_metadata_df = pd.concat(metadata_dfs)
    combined_peaks_df = pd.concat(peaks_dfs)

    return {
        "predicted_spectra": output,
        "predicted_spectra_metadata": combined_metadata_df,
        "predicted_spectra_peaks": combined_peaks_df,
        "messages": [
            {
                "level": logging.INFO,
                "msg": f"Successfully predicted {len(predicted_spectra)} spectra.\nThe output can be found at {output_dir / output.filename if output_dir else 'the dataframe folder of the run'}",
            }
        ],
    }


def plot_spectrum(
    metadata_df: pd.DataFrame,
    peaks_df: pd.DataFrame,
    peptide_sequences: str,
    precursor_charges: int,
    annotation_threshold: float,
):
    """
    Plots the spectrum for the given peptide and charge.
    The metadata and peaks dataframes can be joined via the index, a unique identifier for each spectrum.
    :param metadata_df: the dataframe containing the metadata of the spectra, like sequence, charge, etc.
    :param peaks_df: the dataframe containing the peaks of the spectra
    :param peptide_sequences: the peptide sequence for which to plot the spectrum
    :param precursor_charges: the charge of the precursor ion for which to plot the spectrum
    :param annotation_threshold: the threshold for the intensity of the peaks to be annotated
    :return: a dictionary containing the plot and a message
    """
    assert 0 <= annotation_threshold and annotation_threshold <= 1

    # Get the unique_id for the specified peptide and charge
    unique_id = metadata_df[
        (metadata_df[DataKeys.PEPTIDE_SEQUENCE] == peptide_sequences)
        & (metadata_df[DataKeys.PRECURSOR_CHARGE] == precursor_charges)
    ].index

    assert (
        len(unique_id) == 1
    ), f"Expected exactly one unique_id, but got {len(unique_id)}: {unique_id}"

    # Filter the peaks_df for the specific spectrum
    spectrum = peaks_df.loc[unique_id]

    plot_df = spectrum[
        [
            DataKeys.MZ,
            DataKeys.INTENSITY,
            DataKeys.FRAGMENT_TYPE,
            DataKeys.FRAGMENT_CHARGE,
        ]
    ]
    plot_df["fragment_ion"] = plot_df[DataKeys.FRAGMENT_TYPE].str[0]

    ion_color = PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE
    ion_types = plot_df[DataKeys.FRAGMENT_TYPE].str[0].unique()
    if len(ion_types) != 2:
        raise ValueError(
            f"Expected exactly two fragment types, but got {len(ion_types)}: {ion_types}"
        )

    # Plotting the peaks
    fig = px.bar(
        plot_df,
        x=DataKeys.MZ,
        y=DataKeys.INTENSITY,
        hover_data=[DataKeys.FRAGMENT_TYPE, DataKeys.FRAGMENT_CHARGE],
        color="fragment_ion",
        color_discrete_map={ion_types[0]: ion_color[0], ion_types[1]: ion_color[1]},
        title=f"{peptide_sequences} ({precursor_charges}+)",
    )

    # Updating the layout
    fig.update_layout(
        yaxis=dict(
            title="Relative intensity",
            range=[0, 1.2],
            tickvals=[0, 0.5, 1],
            ticktext=["0.0", "0.5", "1.0"],
            ticks="outside",
            showline=True,
            linewidth=1,
            linecolor="grey",
        ),
        xaxis=dict(
            title="m/z",
            tickmode="linear",
            ticks="outside",
            tick0=0,
            ticklabelstep=2,
            tickangle=-45,
            dtick=50,
            showline=True,
            linewidth=1,
            linecolor="grey",
        ),
    )
    fig.update_traces(width=8.0)

    # Adding the annotations
    for _, row in plot_df.iterrows():
        if row[DataKeys.INTENSITY] < annotation_threshold:
            continue
        fig.add_annotation(
            x=row[DataKeys.MZ],
            y=row[DataKeys.INTENSITY],
            font=dict(
                color=ion_color[0]
                if ion_types[0] in row[DataKeys.FRAGMENT_TYPE]
                else ion_color[1]
            ),
            text=f"{row[DataKeys.FRAGMENT_TYPE]} ({row[DataKeys.FRAGMENT_CHARGE]}+)",
            showarrow=False,
            yshift=30,
            textangle=-90,
        )

    # Updating the color legend to say e.g. "y" and "b" instead of the color codes
    fig.for_each_trace(
        lambda trace: trace.update(
            name=trace.name.replace(ion_color[0], f"{ion_types[0]}-ion").replace(
                ion_color[1], f"{ion_color[1]}-ion"
            )
        )
    )
    # Replace title of legend with "Fragment type"
    fig.update_layout(legend_title_text="Fragment type")
    to_be_returned = dict(
        plots=[fig],
        messages=[
            {
                "level": logging.INFO,
                "msg": f"Successfully plotted the spectrum for {peptide_sequences} ({precursor_charges}+). Tip: You can zoom in by selecting an area on the plot.",
            }
        ],
    )
    to_be_returned[f"spectrum_{peptide_sequences}_{precursor_charges}"] = plot_df
    return to_be_returned


# leftover from an old bachelor thesis. might be interesting if the in the future, experimental spectra
# are compared with predicted spectra for validation
def advanced_cosine_similarity(
    experimental_peaks_df: pd.DataFrame,
    predicted_peaks_df: pd.DataFrame,
    mz_tolerance: float,
) -> float:
    """
    Calculate the cosine similarity between two spectra.
    :param experimental_peaks_df:
    :param predicted_peaks_df:
    :param mz_tolerance:
    :return:
    """
    original_experimental_peaks_df = experimental_peaks_df.copy()
    original_predicted_peaks_df = predicted_peaks_df.copy()
    original_experimental_peaks_df[DataKeys.INTENSITY] = (
        original_experimental_peaks_df[DataKeys.INTENSITY]
        / original_experimental_peaks_df[DataKeys.INTENSITY].max()
    )
    experimental_peaks_df[DataKeys.INTENSITY] = (
        experimental_peaks_df[DataKeys.INTENSITY]
        / experimental_peaks_df[DataKeys.INTENSITY].max()
    )
    matches = []
    unmatched_experimental_peaks = []
    unmatched_theoretical_peaks = []
    for mz_a, int_a in predicted_peaks_df[[DataKeys.MZ, DataKeys.INTENSITY]].values:
        candidates = experimental_peaks_df[
            (experimental_peaks_df[DataKeys.MZ] >= mz_a - mz_tolerance)
            & (experimental_peaks_df[DataKeys.MZ] <= mz_a + mz_tolerance)
        ]
        if candidates.empty:
            unmatched_theoretical_peaks.append((mz_a, int_a))
            continue

        index = candidates[DataKeys.INTENSITY].idxmax()
        mz_b, int_b = experimental_peaks_df.loc[
            index, [DataKeys.MZ, DataKeys.INTENSITY]
        ]
        experimental_peaks_df = experimental_peaks_df.drop(index)
        matches.append(((mz_a, int_a), (mz_b, int_b)))

    for mz_b, int_b in experimental_peaks_df[[DataKeys.MZ, DataKeys.INTENSITY]].values:
        unmatched_experimental_peaks.append((mz_b, int_b))
    if not matches:
        return 0.0
    # Calculate the cosine similarity
    squared_sum_exp_intensities = sum(
        [
            intensity**2
            for mz, intensity in original_experimental_peaks_df[
                [DataKeys.MZ, DataKeys.INTENSITY]
            ].values
        ]
    )
    squared_sum_pred_intensities = sum(
        [
            intensity**2
            for mz, intensity in original_predicted_peaks_df[
                [DataKeys.MZ, DataKeys.INTENSITY]
            ].values
        ]
    )
    squared_sum_unmatched_exp_intensities = sum(
        [intensity**2 for mz, intensity in unmatched_experimental_peaks]
    )
    squared_sum_unmatched_pred_intensities = sum(
        [intensity**2 for mz, intensity in unmatched_theoretical_peaks]
    )
    numerator_a = sum([int_a * int_b for (mz_a, int_a), (mz_b, int_b) in matches])
    demoninator_a = (squared_sum_exp_intensities**0.5) * (
        squared_sum_pred_intensities**0.5
    )
    term_a = numerator_a / demoninator_a

    numerator_b = (
        squared_sum_unmatched_exp_intensities * squared_sum_unmatched_pred_intensities
    )
    denominator_b = squared_sum_exp_intensities * squared_sum_pred_intensities
    term_b = numerator_b / denominator_b
    similarity = term_a - term_b
    if similarity > 1 or similarity < -1:
        raise ValueError(f"Invalid cosine similarity: {similarity}")
    return similarity

