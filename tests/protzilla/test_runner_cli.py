import logging
import sys
from unittest import mock

import pytest
import yaml

from protzilla.constants.paths import PROJECT_PATH
from protzilla.utilities import random_string

sys.path.append(f"{PROJECT_PATH}/..")
sys.path.append(f"{PROJECT_PATH}")

from protzilla.runner import Runner
from runner_cli import args_parser


def test_parse_run_name(tests_folder_name):
    run_name = f"{tests_folder_name}/test_parse_run_name_{random_string()}"
    test_args = ["standard", "ms_data", f"--run_name={run_name}", f"--all_plots"]
    parsed_args = args_parser().parse_args(test_args).__dict__
    assert Runner(**parsed_args).run_name == run_name


def test_existing_workflow(tests_folder_name):
    workflow_name = "standard"
    test_args = [
        workflow_name,
        "ms_data",
        f"--run_name={tests_folder_name}/test_existing_workflow_{random_string()}",
    ]
    parsed_args = args_parser().parse_args(test_args).__dict__
    runner = Runner(**parsed_args)

    assert runner.workflow == workflow_name
    with open(f"{runner.run.run_path}/run.yaml", "r") as f:
        run_config = yaml.safe_load(f)

    assert len(run_config["steps"]) == len(runner.run.steps.all_steps)


def test_non_existing_workflow(tests_folder_name):
    run_name = f"{tests_folder_name}/test_non_existent_workflow_{random_string()}"
    test_args = [
        "non-existent",
        "ms_data",
        f"--run_name={run_name}",
    ]
    parsed_args = args_parser().parse_args(test_args).__dict__
    with pytest.raises(FileNotFoundError):
        Runner(**parsed_args)


def test_parse_ms_data(tests_folder_name):
    run_name = f"{tests_folder_name}/test_parse_ms_data_{random_string()}"
    ms_data_path = "tests/proteinGroups_small_cut.txt"
    test_args = [
        "standard",
        ms_data_path,
        f"--run_name={run_name}",
    ]
    parsed_args = args_parser().parse_args(test_args).__dict__
    assert Runner(**parsed_args).ms_data_path == ms_data_path


def test_parse_meta_data(tests_folder_name):
    run_name = f"{tests_folder_name}/test_parse_meta_data_{random_string()}"
    meta_data_path = "tests/metadata_cut_columns.csv"
    test_args = [
        "standard",
        "ms_data",
        f"--run_name={run_name}",
        f"--meta_data_path={meta_data_path}",
    ]
    parsed_args = args_parser().parse_args(test_args).__dict__
    assert Runner(**parsed_args).meta_data_path == meta_data_path


def test_parse_all_plots(tests_folder_name):
    run_name = f"{tests_folder_name}/test_parse_all_plots_{random_string()}"
    test_args = ["standard", "ms_data", f"--run_name={run_name}", f"--all_plots"]
    parsed_args = args_parser().parse_args(test_args).__dict__
    assert Runner(**parsed_args).all_plots


def test_parse_verbose(caplog, tests_folder_name):
    caplog.set_level(logging.INFO)
    run_name = f"{tests_folder_name}/test_parse_meta_data_{random_string()}"
    test_args = ["standard", "ms_data", f"--run_name={run_name}", f"--verbose"]
    parsed_args = args_parser().parse_args(test_args).__dict__
    assert Runner(**parsed_args).verbose
    assert "Parsed arguments" in caplog.text


def test_run_already_exists(monkeypatch, capsys, tests_folder_name):
    run_name = f"{tests_folder_name}/test_run_already_exists_{random_string()}"
    test_args = ["standard", "ms_data", f"--run_name={run_name}"]
    Runner(**args_parser().parse_args(test_args).__dict__)

    mock_input_no = mock.Mock(return_value="n")
    monkeypatch.setattr("builtins.input", mock_input_no)
    pytest.raises(SystemExit, Runner, **args_parser().parse_args(test_args).__dict__)

    mock_input_yes = mock.Mock(return_value="y")
    monkeypatch.setattr("builtins.input", mock_input_yes)
    Runner(**args_parser().parse_args(test_args).__dict__)
    assert mock_input_yes.call_count == 1
