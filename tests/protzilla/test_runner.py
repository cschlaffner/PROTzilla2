import json
import sys
from pathlib import Path
from shutil import rmtree

import pytest

from protzilla.constants.paths import PROJECT_PATH, RUNS_PATH, WORKFLOWS_PATH
from protzilla.utilities.random import random_string

sys.path.append(f"{PROJECT_PATH}/..")
sys.path.append(f"{PROJECT_PATH}")

from protzilla.runner import Runner
from runner_cli import args_parser


def test_parse_existing_workflow():
    test_args = [
        "standard",
        "tests/proteinGroups_small_cut.txt",
        f"--name=test_parse_workflow_{random_string()}",
    ]
    parsed_args = args_parser().parse_args(test_args)
    runner = Runner(parsed_args)

    with open(Path(f"{WORKFLOWS_PATH}/standard.json"), "r") as f:
        expected_workflow = json.load(f)
    assert runner.run.workflow_config == expected_workflow
    rmtree(runner.run.run_path)


def test_parse_non_existing_workflow():
    run_name = f"test_parse_non_existent_workflow_{random_string()}"
    test_args = [
        "non-existent",
        "tests/proteinGroups_small_cut.txt",
        f"--name={run_name}",
    ]
    parsed_args = args_parser().parse_args(test_args)
    with pytest.raises(FileNotFoundError):
        Runner(parsed_args)

    rmtree(RUNS_PATH / run_name)


def test_parse_ms_data():
    run_name = f"test_parse_ms_data_{random_string()}"
    test_args = [
        "non-existent",
        "tests/proteinGroups_small_cut.txt",
        f"--name={run_name}",
    ]
    parsed_args = args_parser().parse_args(test_args)
    Runner(parsed_args)

    # think about importing data manually vs just checking if correct methods were called
    # assert runner.run.df ==


def test_parse_ms_data_path():
    parser = args_parser()
    print(parser)
