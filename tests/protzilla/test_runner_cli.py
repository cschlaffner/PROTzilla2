import json
import logging
import sys

import pytest

from protzilla.constants.paths import PROJECT_PATH
from protzilla.utilities.random import random_string

sys.path.append(f"{PROJECT_PATH}/..")
sys.path.append(f"{PROJECT_PATH}")

from protzilla.runner import Runner
from runner_cli import args_parser


def test_parse_run_name(tests_folder_name):
    run_name = f"{tests_folder_name}/test_parse_run_name_{random_string()}"
    test_args = ["standard", "ms_data", f"--name={run_name}", f"--allPlots"]
    parsed_args = args_parser().parse_args(test_args)
    print(parsed_args)
    assert Runner(parsed_args).args.name == run_name


def test_existing_workflow(tests_folder_name):
    workflow_name = "standard"
    test_args = [
        workflow_name,
        "ms_data",
        f"--name={tests_folder_name}/test_existing_workflow_{random_string()}",
    ]
    parsed_args = args_parser().parse_args(test_args)
    runner = Runner(parsed_args)

    assert runner.args.workflow == workflow_name
    with open(f"{runner.run.run_path}/run_config.json", "r") as f:
        run_config = json.load(f)
    assert run_config["workflow_config_name"] == workflow_name


def test_non_existing_workflow(tests_folder_name):
    run_name = f"{tests_folder_name}/test_non_existent_workflow_{random_string()}"
    test_args = [
        "non-existent",
        "ms_data",
        f"--name={run_name}",
    ]
    parsed_args = args_parser().parse_args(test_args)
    with pytest.raises(FileNotFoundError):
        Runner(parsed_args)


def test_parse_ms_data(tests_folder_name):
    run_name = f"{tests_folder_name}/test_parse_ms_data_{random_string()}"
    ms_data_path = "tests/proteinGroups_small_cut.txt"
    test_args = [
        "standard",
        ms_data_path,
        f"--name={run_name}",
    ]
    parsed_args = args_parser().parse_args(test_args)
    assert Runner(parsed_args).args.msDataPath == ms_data_path


def test_parse_meta_data(tests_folder_name):
    run_name = f"{tests_folder_name}/test_parse_meta_data_{random_string()}"
    meta_data_path = "tests/metadata_cut_columns.csv"
    test_args = [
        "standard",
        "ms_data",
        f"--name={run_name}",
        f"--metaDataPath={meta_data_path}",
    ]
    parsed_args = args_parser().parse_args(test_args)
    assert Runner(parsed_args).args.metaDataPath == meta_data_path


def test_parse_all_plots(tests_folder_name):
    run_name = f"{tests_folder_name}/test_parse_meta_data_{random_string()}"
    test_args = ["standard", "ms_data", f"--name={run_name}", f"--allPlots"]
    parsed_args = args_parser().parse_args(test_args)
    assert Runner(parsed_args).args.allPlots


def test_parse_verbose(caplog, tests_folder_name):
    caplog.set_level(logging.INFO)
    run_name = f"{tests_folder_name}/test_parse_meta_data_{random_string()}"
    test_args = ["standard", "ms_data", f"--name={run_name}", f"--verbose"]
    parsed_args = args_parser().parse_args(test_args)
    assert Runner(parsed_args).args.verbose
    assert "Parsed arguments" in caplog.text
