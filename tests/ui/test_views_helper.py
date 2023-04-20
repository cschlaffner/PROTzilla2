from unittest.mock import MagicMock, Mock

import pandas as pd
import pytest
from django.test.client import RequestFactory

from ui.runs.views_helper import (
    convert_str_if_possible,
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


