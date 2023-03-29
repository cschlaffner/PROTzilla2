import copy
import json

import pytest

from protzilla import workflow_helper
from protzilla.constants.paths import PROJECT_PATH


@pytest.fixture
def example_workflow():
    with open(f"{PROJECT_PATH}/tests/example_workflow.json", "r") as f:
        return json.load(f)


@pytest.fixture
def workflow_meta():
    with open(f"{PROJECT_PATH}/protzilla/constants/workflow_meta.json", "r") as f:
        return json.load(f)


@pytest.fixture
def example_workflow_all_steps():
    return [
        "ms_data_import",
        "metadata_import",
        "filter_proteins",
        "filter_proteins",
        "filter_samples",
        "imputation",
        "filter_proteins",
        "filter_proteins",
        "outlier_detection",
        "transformation",
        "normalisation",
        "differential_expression",
        "differential_expression",
    ]


def test_get_all_steps(example_workflow, example_workflow_all_steps):
    assert workflow_helper.get_all_steps(example_workflow) == example_workflow_all_steps


def test_get_all_steps_no_side_effects(example_workflow, example_workflow_all_steps):
    example_workflow_copy = copy.deepcopy(example_workflow)
    workflow_helper.get_all_steps(example_workflow)
    assert example_workflow == example_workflow_copy


def test_get_all_default_params_for_methods(workflow_meta):
    result = workflow_helper.get_all_default_params_for_methods(
        workflow_meta, "data_preprocessing", "imputation", "knn"
    )
    expected = {"number_of_neighbours": 5}
    assert result == expected


def test_get_all_default_params_for_methods_no_side_effects(workflow_meta):
    workflow_meta_copy = copy.deepcopy(workflow_meta)
    workflow_helper.get_all_default_params_for_methods(
        workflow_meta, "data_preprocessing", "imputation", "knn"
    )
    assert workflow_meta_copy == workflow_meta
