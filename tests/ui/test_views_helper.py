from unittest.mock import MagicMock, Mock

import pandas as pd
import pytest
from django.test.client import RequestFactory

from ui.runs.views_helper import (
    convert_str_if_possible,
    insert_special_params,
    parameters_from_post,
)


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
