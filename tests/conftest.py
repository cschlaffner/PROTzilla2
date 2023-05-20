import json
from pathlib import Path
from shutil import rmtree

import numpy as np
import pandas as pd
import pytest
import socket

from ..protzilla.constants.paths import PROJECT_PATH, RUNS_PATH
from ..protzilla.utilities.random import random_string


def check_internet_connection():
    try:
        with socket.create_connection(("www.google.com", 80)):
            return True
    except OSError:
        return False


def pytest_configure(config):
    internet_available = check_internet_connection()
    config.addinivalue_line(
        "markers", f"internet(required: bool = True): Mark test as dependent on an internet connection (internet_available={internet_available})"
    )


def pytest_collection_modifyitems(config, items):
    for item in items:
        internet_marker = item.get_closest_marker("internet")
        if internet_marker:
            internet_required = internet_marker.kwargs.get("required", True)
            if not internet_required or (internet_required and check_internet_connection()):
                continue
            item.add_marker(pytest.mark.skip(reason="Internet connection not available"))


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
