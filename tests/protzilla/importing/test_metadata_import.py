import logging
from shutil import rmtree

import pandas as pd

from protzilla.constants.paths import PROJECT_PATH, RUNS_PATH
from protzilla.importing import metadata_import
from protzilla.methods.importing import MetadataColumnAssignment
from protzilla.run import Run
from protzilla.utilities import random_string


def test_metadata_import():
    name = "test_run" + random_string()
    run = Run(name, "only_import")
    run.step_remove(section="importing", step_index=0)
    run.step_calculate({
        "file_path": f"{PROJECT_PATH}/tests/metadata_cut_columns.csv",
        "feature_orientation": "Columns (samples in rows, features in columns)",
    })
    test_metadata = pd.read_csv(f"{PROJECT_PATH}/tests/metadata_cut_columns.csv")
    pd.testing.assert_frame_equal(test_metadata, run.current_outputs["metadata_df"])
    rmtree(RUNS_PATH / name)


def test_metadata_import_diann():
    name = "test_run" + random_string()
    run = Run(name, "only_import")
    run.step_remove(section="importing", step_index=0)
    run.step_calculate(
        metadata_import.metadata_import_method_diann,
        file_path=f"{PROJECT_PATH}/tests/diann_run_relationship_metadata.xlsx",
    )
    test_metadata = pd.read_excel(
        f"{PROJECT_PATH}/tests/diann_run_relationship_metadata.xlsx"
    )
    pd.testing.assert_frame_equal(test_metadata, run.current_outputs["metadata_df"])
    rmtree(RUNS_PATH / name)


def test_metadata_orientation():
    name1 = "test_run" + random_string()
    name2 = "test_run" + random_string()
    run1 = Run(name1, "only_import")
    run2 = Run(name2, "only_import")
    run1.step_remove(section="importing", step_index=0)
    run2.step_remove(section="importing", step_index=0)
    run1.step_calculate({
        "file_path": f"{PROJECT_PATH}/tests/metadata_cut_columns.csv",
        "feature_orientation": "Columns (samples in rows, features in columns)",
    })
    run2.step_calculate({
        "file_path": f"{PROJECT_PATH}/tests/metadata_cut_rows.csv",
        "feature_orientation": "Rows (features in rows, samples in columns)",
    })
    pd.testing.assert_frame_equal(run1.current_outputs["metadata_df"], run2.current_outputs["metadata_df"])
    rmtree(RUNS_PATH / name1)
    rmtree(RUNS_PATH / name2)


def test_metadata_column_assignment():
    name = "test_run" + random_string()
    run = Run(name, "only_import")
    run.step_remove(section="importing", step_index=0)
    run.step_add(MetadataColumnAssignment())
    run.step_calculate({
        "file_path": f"{PROJECT_PATH}/tests/metadata_cut_columns.csv",
        "feature_orientation": "Columns (samples in rows, features in columns)",
    })
    run.step_next()

    run.step_calculate({
        "metadata_required_column": "Sample_renamed",
        "metadata_unknown_column": "Sample",
    })
    assert run.current_outputs["metadata_df"].columns[0] == "Sample_renamed"

    run.step_calculate({
        "metadata_required_column": "Sample",
        "metadata_unknown_column": "Sample_renamed",
    })
    assert run.current_outputs["metadata_df"].columns[0] == "Sample"

    run.step_calculate({
        "metadata_required_column": "Group",
        "metadata_unknown_column": "Sample",
    })
    assert any(message["level"] == logging.ERROR for message in run.current_messages.messages)

    run.step_calculate({
        "metadata_required_column": "",
        "metadata_unknown_column": "",
    })

    rmtree(RUNS_PATH / name)
