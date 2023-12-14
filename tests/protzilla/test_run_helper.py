import copy
from unittest.mock import MagicMock, Mock

import pandas as pd
import pytest

from protzilla.run_helper import get_parameters, insert_special_params


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


def test_get_parameters():
    run = Mock()
    run.workflow_meta = {
        "section1": {
            "step1": {
                "method1": {
                    "parameters": {
                        "param1": {"default": "default1", "type": ""},
                        "param2": {"default": "default2", "type": ""},
                        "param3": {"default": "default3", "type": ""},
                    }
                }
            }
        }
    }
    run.current_parameters = {"method1": {"param1": "current1"}}
    run.workflow_config = {
        "sections": {
            "section1": {
                "steps": [
                    {
                        "name": "step1",
                        "method": "method1",
                        "parameters": {"param1": "config1", "param2": "config2"},
                    }
                ]
            }
        }
    }
    run.step_index_in_current_section.return_value = 0
    expected = {
        "param1": {"default": "current1", "type": ""},
        "param2": {"default": "config2", "type": ""},
        "param3": {"default": "default3", "type": ""},
    }
    assert get_parameters(run, "section1", "step1", "method1") == expected


def test_get_parameters_no_side_effects(workflow_meta, example_workflow):
    run = Mock()
    run.workflow_meta = copy.deepcopy(workflow_meta)
    run.current_parameters = {"strategy": "median"}
    run.workflow_config = copy.deepcopy(example_workflow)
    run.step_index_in_current_section.return_value = 5
    get_parameters(
        run, "data_preprocessing", "imputation", "simple_imputation_per_protein"
    )
    assert run.current_parameters == {"strategy": "median"}
    assert run.workflow_config == example_workflow
    assert run.workflow_meta == workflow_meta


def test_insert_special_params_named_output():
    param_dict = {"name": "name", "type": "named_output", "default": "default"}
    expected = {
        "name": "name",
        "type": "named_output",
        "default": "default",
        "steps": ["step1", "step2"],
        "outputs": ["mock_output_name"],
    }

    run = Mock()
    run.history = Mock()
    run.history.output_keys_of_named_step = MagicMock(return_value=["mock_output_name"])
    run.history.step_names = ["step2", "step1"]

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
