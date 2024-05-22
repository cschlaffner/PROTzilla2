import json
import sys
from unittest import mock

import pytest

from protzilla.constants.paths import PROJECT_PATH
from protzilla.utilities import random_string

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
    return "tests/test_data/peptides_vsmall.txt"


def mock_perform_method(runner: Runner):
    mock_perform = mock.MagicMock()
    mock_perform.methods = []
    mock_perform.inputs = []

    def mock_current_parameters(*args, **kwargs):
        # saving parameters for later inspection
        mock_perform.methods.append(str(runner.run.current_step))
        mock_perform.inputs.append(runner.run.current_step.inputs)

        # side effect to mark the step as finished
        # runner.run.current_step._finished = True # TODO is deprecated

    mock_perform.side_effect = mock_current_parameters

    return mock_perform


def mock_perform_plot(runner: Runner):
    mock_plot = mock.MagicMock()
    mock_plot.inputs = []

    def mock_current_parameters(*args, **kwargs):
        # saving parameters for later inspection
        mock_plot.inputs.append(runner.run.current_step.plot_inputs)

    mock_plot.side_effect = mock_current_parameters

    return mock_plot


def test_runner_imports(
    monkeypatch, tests_folder_name, ms_data_path, metadata_path, peptide_path
):
    importing_args = [
        "only_import",  # expects max-quant import, metadata import
        ms_data_path,
        f"--run_name={tests_folder_name}/test_runner_{random_string()}",
        f"--meta_data_path={metadata_path}",
    ]

    kwargs = args_parser().parse_args(importing_args).__dict__
    runner = Runner(**kwargs)

    mock_method = mock_perform_method(runner)
    monkeypatch.setattr(runner, "_perform_current_step", mock_method)

    runner.compute_workflow()

    expected_methods = ["MaxQuantImport", "MetadataImport"]
    expected_method_parameters = [
        {"file_path": ms_data_path, "intensity_name": "iBAQ", "map_to_uniprot": False},
        {
            "file_path": metadata_path,
            "feature_orientation": "Columns (samples in rows, features in columns)",
        },
    ]

    assert mock_method.methods == expected_methods
    assert mock_method.inputs == expected_method_parameters
    assert mock_method.call_count == 2


def test_runner_raises_error_for_missing_metadata_arg(
    monkeypatch, tests_folder_name, ms_data_path
):
    no_metadata_args = [
        "only_import",
        ms_data_path,
        f"--run_name={tests_folder_name}/test_runner_{random_string()}",
    ]
    kwargs = args_parser().parse_args(no_metadata_args).__dict__
    runner = Runner(**kwargs)
    mock_method = mock_perform_method(runner)

    monkeypatch.setattr(runner, "_perform_current_step", mock_method)

    with pytest.raises(ValueError) as e:
        runner.compute_workflow()


def test_runner_calculates(monkeypatch, tests_folder_name, ms_data_path, metadata_path):
    calculating_args = [
        "only_import_and_filter_proteins",
        ms_data_path,
        f"--run_name={tests_folder_name}/test_runner_{random_string()}",
        f"--meta_data_path={metadata_path}",
    ]
    kwargs = args_parser().parse_args(calculating_args).__dict__
    runner = Runner(**kwargs)

    mock_method = mock_perform_method(runner)

    mock_plot = mock_perform_plot(runner)

    monkeypatch.setattr(runner, "_perform_current_step", mock_method)
    for step in runner.run.steps.data_preprocessing:
        monkeypatch.setattr(step, "plot", mock_plot)

    runner.compute_workflow()

    assert mock_method.methods == [
        "MaxQuantImport",
        "MetadataImport",
        "FilterProteinsBySamplesMissing",
    ]
    assert {"percentage": 0.2} in mock_method.inputs
    assert mock_method.call_count == 3
    mock_plot.assert_not_called()


def test_runner_calculates_logging(caplog, tests_folder_name, ms_data_path):
    calculating_args = [
        "only_import_and_filter_proteins",
        "wrong_ms_data_path",
        f"--run_name={tests_folder_name}/test_runner_{random_string()}",
        f"--meta_data_path={metadata_path}",
    ]
    kwargs = args_parser().parse_args(calculating_args).__dict__
    runner = Runner(**kwargs)

    runner.compute_workflow()

    assert "ERROR" in caplog.text
    assert "FileNotFoundError" in caplog.text


def test_runner_plots(monkeypatch, tests_folder_name, ms_data_path, metadata_path):
    plot_args = [
        "only_import_and_filter_proteins",
        ms_data_path,
        f"--run_name={tests_folder_name}/test_runner_{random_string()}",
        f"--meta_data_path={metadata_path}",
        "--all_plots",
    ]
    kwargs = args_parser().parse_args(plot_args).__dict__
    runner = Runner(**kwargs)

    mock_method = mock_perform_method(runner)
    mock_plot = mock_perform_plot(runner)

    monkeypatch.setattr(runner, "_perform_current_step", mock_method)
    for step in runner.run.steps.data_preprocessing:
        monkeypatch.setattr(step, "plot", mock_plot)

    runner.compute_workflow()

    assert mock_plot.call_count == 1
    assert mock_plot.inputs == [{"graph_type": "Pie chart"}]


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
        "graph_type_quantities": "Pie chart",
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
