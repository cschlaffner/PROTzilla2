import pandas as pd

from protzilla.constants.paths import PROJECT_PATH
from protzilla.importing import metadata_import
from protzilla.run import Run
from protzilla.utilities.random import random_string


def test_metadata_import():
    name = "test_run" + random_string()
    run = Run.create(name)
    run.calculate_and_next(
        metadata_import.metadata_import_method,
        file=str(PROJECT_PATH / "tests/metadata_cut_columns.csv"),
        feature_orientation="Columns (samples in rows, features in columns)",
    )
    test_metadata = pd.read_csv(str(PROJECT_PATH / "tests/metadata_cut_columns.csv"))
    assert run.metadata.equals(test_metadata)


def test_metadata_orientation():
    name1 = "test_run" + random_string()
    name2 = "test_run" + random_string()
    run1 = Run.create(name1)
    run2 = Run.create(name2)
    run1.calculate_and_next(
        metadata_import.metadata_import_method,
        file=str(PROJECT_PATH / "tests/metadata_cut_columns.csv"),
        feature_orientation="Columns (samples in rows, features in columns)",
    )
    run2.calculate_and_next(
        metadata_import.metadata_import_method,
        file=str(PROJECT_PATH / "tests/metadata_cut_rows.csv"),
        feature_orientation="Rows (features in rows, samples in columns)",
    )
    print(run1.metadata)
    print(run2.metadata)

    assert run1.metadata.equals(run2.metadata)
