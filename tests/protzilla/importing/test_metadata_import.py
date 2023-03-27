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
        file=str(PROJECT_PATH / "tests/metadata_cut.csv"),
        feature_orientation="Columns (samples in rows, features in columns)",
    )
    test_metadata = pd.read_csv(str(PROJECT_PATH / "tests/metadata_cut.csv"))
    assert run.metadata.equals(test_metadata)
