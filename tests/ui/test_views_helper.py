import copy
from unittest.mock import MagicMock, Mock

import pandas as pd
import pytest
from django.test.client import RequestFactory

from ui.runs.views_helper import (
    convert_str_if_possible,
    get_displayed_steps,
    insert_special_params,
    parameters_from_post,
)


@pytest.fixture
def example_displayed_steps_importing_and_data_preprocessing():
    return [
        {
            "finished": True,
            "possible_steps": ["ms_data_import", "metadata_import"],
            "section": "importing",
            "steps": [{"name": "ms_data_import", "selected": False}],
        },
        {
            "finished": False,
            "possible_steps": [
                "filter_proteins",
                "filter_samples",
                "outlier_detection",
                "transformation",
                "normalisation",
                "imputation",
            ],
            "section": "data_preprocessing",
            "steps": [{"name": "filter_proteins", "selected": True}],
        },
    ]


@pytest.fixture
def mock_metadata_df():
    test_metadata_list = (
        ["Sample1", "Group1", "Batch1"],
        ["Sample2", "Group1", "Batch1"],
        ["Sample3", "Group1", "Batch2"],
        ["Sample4", "Group2", "Batch1"],
        ["Sample5", "Group2", "Batch2"],
        ["Sample6", "Group2", "Batch1"],
        ["Sample7", "Group3", "Batch2"],
    )

    return pd.DataFrame(
        data=test_metadata_list,
        columns=["Sample", "Group", "Batch"],
    )


@pytest.fixture
def mock_post():
    rf = RequestFactory()
    post_request = rf.post(
        "/calculate/",
        {
            "csrfmiddlewaretoken": ["test_token"],
            "chosen_method": ["low_frequency_filter"],
            "threshold": ["0.5"],
        },
    )
    return post_request.POST


def test_parameters_from_post(mock_post):
    assert parameters_from_post(mock_post) == {
        "chosen_method": "low_frequency_filter",
        "threshold": 0.5,
    }


def test_convert_str_if_possible():
    assert convert_str_if_possible("1.0") == 1
    assert convert_str_if_possible("0.5") == 0.5
    assert convert_str_if_possible("test") == "test"
    assert isinstance(convert_str_if_possible("1.00"), int)


def test_insert_special_params_named_output():
    param_dict = {"name": "name", "type": "named_output", "default": "default"}
    expected = {
        "name": "name",
        "type": "named_output",
        "default": "default",
        "steps": ["step1", "step2"],
        "outputs": "output_keys_of_named_step",
    }

    run = Mock()
    run.history = Mock()
    run.history.output_keys_of_named_step = MagicMock(
        return_value="output_keys_of_named_step"
    )
    run.history.step_names = ["step1", "step2"]

    insert_special_params(param_dict, run)
    assert param_dict == expected


def test_insert_special_params_fill_metadata_columns(mock_metadata_df):
    param_dict = {
        "name": "Group 2",
        "type": "categorical",
        "fill": "metadata_column_data",
        "categories": [],
        "default": None,
    }
    expected = {
        "name": "Group 2",
        "type": "categorical",
        "fill": "metadata_column_data",
        "categories": ["Group1", "Group2", "Group3"],
        "default": None,
    }

    run = Mock()
    run.metadata = mock_metadata_df
    insert_special_params(param_dict, run)
    param_dict["categories"] = list(param_dict["categories"])
    assert param_dict == expected


def test_get_displayed_steps_structure(
    workflow_meta,
    example_workflow_short,
):
    section_keys = ["finished", "id", "name", "possible_steps", "steps", "selected"]
    possible_steps_keys = ["id", "methods", "name"]
    possible_steps_keys_methods = ["id", "name", "description"]
    steps_keys = [
        "id",
        "name",
        "selected",
        "index",
        "method_name",
        "name",
        "selected",
        "finished",
    ]

    result = get_displayed_steps(example_workflow_short, workflow_meta, 1)

    assert all(section.keys() == set(section_keys) for section in result)
    assert result[0]["possible_steps"][0].keys() == set(possible_steps_keys)
    assert result[0]["possible_steps"][0]["methods"][0].keys() == set(
        possible_steps_keys_methods
    )
    assert result[0]["steps"][0].keys() == set(steps_keys)


def test_get_displayed_steps_no_side_effects(workflow_meta, example_workflow_short):
    example_workflow_copy = copy.deepcopy(example_workflow_short)
    workflow_meta_copy = copy.deepcopy(workflow_meta)
    get_displayed_steps(example_workflow_short, workflow_meta, 0)
    assert example_workflow_short == example_workflow_copy
    assert workflow_meta == workflow_meta_copy
