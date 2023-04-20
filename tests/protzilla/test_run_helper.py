from unittest.mock import Mock, MagicMock

from protzilla.run_helper import get_parameters, insert_special_params


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
    run.current_parameters = {"param1": "current1"}
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
    expected = {
        "param1": {"default": "current1", "type": ""},
        "param2": {"default": "config2", "type": ""},
        "param3": {"default": "default3", "type": ""},
    }
    assert get_parameters(run, "section1", "step1", "method1") == expected


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
