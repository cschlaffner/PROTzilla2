from pathlib import Path

import pytest

from protzilla.constants.paths import TEST_DATA_PATH
from protzilla.methods.data_analysis import PredictSpectra
from protzilla.methods.importing import EvidenceImport


@pytest.fixture
def spectrum_prediction_run(run_imported):
    run = run_imported
    run.step_add(EvidenceImport())
    run.step_next()
    # TODo magic path
    evidence_file = Path(TEST_DATA_PATH) / "data_import" / "evidence_small.txt"
    if not evidence_file.exists():
        raise FileNotFoundError(f"File {evidence_file} does not exist")
    run.step_calculate(
        {
            "file_path": str(evidence_file),
            "intensity_name": "Intensity",
            "map_to_uniprot": False,
        }
    )
    run.step_add(PredictSpectra())
    run.step_next()
    return run


def test_spectrum_prediction(spectrum_prediction_run):
    spectrum_prediction_run.step_calculate(
        {"model_name": "PrositIntensityHCD", "output_format": "msp"}
    )
    return
