import json
import sys
from unittest import mock

import pytest

from protzilla.constants.paths import PROJECT_PATH
from protzilla.utilities.random import random_string
from protzilla.workflow_helper import get_steps_of_workflow

sys.path.append(f"{PROJECT_PATH}/..")
sys.path.append(f"{PROJECT_PATH}")

from protzilla.runner import Runner, _serialize_graphs
from runner_cli import args_parser


@pytest.fixture
def ms_data_path():
    return "tests/proteinGroups_small_cut.txt"


@pytest.fixture
def metadata_path():
    return "tests/metadata_cut_columns.csv"


@pytest.fixture
def peptide_path():
    return "tests/test_data/peptides-vsmall.txt"


def test_runner_imports(
    monkeypatch, tests_folder_name, ms_data_path, metadata_path, peptide_path
):
    importing_args = [
        "only_import",  # expects max-quant import, metadata import
        ms_data_path,
        f"--run_name={tests_folder_name}/test_runner_{random_string()}",
        f"--meta_data_path={metadata_path}",
        f"--peptides_path={peptide_path}",
    ]

    kwargs = args_parser().parse_args(importing_args).__dict__
    runner = Runner(**kwargs)

    mock_perform = mock.MagicMock()
    mock_add_step = mock.MagicMock()

    def mock_current_parameters(*args, **kwargs):
        runner.run.current_parameters = {None: {}}

    mock_perform.side_effect = mock_current_parameters
    monkeypatch.setattr(runner, "_perform_current_step", mock_perform)
    monkeypatch.setattr(runner.run.history, "add_step", mock_add_step)

    runner.compute_workflow()

    calls = [
        mock.call({"intensity_name": "iBAQ", "file_path": ms_data_path}),
        mock.call(
            {
                "feature_orientation": "Rows (features in rows, samples in columns)",
                "file_path": metadata_path,
            }
        ),
        mock.call({"intensity_name": "iBAQ", "file_path": peptide_path}),
    ]

    mock_perform.assert_has_calls(calls)
    assert mock_perform.call_count == 3


def test_runner_raises_error_for_missing_metadata_arg(
    monkeypatch, tests_folder_name, ms_data_path
):
    no_metadata_args = [
        "only_import",
        ms_data_path,
        f"--run_name={tests_folder_name}/test_runner_{random_string()}",
    ]
    with pytest.raises(ValueError) as e:
        kwargs = args_parser().parse_args(no_metadata_args).__dict__
        runner = Runner(**kwargs)
        mock_perform = mock.MagicMock()

        def mock_current_parameters(*args, **kwargs):
            runner.run.current_parameters = {None: {}}

        mock_perform.side_effect = mock_current_parameters

        monkeypatch.setattr(runner, "_perform_current_step", mock_perform)
        monkeypatch.setattr(runner.run.history, "add_step", mock.MagicMock())
        monkeypatch.setattr(
            runner.run, "create_plot_from_current_location", mock.MagicMock()
        )

        runner.compute_workflow()


def test_runner_calculates(monkeypatch, tests_folder_name, ms_data_path, metadata_path):
    calculating_args = [
        "only_import_and_filter_proteins",
        ms_data_path,
        f"--run_name={tests_folder_name}/test_runner_{random_string()}",
    ]
    kwargs = args_parser().parse_args(calculating_args).__dict__
    runner = Runner(**kwargs)

    mock_perform = mock.MagicMock()

    def mock_current_parameters(*args, **kwargs):
        runner.run.current_parameters = {None: {}}

    mock_perform.side_effect = mock_current_parameters
    mock_plot = mock.MagicMock()

    monkeypatch.setattr(runner, "_perform_current_step", mock_perform)
    monkeypatch.setattr(runner.run.history, "add_step", mock.MagicMock())
    monkeypatch.setattr(runner.run, "create_plot_from_current_location", mock_plot)

    runner.compute_workflow()

    mock_perform.assert_any_call({"threshold": 0.2})
    assert mock_perform.call_count == 2
    mock_plot.assert_not_called()


def test_runner_plots(monkeypatch, tests_folder_name, ms_data_path):
    plot_args = [
        "only_import_and_filter_proteins",
        ms_data_path,
        f"--run_name={tests_folder_name}/test_runner_{random_string()}",
        "--all_plots",
    ]
    kwargs = args_parser().parse_args(plot_args).__dict__
    runner = Runner(**kwargs)

    mock_plot = mock.MagicMock()
    mock_perform = mock.MagicMock()

    def mock_current_parameters(*args, **kwargs):
        runner.run.current_parameters = {None: {}}

    mock_perform.side_effect = mock_current_parameters

    monkeypatch.setattr(runner, "_perform_current_step", mock_perform)
    monkeypatch.setattr(runner.run.history, "add_step", mock.MagicMock())
    monkeypatch.setattr(runner.run, "create_plot_from_current_location", mock_plot)

    runner.compute_workflow()

    mock_plot.assert_called_once_with(
        parameters={"graph_type": "Pie chart"},
    )


def test_serialize_graphs():
    pre_graphs = [  # this is what the "graphs" section of a step should look like
        {"graph_type": "Bar chart", "group_by": "Sample"},
        {"graph_type_quantities": "Pie chart"},
    ]
    expected = {
        "graph_type": "Bar chart",
        "group_by": "Sample",
        "graph_type_quantities": "Pie chart",
    }
    assert _serialize_graphs(pre_graphs) == expected


def test_serialize_workflow_graphs():
    with open(
        PROJECT_PATH / "tests" / "test_workflows" / "example_workflow.json", "r"
    ) as f:
        workflow_config = json.load(f)

    serial_imputation_graphs = {
        "graph_type": "Bar chart",
        "group_by": "Sample",
        "graph_type_quantites": "Pie chart",
    }

    serial_filter_graphs = {"graph_type": "Pie chart"}

    steps = workflow_config["sections"]["data_preprocessing"]["steps"]
    for step in steps:
        if step["name"] == "imputation":
            assert _serialize_graphs(step["graphs"]) == serial_imputation_graphs
        elif step["name"] == "filter_proteins":
            assert _serialize_graphs(step["graphs"]) == serial_filter_graphs


def test_integration_runner(metadata_path, ms_data_path, tests_folder_name):
    name = tests_folder_name + "/test_runner_integration_" + random_string()
    runner = Runner(
        **{
            "workflow": "standard",
            "ms_data_path": f"{PROJECT_PATH}/{ms_data_path}",
            "meta_data_path": f"{PROJECT_PATH}/{metadata_path}",
            "peptides_path": None,
            "run_name": f"{name}",
            "df_mode": "disk",
            "all_plots": True,
            "verbose": False,
        }
    )
    runner.compute_workflow()


def test_integration_all_methods_runner(
    workflow_meta, metadata_path, ms_data_path, tests_folder_name, peptide_path
):
    with open(f"{PROJECT_PATH}/tests/test_workflows/test_methods1.json", "r") as f:
        workflow1 = json.load(f)
    with open(f"{PROJECT_PATH}/tests/test_workflows/test_methods2.json", "r") as f:
        workflow2 = json.load(f)

    test_workflows = [workflow1, workflow2]
    # test if all methods are covered in test_workflows
    tested_methods = set()
    existing_methods = set()

    for workflow in test_workflows:
        for section in get_steps_of_workflow(workflow):
            for step in section["steps"]:
                tested_methods.add((step["name"], step["method"]))
    for _, section in workflow_meta.items():
        for step_name, step in section.items():
            for method, _ in step.items():
                existing_methods.add((step_name, method))

    assert (
        existing_methods == tested_methods
    ), "please add new methods to a workflow in test_workflows or add a new workflow"

    for workflow in test_workflows:
        name = tests_folder_name + "/test_runner_integration" + random_string()
        runner = Runner(
            **{
                "workflow": "standard",
                "ms_data_path": f"{PROJECT_PATH}/{ms_data_path}",
                "meta_data_path": f"{PROJECT_PATH}/{metadata_path}",
                "peptides_path": f"{PROJECT_PATH}/{peptide_path}",
                "run_name": f"{name}",
                "df_mode": "disk",
                "all_plots": False,
                "verbose": False,
            }
        )
        runner.run.workflow_config = workflow
        runner.compute_workflow()


def test_integration_runner_no_plots(metadata_path, ms_data_path, tests_folder_name):
    name = tests_folder_name + "/test_runner_integration" + random_string()
    runner = Runner(
        **{
            "workflow": "standard",
            "ms_data_path": f"{PROJECT_PATH}/{ms_data_path}",
            "meta_data_path": f"{PROJECT_PATH}/{metadata_path}",
            "peptides_path": None,
            "run_name": f"{name}",
            "df_mode": "disk",
            "all_plots": False,
            "verbose": False,
        }
    )
    runner.compute_workflow()
