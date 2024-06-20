import base64
import io
import logging
import time
import uuid
from pathlib import Path
from shutil import rmtree

import numpy as np
import pandas as pd
import pytest
from PIL import Image

from protzilla.methods.importing import MaxQuantImport
from protzilla.run import Run

from ..protzilla.constants.paths import RUNS_PATH, TEST_DATA_PATH
from ..protzilla.utilities import random_string


def pytest_addoption(parser):
    parser.addoption(
        "--show-figures",
        action="store",
        default=False,
        help="If 'True', tests will open figures using the default renderer",
    )


@pytest.fixture(scope="function")
def run_name_and_cleanup():
    # Generate a unique run name
    run_name = f"test_run_{uuid.uuid4()}"
    run_path = Path(RUNS_PATH) / run_name

    # Yield the run name to the test or fixture that uses this fixture
    yield run_name

    # After the test or fixture that uses this fixture is done, remove the directory
    while run_path.exists():
        time.sleep(1)
        rmtree(run_path)


@pytest.fixture
def maxquant_data_file():
    return str((Path(TEST_DATA_PATH) / "data_import" / "maxquant_small.tsv").absolute())


@pytest.fixture(scope="function")
def run_standard(run_name_and_cleanup):
    run_name = run_name_and_cleanup
    yield Run(run_name=run_name, workflow_name="standard", df_mode="memory")


@pytest.fixture(scope="function")
def run_empty(run_name_and_cleanup):
    run_name = run_name_and_cleanup
    yield Run(run_name=run_name, workflow_name="test-run-empty", df_mode="memory")


@pytest.fixture(scope="function")
def run_imported(run_name_and_cleanup, maxquant_data_file):
    run_name = run_name_and_cleanup
    run = Run(run_name=run_name, workflow_name="test-run-empty", df_mode="memory")
    run.step_add(MaxQuantImport())
    run.step_calculate(
        {
            "file_path": str(maxquant_data_file),
            "intensity_name": "iBAQ",
            "map_to_uniprot": False,
        }
    )
    yield run


@pytest.fixture(scope="session")
def show_figures(request):
    return request.config.getoption("--show-figures")


@pytest.fixture(scope="session")
def tests_folder_name():
    name = f"tests_{random_string()}"
    yield name
    while Path(f"{RUNS_PATH}/{name}").exists():
        time.sleep(1)
        rmtree(Path(f"{RUNS_PATH}/{name}"))


@pytest.fixture
def critical_logger():
    from ..protzilla.constants.protzilla_logging import logger

    logger.setLevel(logging.CRITICAL)
    yield
    logger.setLevel(logging.INFO)


@pytest.fixture
def no_logging():
    from ..protzilla.constants.protzilla_logging import logger

    # highest used level is 50 -> 60 blocks everything
    logger.setLevel(60)
    yield
    logger.setLevel(logging.INFO)


@pytest.fixture
def error_logger():
    from ..protzilla.constants.protzilla_logging import logger

    logger.setLevel(logging.ERROR)
    yield
    logger.setLevel(logging.INFO)


@pytest.fixture(scope="function")
def debug_logger():
    from ..protzilla.constants.protzilla_logging import logger

    logger.setLevel(logging.DEBUG)
    yield
    logger.setLevel(logging.INFO)


@pytest.fixture
def df_with_nan():
    list_nan = (
        ["Sample1", "Protein1", "Gene1", 18],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample2", "Protein1", "Gene1", np.nan],
        ["Sample2", "Protein2", "Gene1", 18],
        ["Sample2", "Protein3", "Gene1", 2],
    )

    df_with_nan = pd.DataFrame(
        data=list_nan,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return df_with_nan


@pytest.fixture
def leftover_peptide_df():
    # sample, protein id, sequence, intensity, pep
    leftover_peptide_protein_list = (
        ["Sample01", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", np.NAN, 0.037779],
        ["Sample02", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", np.NAN, 0.037779],
        ["Sample03", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", 6923600.0, 0.037779],
        ["Sample04", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", np.NAN, 0.037779],
        ["Sample05", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", 37440000.0, 0.037779],
    )

    peptide_df = pd.DataFrame(
        data=leftover_peptide_protein_list,
        columns=["Sample", "Protein ID", "Sequence", "Intensity", "PEP"],
    )
    peptide_df.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)
    return peptide_df


@pytest.fixture
def filtered_peptides_list():
    return ["AAQSTAMNR"]


@pytest.fixture
def peptides_df():
    df = pd.DataFrame(
        (
            ["Sample1", "Protein1", "SEQA", 1000000, 0.00001],
            ["Sample1", "Protein2", "SEQB", 2000000, 0.00002],
            ["Sample1", "Protein2", "SEQC", 3000000, 0.00003],
            ["Sample1", "Protein2", "SEQD", 4000000, 0.00004],
            ["Sample1", "Protein3", "SEQE", 5000000, 0.00005],
            ["Sample1", "Protein3", "SEQF", 6000000, 0.00006],
            ["Sample1", "Protein3", "SEQG", 7000000, 0.00007],
            ["Sample1", "Protein4", "SEQH", 8000000, 0.00008],
            ["Sample1", "Protein5", "SEQI", 9000000, 0.00009],
            ["Sample2", "Protein1", "SEQJ", 10000000, 0.0001],
            ["Sample2", "Protein2", "SEQK", 11000000, 0.00011],
            ["Sample2", "Protein3", "SEQL", 12000000, 0.00012],
            ["Sample2", "Protein4", "SEQM", 13000000, 0.00013],
            ["Sample2", "Protein5", "SEQN", 14000000, 0.00014],
            ["Sample3", "Protein1", "SEQO", 15000000, 0.00015],
            ["Sample3", "Protein2", "SEQP", 16000000, 0.00016],
            ["Sample3", "Protein3", "SEQQ", 17000000, 0.00017],
            ["Sample3", "Protein4", "SEQR", 18000000, 0.00018],
            ["Sample3", "Protein5", "SEQS", 19000000, 0.00019],
            ["Sample4", "Protein1", "SEQT", 20000000, 0.0002],
            ["Sample4", "Protein2", "SEQU", 21000000, 0.00021],
            ["Sample4", "Protein3", "SEQV", 22000000, 0.00022],
            ["Sample4", "Protein4", "SEQW", 23000000, 0.00023],
        ),
        columns=["Sample", "Protein ID", "Sequence", "Intensity", "PEP"],
    )

    return df


class Helpers:
    @staticmethod
    def open_graph_from_base64(encoded_string):
        decoded_bytes = base64.b64decode(encoded_string)
        image_stream = io.BytesIO(decoded_bytes)
        image = Image.open(image_stream)
        image.show()


@pytest.fixture
def helpers():
    return Helpers
