from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from protzilla.constants.ms_constants import DataKeys, FragmentationType
from protzilla.constants.paths import PEPTIDE_TEST_DATA_PATH
from protzilla.data_analysis.spectrum_prediction.spectrum import (
    KoinaModel,
    Spectrum,
    SpectrumExporter,
)
from protzilla.data_analysis.spectrum_prediction.spectrum_prediction_utils import (
    CSV_COLUMNS,
    OutputFormats,
    OutputKeys,
    PredictionModelMetadata,
    PredictionModels,
)
from protzilla.methods.data_analysis import PredictSpectrum
from protzilla.methods.importing import EvidenceImport

evidence_small = Path(PEPTIDE_TEST_DATA_PATH) / "evidence_100.txt"


@pytest.fixture
def spectrum_prediction_run(run_imported):
    run = run_imported
    run.step_add(EvidenceImport())
    run.step_next()
    run.step_calculate(
        {
            "file_path": str(evidence_small),
            "intensity_name": "Intensity",
            "map_to_uniprot": False,
        }
    )
    assert (
        "peptide_df" in run.current_outputs
        and not run.current_outputs["peptide_df"].empty
    )
    run.step_add(PredictSpectrum())
    run.step_next()
    return run


@pytest.fixture
def prediction_df_complete():
    return pd.DataFrame(
        {
            DataKeys.PEPTIDE_SEQUENCE: ["PEPTIDE1", "PEPTIDE2"],
            DataKeys.PRECURSOR_CHARGE: [1, 2],
            DataKeys.COLLISION_ENERGY: [30, 30],
            DataKeys.PRECURSOR_MZ: [100, 200],
            DataKeys.FRAGMENTATION_TYPE: [
                FragmentationType.HCD,
                FragmentationType.HCD,
            ],
        }
    )


@pytest.fixture
def prediction_df_incomplete():
    return pd.DataFrame(
        {
            DataKeys.PEPTIDE_SEQUENCE: ["PEPTIDE1", "PEPTIDE2"],
            DataKeys.PRECURSOR_CHARGE: [1, 2],
            DataKeys.PRECURSOR_MZ: [100, 200],
        }
    )


@pytest.fixture
def prediction_df_large():
    return pd.DataFrame(
        {
            DataKeys.PEPTIDE_SEQUENCE: ["PEPTIDE" + str(i) for i in range(2000)],
            DataKeys.PRECURSOR_CHARGE: [1 for _ in range(2000)],
            DataKeys.PRECURSOR_MZ: [100 for _ in range(2000)],
            DataKeys.COLLISION_ENERGY: [30 for _ in range(2000)],
            DataKeys.FRAGMENTATION_TYPE: [FragmentationType.HCD for _ in range(2000)],
        }
    )


@pytest.fixture
def prediction_df_ptms():
    return pd.DataFrame(
        {
            DataKeys.PEPTIDE_SEQUENCE: ["PEPTIDE1", "PEPTI[DE2", "PEPTI(DE3"],
            DataKeys.PRECURSOR_CHARGE: [1, 2, 3],
            DataKeys.PRECURSOR_MZ: [100, 200, 300],
            DataKeys.COLLISION_ENERGY: [30, 30, 30],
            DataKeys.FRAGMENTATION_TYPE: [
                FragmentationType.HCD,
                FragmentationType.HCD,
                FragmentationType.HCD,
            ],
        }
    )


@pytest.fixture
def prediction_df_high_charge():
    return pd.DataFrame(
        {
            DataKeys.PEPTIDE_SEQUENCE: ["PEPTIDE1", "PEPTIDE2", "PEPTIDE3"],
            DataKeys.PRECURSOR_CHARGE: [1, 5, 6],
            DataKeys.PRECURSOR_MZ: [100, 200, 300],
            DataKeys.COLLISION_ENERGY: [30, 30, 30],
            DataKeys.FRAGMENTATION_TYPE: [
                FragmentationType.HCD,
                FragmentationType.HCD,
                FragmentationType.HCD,
            ],
        }
    )


@pytest.fixture
def spectrum_one():
    return Spectrum(
        "sequence1",
        1,
        1.0,
        [100, 200],
        [0.5, 0.7],
        {"Charge": 1, "Parent": 1.0},
        {DataKeys.FRAGMENT_TYPE: ["b1+1", "y1+2"]},
    )


@pytest.fixture
def spectrum_two():
    return Spectrum(
        "sequence2",
        2,
        2.0,
        [150, 250],
        [0.6, 0.8],
        {"Charge": 2, "Parent": 2.0},
        {DataKeys.FRAGMENT_TYPE: ["b1+1", "y1+2"]},
    )


@pytest.fixture
def spectrum_none_metadata():
    return Spectrum(
        "sequence1",
        None,
        None,
        [100, 200],
        [0.5, 0.7],
        {"Charge": None},
        {DataKeys.FRAGMENT_TYPE: ["b1+1", "y1+2"]},
    )


@pytest.fixture
def expected_csv_header():
    return ",".join(CSV_COLUMNS)


@pytest.fixture
def expected_tsv_header():
    return "\t".join(CSV_COLUMNS)


@pytest.mark.parametrize(
    "model_name",
    [
        PredictionModels.PROSITINTENSITYHCD,
        PredictionModels.PROSITINTENSITYCID,
        PredictionModels.PROSITINTENSITYTIMSTOF,
    ],
)
@pytest.mark.parametrize(
    "output_format",
    [
        OutputFormats.CSV_TSV,
        OutputFormats.MSP,
        OutputFormats.MGF,
    ],
)
@pytest.mark.parametrize("csv_separator", [",", ";", "\t"])
@pytest.mark.parametrize(
    "fragmentation_type", [FragmentationType.HCD, FragmentationType.CID]
)
def test_spectrum_prediction(
    spectrum_prediction_run,
    model_name,
    output_format,
    csv_separator,
    fragmentation_type,
):
    run = spectrum_prediction_run

    # Set up the parameters
    params = {
        "model_name": model_name,
        "output_format": output_format,
        "collision_energy": 30,
        "fragmentation_type": fragmentation_type,
        "column_seperator": csv_separator,
        "file_name": "predicted_spectra",
    }

    # Adjust parameters based on model requirements
    model_info = PredictionModelMetadata[model_name]
    required_keys = model_info["required_keys"]

    # Run the step calculation
    run.step_calculate(params)

    # Assert outputs
    assert "predicted_spectra_metadata" in run.current_outputs
    assert "predicted_spectra_peaks" in run.current_outputs

    metadata_df = run.current_outputs["predicted_spectra_metadata"]
    peaks_df = run.current_outputs["predicted_spectra_peaks"]

    # Check metadata DataFrame
    assert not metadata_df.empty
    for key in required_keys:
        assert key in metadata_df.columns
    assert DataKeys.PRECURSOR_MZ in metadata_df.columns

    # Check peaks DataFrame
    assert not peaks_df.empty
    assert DataKeys.MZ in peaks_df.columns
    assert DataKeys.INTENSITY in peaks_df.columns
    assert OutputKeys.FRAGMENT_TYPE in peaks_df.columns
    assert OutputKeys.FRAGMENT_CHARGE in peaks_df.columns

    # Check if the output file is generated
    assert "predicted_spectra" in run.current_outputs
    if output_format == OutputFormats.CSV_TSV:
        file_output = run.current_outputs["predicted_spectra"]
        assert file_output.file_extension in ["csv", "tsv"]
        if csv_separator == "\t":
            assert file_output.file_extension == "tsv"
        else:
            assert file_output.file_extension == "csv"

        # Check CSV/TSV content
        content = file_output.content
        assert content.startswith(csv_separator.join(CSV_COLUMNS))
        assert len(content.splitlines()) > 1  # At least header and one data row
    elif output_format == OutputFormats.MSP:
        file_output = run.current_outputs["predicted_spectra"]
        assert file_output.file_extension == "msp"

        # Check MSP content
        content = file_output.content
        assert "Name:" in content
        assert "Num Peaks:" in content
    elif output_format == OutputFormats.MGF:
        file_output = run.current_outputs["predicted_spectra"]
        assert file_output.file_extension == "mgf"

        # Check MGF content
        content = file_output.content
        assert "BEGIN IONS" in content
        assert "TITLE=" in content
        assert "PEPMASS=" in content
        assert "CHARGE=" in content
        assert "END IONS" in content

    # Check if any error messages were generated
    assert not any(msg["level"] == "ERROR" for msg in run.current_messages)

    # Check if the number of predicted spectra matches the number of input peptides
    num_input_peptides = len(metadata_df)
    num_predicted_spectra = len(set(peaks_df.index))
    assert num_input_peptides == num_predicted_spectra

    # Check if the fragmentation type is correctly applied (if applicable)
    if DataKeys.FRAGMENTATION_TYPE in metadata_df.columns:
        assert all(metadata_df[DataKeys.FRAGMENTATION_TYPE] == fragmentation_type)

    # Check if the collision energy is correctly applied (if applicable)
    if DataKeys.COLLISION_ENERGY in metadata_df.columns:
        assert all(metadata_df[DataKeys.COLLISION_ENERGY] == params["collision_energy"])

    # Check if the peaks are valid
    assert all(peaks_df[DataKeys.MZ] > 0)
    assert all(
        (peaks_df[DataKeys.INTENSITY] >= 0) & (peaks_df[DataKeys.INTENSITY] <= 1)
    )

    # Check if fragment types are valid
    valid_fragment_types = set(["a", "b", "c", "x", "y", "z"])  # Add more if needed

    assert set(peaks_df[OutputKeys.FRAGMENT_TYPE].str[0]).issubset(valid_fragment_types)

    # Check if fragment charges are valid
    assert all(peaks_df[OutputKeys.FRAGMENT_CHARGE].astype(int) > 0)


def test_preprocess_renames_columns_correctly(prediction_df_complete):
    model = KoinaModel(
        required_keys=[
            DataKeys.PEPTIDE_SEQUENCE,
            DataKeys.PRECURSOR_CHARGE,
            DataKeys.FRAGMENTATION_TYPE,
            DataKeys.COLLISION_ENERGY,
        ],
        url="",
    )
    model.prediction_df = prediction_df_complete
    model.preprocess()
    assert set(model.prediction_df.columns) == set(
        model.required_keys + [DataKeys.PRECURSOR_MZ]
    )


def test_preprocess_removes_not_required_columns(prediction_df_complete):
    model = KoinaModel(
        required_keys=[
            DataKeys.PEPTIDE_SEQUENCE,
            DataKeys.PRECURSOR_CHARGE,
            DataKeys.FRAGMENTATION_TYPE,
            DataKeys.COLLISION_ENERGY,
        ],
        url="",
    )
    prediction_df_complete["ExtraColumn"] = 42
    model.prediction_df = prediction_df_complete
    model.preprocess()
    assert "ExtraColumn" not in model.prediction_df.columns


def test_preprocess_filters_out_high_charge_peptides(prediction_df_high_charge):
    model = KoinaModel(
        required_keys=[
            DataKeys.PEPTIDE_SEQUENCE,
            DataKeys.PRECURSOR_CHARGE,
            DataKeys.FRAGMENTATION_TYPE,
            DataKeys.COLLISION_ENERGY,
        ],
        url="",
    )
    model.prediction_df = prediction_df_high_charge
    model.preprocess()
    assert len(model.prediction_df) == 2


def test_preprocess_filters_out_peptides_with_ptms(prediction_df_ptms):
    model = KoinaModel(
        required_keys=[
            DataKeys.PEPTIDE_SEQUENCE,
            DataKeys.PRECURSOR_CHARGE,
            DataKeys.FRAGMENTATION_TYPE,
            DataKeys.COLLISION_ENERGY,
        ],
        url="",
    )
    model.prediction_df = prediction_df_ptms
    model.preprocess()
    assert len(model.prediction_df) == 1


def test_dataframe_verification_passes_with_required_keys(prediction_df_complete):
    model = KoinaModel(
        required_keys=[DataKeys.PEPTIDE_SEQUENCE, DataKeys.PRECURSOR_CHARGE], url=""
    )
    model.prediction_df = prediction_df_complete
    model.preprocess()
    model.verify_dataframe(prediction_df_complete)


def test_dataframe_verification_raises_error_when_key_missing(prediction_df_complete):
    model = KoinaModel(
        required_keys=[
            DataKeys.PEPTIDE_SEQUENCE,
            DataKeys.PRECURSOR_CHARGE,
            "MissingKey",
        ],
        url="",
    )
    with pytest.raises(ValueError):
        model.verify_dataframe(prediction_df_complete)


def test_slice_dataframe_returns_correct_slices(prediction_df_incomplete):
    model = KoinaModel(
        required_keys=[DataKeys.PEPTIDE_SEQUENCE, DataKeys.PRECURSOR_CHARGE], url=""
    )
    model.load_prediction_df(prediction_df_incomplete)
    slices = model.slice_dataframe()
    assert len(slices) == 1


def test_slice_dataframe_returns_correct_slices_for_large_dataframe(
    prediction_df_large,
):
    model = KoinaModel(
        required_keys=[DataKeys.PEPTIDE_SEQUENCE, DataKeys.PRECURSOR_CHARGE], url=""
    )
    model.load_prediction_df(prediction_df_large)
    slices = model.slice_dataframe()
    assert len(slices) == 2
    slices_small = model.slice_dataframe(200)
    assert len(slices_small) == 10


def test_format_dataframes_returns_correct_output(prediction_df_complete):
    model = KoinaModel(
        required_keys=[DataKeys.PEPTIDE_SEQUENCE, DataKeys.PRECURSOR_CHARGE], url=""
    )
    model.load_prediction_df(prediction_df_complete)
    slices = model.slice_dataframe()
    formatted_data = model.format_dataframes(slices)
    assert len(formatted_data) == len(slices)


def test_format_for_request(prediction_df_complete):
    model = KoinaModel(
        required_keys=[DataKeys.PEPTIDE_SEQUENCE, DataKeys.PRECURSOR_CHARGE], url=""
    )
    formatted_data = model.format_for_request(prediction_df_complete)
    assert formatted_data is not None
    assert "id" in formatted_data
    assert "inputs" in formatted_data
    for key in model.required_keys:
        assert any(
            key == input_data["name"] for input_data in formatted_data["inputs"]
        ), f"Key {key} not found in formatted request"


def test_load_prediction_df():
    model = KoinaModel(
        required_keys=[DataKeys.PEPTIDE_SEQUENCE, DataKeys.PRECURSOR_CHARGE], url=""
    )
    df = pd.DataFrame(
        {
            DataKeys.PRECURSOR_MZ: [100, 200],
            DataKeys.PEPTIDE_SEQUENCE: ["PEPTIDE1", "PEPTIDE2"],
            DataKeys.PRECURSOR_CHARGE: [1, 2],
        }
    )
    model.load_prediction_df(df)
    assert model.prediction_df is not None


def test_extract_fragment_information_handles_valid_annotations():
    fragment_annotations = np.array(["b1+1", "y1+2", "b2+1", "y2+2"])
    fragment_charges, fragment_types = KoinaModel.extract_fragment_information(
        fragment_annotations
    )
    expected_charges, expected_types = np.array(["1", "2", "1", "2"]), np.array(
        ["b1", "y1", "b2", "y2"]
    )
    np.testing.assert_array_equal(fragment_charges, expected_charges)
    np.testing.assert_array_equal(fragment_types, expected_types)


def test_extract_fragment_information_handles_invalid_annotations():
    fragment_annotations = np.array(["invalid1", "invalid2", "invalid3", "invalid4"])
    fragment_charges, fragment_types = KoinaModel.extract_fragment_information(
        fragment_annotations
    )
    expected_charges, expected_types = np.array(["", "", "", ""]), np.array(
        ["", "", "", ""]
    )
    np.testing.assert_array_equal(fragment_charges, expected_charges)
    np.testing.assert_array_equal(fragment_types, expected_types)


def test_extract_fragment_information_handles_mixed_annotations():
    fragment_annotations = np.array(["b1+1", "invalid1", "b2+1", "y2+2"])
    fragment_charges, fragment_types = KoinaModel.extract_fragment_information(
        fragment_annotations
    )
    expected_charges, expected_types = np.array(["1", "", "1", "2"]), np.array(
        ["b1", "", "b2", "y2"]
    )
    np.testing.assert_array_equal(fragment_charges, expected_charges)
    np.testing.assert_array_equal(fragment_types, expected_types)


def test_create_spectrum_with_valid_data():
    row = pd.Series(
        {DataKeys.PEPTIDE_SEQUENCE: "PEPTIDE", DataKeys.PRECURSOR_CHARGE: 2}
    )
    prepared_data = {
        OutputKeys.MZ_VALUES: np.array([[100, 200, 300]]),
        OutputKeys.INTENSITY_VALUES: np.array([[0.1, 0.2, 0.3]]),
        OutputKeys.FRAGMENT_TYPE: np.array([["b", "y", "b"]]),
        OutputKeys.FRAGMENT_CHARGE: np.array([[1, 2, 1]]),
    }
    index = 0

    spectrum = KoinaModel.create_spectrum(row, prepared_data, index)

    assert isinstance(spectrum, Spectrum)
    assert spectrum.peptide_sequence == "PEPTIDE"
    assert spectrum.precursor_charge == 2
    assert np.array_equal(
        spectrum.spectrum[DataKeys.MZ].values,
        prepared_data[OutputKeys.MZ_VALUES][index],
    )
    assert np.array_equal(
        spectrum.spectrum[DataKeys.INTENSITY].values,
        prepared_data[OutputKeys.INTENSITY_VALUES][index],
    )
    assert np.array_equal(
        spectrum.spectrum[OutputKeys.FRAGMENT_TYPE],
        prepared_data[OutputKeys.FRAGMENT_TYPE][index],
    )
    assert np.array_equal(
        spectrum.spectrum[OutputKeys.FRAGMENT_CHARGE],
        prepared_data[OutputKeys.FRAGMENT_CHARGE][index],
    )


def test_create_spectrum_with_missing_data():
    row = pd.Series(
        {
            DataKeys.PEPTIDE_SEQUENCE: "PEPTIDE",
        }
    )
    prepared_data = {
        OutputKeys.MZ_VALUES: np.array([100, 200, 300]),
        OutputKeys.INTENSITY_VALUES: np.array([0.1, 0.2, 0.3]),
    }
    index = 1

    with pytest.raises(ValueError):
        KoinaModel.create_spectrum(row, prepared_data, index)


def test_peak_annotation_with_valid_data():
    spectrum_df = pd.DataFrame(
        {
            DataKeys.MZ: [100, 200, 300],
            DataKeys.INTENSITY: [0.1, 0.2, 0.3],
            OutputKeys.FRAGMENT_TYPE: ["b", "y", "b"],
            OutputKeys.FRAGMENT_CHARGE: [1, 2, 1],
        }
    )
    result = SpectrumExporter._format_peaks_for_msp(spectrum_df)
    expected = ['100.0\t0.1\t"b^1"\n', '200.0\t0.2\t"y^2"\n', '300.0\t0.3\t"b^1"\n']
    assert result == expected


def test_peak_annotation_with_empty_data():
    spectrum_df = pd.DataFrame(
        {
            DataKeys.MZ: [],
            DataKeys.INTENSITY: [],
        }
    )
    result = SpectrumExporter._format_peaks_for_msp(spectrum_df)
    assert result == []


def test_peak_annotation_with_custom_prefix_suffix():
    spectrum_df = pd.DataFrame(
        {
            DataKeys.MZ: [100, 200, 300],
            DataKeys.INTENSITY: [0.1, 0.2, 0.3],
            OutputKeys.FRAGMENT_TYPE: ["b", "y", "b"],
            OutputKeys.FRAGMENT_CHARGE: [1, 2, 1],
        }
    )
    result = SpectrumExporter._format_peaks_for_msp(spectrum_df, prefix="(", suffix=")")
    expected = ["100.0\t0.1\t(b^1)\n", "200.0\t0.2\t(y^2)\n", "300.0\t0.3\t(b^1)\n"]
    assert result == expected


def test_export_to_msp_with_valid_spectra(spectrum_one, spectrum_two):
    spectra = [spectrum_one, spectrum_two]
    base_file_name = "test_file"
    result = SpectrumExporter.export_to_msp(spectra, base_file_name)
    assert "Name: sequence1" in result.content
    assert "Name: sequence2" in result.content
    assert "Charge=1" in result.content
    assert "Charge=2" in result.content
    assert "Parent=1.0" in result.content
    assert "Parent=2.0" in result.content


def test_export_to_msp_with_empty_spectra():
    spectra = []
    base_file_name = "test_file"
    result = SpectrumExporter.export_to_msp(spectra, base_file_name)
    assert result.content == ""


def test_export_to_msp_with_none_metadata(spectrum_none_metadata):
    spectra = [spectrum_none_metadata]
    base_file_name = "test_file"
    result = SpectrumExporter.export_to_msp(spectra, base_file_name)
    assert "Name: sequence1" in result.content
    assert "Charge=" not in result.content
    assert "Parent=" not in result.content


def test_export_to_csv_with_valid_spectra(
    spectrum_one, spectrum_two, expected_csv_header
):
    spectra = [spectrum_one, spectrum_two]
    base_file_name = "test_file"
    result = SpectrumExporter.export_to_generic_text(spectra, base_file_name)
    assert result.file_extension == "csv"
    assert result.base_file_name == base_file_name
    assert result.filename == "test_file.csv"
    assert expected_csv_header in result.content
    assert "sequence1,1.0,1,100,0.5,b,1" in result.content
    assert "sequence2,2.0,2,150,0.6,b,1" in result.content


def test_export_to_csv_with_empty_spectra(expected_csv_header):
    spectra = []
    base_file_name = "test_file"
    result = SpectrumExporter.export_to_generic_text(spectra, base_file_name)
    assert result.filename == "test_file.csv"
    assert expected_csv_header in result.content


def test_export_to_csv_with_invalid_separator(spectrum_one):
    spectra = [spectrum_one]
    base_file_name = "test_file"
    with pytest.raises(ValueError):
        SpectrumExporter.export_to_generic_text(spectra, base_file_name, seperator="*")


def test_export_to_csv_with_tab_separator(spectrum_one, expected_tsv_header):
    spectra = [spectrum_one]
    base_file_name = "test_file"
    result = SpectrumExporter.export_to_generic_text(
        spectra, base_file_name, seperator="\t"
    )
    assert result.file_extension == "tsv"
    assert expected_tsv_header in result.content
    assert "sequence1\t1.0\t1\t" in result.content


def test_export_to_mgf_with_valid_spectra(spectrum_one, spectrum_two):
    spectra = [spectrum_one, spectrum_two]
    base_file_name = "test_file"
    result = SpectrumExporter.export_to_mgf(spectra, base_file_name)
    assert "BEGIN IONS" in result.content
    assert "TITLE=sequence1" in result.content
    assert "TITLE=sequence2" in result.content
    assert "CHARGE=1+" in result.content
    assert "CHARGE=2+" in result.content
    assert "END IONS" in result.content


def test_export_to_mgf_with_empty_spectra():
    spectra = []
    base_file_name = "test_file"
    result = SpectrumExporter.export_to_mgf(spectra, base_file_name)
    assert result.content == ""


def test_export_to_mgf_with_none_metadata(spectrum_none_metadata):
    spectra = [spectrum_none_metadata]
    base_file_name = "test_file"
    with pytest.raises(ValueError):
        SpectrumExporter.export_to_mgf(spectra, base_file_name)
