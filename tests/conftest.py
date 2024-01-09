import base64
import io
import json
import logging
from pathlib import Path
from shutil import rmtree

import numpy as np
import pandas as pd
import pytest
from PIL import Image

from ..protzilla.constants.paths import PROJECT_PATH, RUNS_PATH
from ..protzilla.utilities import random_string


def pytest_addoption(parser):
    parser.addoption(
        "--show-figures",
        action="store",
        default=False,
        help="If 'True', tests will open figures using the default renderer",
    )


@pytest.fixture(scope="session")
def show_figures(request):
    return request.config.getoption("--show-figures")


@pytest.fixture(scope="session")
def workflow_meta():
    with open(f"{PROJECT_PATH}/protzilla/constants/workflow_meta.json", "r") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def tests_folder_name():
    return f"tests_{random_string()}"


@pytest.fixture(scope="session", autouse=True)
def run_test_folder(tests_folder_name):
    Path(f"{RUNS_PATH}/{tests_folder_name}").mkdir()
    yield
    rmtree(Path(f"{RUNS_PATH}/{tests_folder_name}"))


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
def example_workflow_short():
    with open(
        f"{PROJECT_PATH}/tests/test_workflows/example_workflow_short.json", "r"
    ) as f:
        return json.load(f)


@pytest.fixture
def example_workflow():
    with open(f"{PROJECT_PATH}/tests/test_workflows/example_workflow.json", "r") as f:
        return json.load(f)


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
