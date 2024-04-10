import copy
import json

import pytest

from protzilla import workflow
from protzilla.constants.paths import PROJECT_PATH
from protzilla.workflow import (
    get_workflow_default_param_value,
    validate_workflow_graphs,
    validate_workflow_parameters,
)


@pytest.fixture
def workflow_wrong_graphs():
    with open(f"{PROJECT_PATH}/tests/test_workflows/wrong_graphs.json", "r") as f:
        return json.load(f)


@pytest.fixture
def workflow_wrong_parameters():
    with open(f"{PROJECT_PATH}/tests/test_workflows/wrong_parameters.json", "r") as f:
        return json.load(f)


@pytest.fixture
def example_workflow_all_steps() -> list[dict[str, str | list[dict[str, str]]]]:
    return [
        {
            "section": "importing",
            "steps": [
                {"method": "max_quant_import", "name": "ms_data_import"},
                {"method": "metadata_import_method", "name": "metadata_import"},
            ],
        },
        {
            "section": "data_preprocessing",
            "steps": [
                {"method": "samples_missing_filter", "name": "filter_proteins"},
                {"method": "protein_intensity_sum_filter", "name": "filter_samples"},
                {"method": "knn", "name": "imputation"},
                {"method": "local_outlier_factor", "name": "outlier_detection"},
                {"method": "log_transformation", "name": "transformation"},
                {"method": "median", "name": "normalisation"},
            ],
        },
        {
            "section": "data_analysis",
            "steps": [
                {"method": "anova", "name": "differential_expression"},
                {"method": "t_test", "name": "differential_expression"},
            ],
        },
        {"section": "data_integration", "steps": []},
    ]


def test_get_steps_of_workflow(example_workflow, example_workflow_all_steps):
    assert (
        workflow.get_steps_of_workflow(example_workflow) == example_workflow_all_steps
    )


def test_get_steps_of_workflow_no_side_effects(example_workflow):
    example_workflow_copy = copy.deepcopy(example_workflow)
    workflow.get_steps_of_workflow(example_workflow)
    assert example_workflow == example_workflow_copy


def test_get_steps_amount_of_workflow(example_workflow):
    assert workflow.get_steps_amount_of_workflow(example_workflow) == 10


def test_get_defaults():
    method_params = {
        "test1": {"default": 1},
        "test2": {"something": 2},
    }
    expected = {"test1": 1, "test2": {"something": 2}}
    result = workflow.get_defaults(method_params)
    assert result == expected


def test_get_all_default_params_for_methods(workflow_meta):
    result = workflow.get_all_default_params_for_methods(
        workflow_meta, "data_preprocessing", "imputation", "knn"
    )
    expected = {"number_of_neighbours": 5}
    assert result == expected


def test_get_all_default_params_for_methods_no_side_effects(workflow_meta):
    workflow_meta_copy = copy.deepcopy(workflow_meta)
    workflow.get_all_default_params_for_methods(
        workflow_meta, "data_preprocessing", "imputation", "knn"
    )
    assert workflow_meta_copy == workflow_meta


def test_get_parameter_type(workflow_meta):
    assert (
        workflow.get_parameter_type(
            workflow_meta,
            "data_preprocessing",
            "imputation",
            "knn",
            "number_of_neighbours",
        )
        == "numeric"
    )
    assert (
        workflow.get_parameter_type(
            workflow_meta,
            "importing",
            "ms_data_import",
            "max_quant_import",
            "file_path",
        )
        == "file"
    )


def test_get_workflow_default_param_value(example_workflow):
    threshold_value = get_workflow_default_param_value(
        example_workflow,
        "data_preprocessing",
        "filter_proteins",
        "samples_missing_filter",
        0,
        "percentage",
    )
    output_name = get_workflow_default_param_value(
        example_workflow,
        "data_preprocessing",
        "normalisation",
        "median",
        5,
        "output_name",
    )
    output_name_t_test = get_workflow_default_param_value(
        example_workflow,
        "data_analysis",
        "differential_expression",
        "t_test",
        1,
        "output_name",
    )

    assert threshold_value == 0.2
    assert output_name == "preprocessed-data"
    assert output_name_t_test == None


def test_get_workflow_default_param_value_nonexistent(example_workflow_short):
    threshold_value = get_workflow_default_param_value(
        example_workflow_short,
        "data_preprocessing",
        "filter_samples",
        "protein_intensity_sum_filter",
        0,
        "deviation_threshold",
    )

    assert threshold_value is None


def test_test_get_workflow_default_param_value_no_side_effects(example_workflow):
    example_workflow_copy = example_workflow.copy()
    get_workflow_default_param_value(
        example_workflow,
        "data_preprocessing",
        "filter_proteins",
        "samples_missing_filter",
        0,
        "percentage",
    )
    assert example_workflow == example_workflow_copy


def test_get_global_index_of_step(example_workflow):
    assert workflow.get_global_index_of_step(example_workflow, "importing", 0) == 0
    assert (
        workflow.get_global_index_of_step(example_workflow, "data_preprocessing", 0)
        == 2
    )
    assert (
        workflow.get_global_index_of_step(example_workflow, "data_preprocessing", 5)
        == 7
    )
    assert workflow.get_global_index_of_step(example_workflow, "data_analysis", 0) == 8

    assert (
        workflow.get_global_index_of_step(example_workflow, "data_integration", 4) == -1
    )
    assert (
        workflow.get_global_index_of_step(example_workflow, "nonexisting_section", 4)
        == -1
    )


def test_is_last_step_in_section(example_workflow):
    assert workflow.is_last_step_in_section(example_workflow, "data_preprocessing", 5)
    assert not workflow.is_last_step_in_section(
        example_workflow, "data_preprocessing", 4
    )


def test_is_last_step(example_workflow):
    assert workflow.is_last_step(example_workflow, 9)
    assert not workflow.is_last_step(example_workflow, 8)


def test_validate_workflow(example_workflow, workflow_meta):
    assert validate_workflow_parameters(example_workflow, workflow_meta)
    assert validate_workflow_graphs(example_workflow, workflow_meta)


def test_validate_workflow_wrong_graphs(workflow_wrong_graphs, workflow_meta):
    pytest.raises(
        ValueError, validate_workflow_graphs, workflow_wrong_graphs, workflow_meta
    )
    assert validate_workflow_parameters(workflow_wrong_graphs, workflow_meta)


def test_validate_workflow_wrong_parameters(workflow_wrong_parameters, workflow_meta):
    assert validate_workflow_graphs(workflow_wrong_parameters, workflow_meta)
    pytest.raises(
        ValueError,
        validate_workflow_parameters,
        workflow_wrong_parameters,
        workflow_meta,
    )
