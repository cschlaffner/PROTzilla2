import copy

import pandas as pd
import pytest
from django.test.client import RequestFactory

from protzilla.run_v2 import Run
from protzilla.steps import StepManager
from ui.runs.views_helper import (
    convert_str_if_possible,
    get_displayed_steps,
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
            "chosen_method": ["samples_missing_filter"],
            "percentage": ["0.5"],
        },
    )
    return post_request.POST


def test_parameters_from_post(mock_post):
    assert parameters_from_post(mock_post) == {
        "chosen_method": "samples_missing_filter",
        "percentage": 0.5,
    }


def test_convert_str_if_possible():
    assert convert_str_if_possible("1.0") == 1
    assert convert_str_if_possible("0.5") == 0.5
    assert convert_str_if_possible("test") == "test"
    assert isinstance(convert_str_if_possible("1.00"), int)


def test_get_displayed_steps_structure(
    run_standard: Run
):
    section_keys = {"finished", "id", "name", "possible_steps", "steps", "selected"}
    possible_steps_keys = {"id", "methods", "name"}
    possible_steps_keys_methods = {"id", "name", "description"}
    steps_keys = {
        "id",
        "name",
        "selected",
        "section",
        "index",
        "method_name",
        "name",
        "selected",
        "finished",
    }

    result = get_displayed_steps(run_standard.steps)

    assert all(set(section.keys()) == section_keys for section in result)
    assert set(result[0]["possible_steps"][0].keys()) == possible_steps_keys
    assert (
        set(result[0]["possible_steps"][0]["methods"][0].keys())
        == possible_steps_keys_methods
    )
    assert set(result[0]["steps"][0].keys()) == steps_keys
