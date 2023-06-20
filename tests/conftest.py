import base64
import io
import json
from pathlib import Path
from shutil import rmtree
from PIL import Image

import numpy as np
import pandas as pd
import pytest
import requests

from ..protzilla.constants.paths import PROJECT_PATH, RUNS_PATH
from ..protzilla.utilities import random_string


def check_internet_connection():
    try:
        response = requests.get("https://www.google.com", stream=True)
        return True
    except requests.exceptions.RequestException:
        return False


def pytest_configure(config):
    internet_available = check_internet_connection()
    config.addinivalue_line(
        "markers",
        f"internet(required: bool = True): Mark test as dependent on an internet connection (internet_available={internet_available})",
    )


def pytest_collection_modifyitems(config, items):
    for item in items:
        internet_marker = item.get_closest_marker("internet")
        internet_connection = check_internet_connection()
        if internet_marker and not internet_connection:
            item.add_marker(
                pytest.mark.skip(reason="Internet connection not available")
            )


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
