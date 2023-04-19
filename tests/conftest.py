import json

import pytest

from protzilla.constants.paths import PROJECT_PATH


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
def example_workflow():
    with open(f"{PROJECT_PATH}/tests/test_workflows/example_workflow.json", "r") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def workflow_meta():
    with open(f"{PROJECT_PATH}/protzilla/constants/workflow_meta.json", "r") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def example_workflow_short():
    with open(
        f"{PROJECT_PATH}/tests/test_workflows/example_workflow_short.json", "r"
    ) as f:
        return json.load(f)