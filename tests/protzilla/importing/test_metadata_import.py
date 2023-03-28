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
    print("test", test_metadata)
    print("run", run.metadata)
    assert run.metadata.equals(test_metadata)
    pd.testing.assert_frame_equal(test_metadata, run.metadata)


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
        # file=str(PROJECT_PATH / "tests/protzilla/importing/conversion_tmp_fxaCsBjMOAOASmmM.csv"),
        # feature_orientation="Columns (features in rows, samples in columns)",
    )
    print(run1.metadata.info())
    print(run2.metadata.info())

    print("\n\ncompare")
    print(run1.metadata.compare(run2.metadata))
    print("\n\n")

    print(
        pd.testing.assert_frame_equal(
            run1.metadata, run2.metadata, check_dtype=False, check_exact=False
        )
    )
    assert run1.metadata.equals(run2.metadata)
