import sys
from unittest import mock

import pytest

from protzilla.constants.paths import PROJECT_PATH
from protzilla.utilities.random import random_string

sys.path.append(f"{PROJECT_PATH}/..")
sys.path.append(f"{PROJECT_PATH}")

from protzilla.runner import Runner
from runner_cli import args_parser


@pytest.fixture
def ms_data_path():
    return "tests/proteinGroups_small_cut.txt"


@pytest.fixture
def metadata_path():
    return "tests/metadata_cut_columns.csv"


@pytest.fixture
def importing_args(tests_folder_name, metadata_path, ms_data_path):
    return [
        "only_import",  # expects max-quant import, metadata import
        ms_data_path,
        f"--name={tests_folder_name}/test_runner_{random_string()}",
        f"--metaDataPath={metadata_path}",
    ]


@pytest.fixture
def no_metadata_args(tests_folder_name, ms_data_path):
    return [
        "only_import",  # expects max-quant import, metadata import
        ms_data_path,
        f"--name={tests_folder_name}/test_runner_{random_string()}",
    ]


@pytest.fixture
def calculating_args(tests_folder_name, ms_data_path):
    return [
        # expects: max-quant, filter proteins
        "only_import_and_filter_proteins",
        ms_data_path,
        f"--name={tests_folder_name}/test_runner_{random_string()}",
    ]


@pytest.fixture
def plot_args(tests_folder_name, metadata_path, ms_data_path):
    return [
        # expects: max-quant, filter proteins
        "only_import_and_filter_proteins",
        ms_data_path,
        f"--name={tests_folder_name}/test_runner_{random_string()}",
        "--allPlots",
    ]


def prep_run_and_compute(monkeypatch, args):
    runner = Runner(args_parser().parse_args(args))

    mock_perform = mock.MagicMock()
    mock_add_step = mock.MagicMock()
    mock_plot = mock.MagicMock()

    monkeypatch.setattr(runner, "_perform_current_step", mock_perform)
    monkeypatch.setattr(runner.run.history, "add_step", mock_add_step)
    monkeypatch.setattr(runner.run, "create_plot_from_location", mock_plot)

    runner.compute_workflow()
    return dict(
        runner=runner, perform=mock_perform, add_step=mock_add_step, plot=mock_plot
    )


def test_runner_imports(monkeypatch, importing_args, ms_data_path, metadata_path):
    out = prep_run_and_compute(monkeypatch, importing_args)
    mock_perform = out["perform"]

    calls = [
        mock.call({"intensity_name": "iBAQ", "file_path": ms_data_path}),
        mock.call(
            {
                "feature_orientation": "Rows (features in rows, samples in columns)",
                "file_path": metadata_path,
            }
        ),
    ]

    mock_perform.assert_has_calls(calls)
    assert mock_perform.call_count == 2


def test_runner_raises_error_for_missing_metadata_arg(monkeypatch, no_metadata_args):
    pytest.raises(ValueError, prep_run_and_compute, monkeypatch, no_metadata_args)


def test_runner_calculates(monkeypatch, calculating_args, ms_data_path, metadata_path):
    out = prep_run_and_compute(monkeypatch, calculating_args)
    mock_perform = out["perform"]
    mock_plot = out["plot"]

    mock_perform.assert_any_call({"threshold": 0.2})
    # import, filter proteins
    assert mock_perform.call_count == 2
    mock_plot.assert_not_called()


def test_runner_plots(monkeypatch, plot_args):
    out = prep_run_and_compute(monkeypatch, plot_args)
    mock_plot = out["plot"]

    mock_plot.assert_called_once_with(
        "data_preprocessing",
        "filter_proteins",
        "low_frequency_filter",
        parameters={"graph_type": "Pie chart"},
    )
