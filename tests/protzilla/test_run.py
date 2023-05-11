import json
from shutil import rmtree

import pytest
from PIL import Image

from protzilla import data_preprocessing
from protzilla.constants.paths import PROJECT_PATH, RUNS_PATH
from protzilla.importing import ms_data_import
from protzilla.run import Run
from protzilla.utilities.random import random_string


@pytest.fixture
def example_workflow():
    with open(f"{PROJECT_PATH}/tests/test_workflows/example_workflow.json", "r") as f:
        return json.load(f)


def test_updated_params_in_workflow_config(example_workflow_short):
    run_name = "test_export_workflow" + random_string()
    run = Run.create(run_name, df_mode="memory")

    run.calculate_and_next(
        ms_data_import.max_quant_import,
        file_path=f"{PROJECT_PATH}/tests/proteinGroups_small_cut.txt",
        intensity_name="Intensity",
    )
    run.perform_calculation_from_location(
        "data_preprocessing",
        "filter_proteins",
        "low_frequency_filter",
        {"threshold": 0.5},
    )
    assert (
        run.workflow_config["sections"]["data_preprocessing"]["steps"][0]["parameters"][
            "threshold"
        ]
        == 0.5
    )

    run.perform_calculation_from_location(
        "data_preprocessing",
        "filter_proteins",
        "low_frequency_filter",
        {"threshold": 1},
    )
    assert (
        run.workflow_config["sections"]["data_preprocessing"]["steps"][0]["parameters"][
            "threshold"
        ]
        == 1
    )
    rmtree(RUNS_PATH / run_name)


def test_run_create():
    # here the run should be used like in the CLI
    name = "test_run" + random_string()
    run = Run.create(name)
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        # call with str to make json serializable
        file_path=f"{PROJECT_PATH}/tests/proteinGroups_small_cut.txt",
        intensity_name="Intensity",
    )
    run.calculate_and_next(
        data_preprocessing.filter_proteins.by_low_frequency, threshold=1
    )
    run.calculate_and_next(
        data_preprocessing.filter_samples.by_protein_intensity_sum, threshold=1
    )
    rmtree(RUNS_PATH / name)
    # print([s.outputs for s in run.history.steps])
    # to get a history that can be used to create a worklow, the section, step, method
    # should be set by calculate_and_next


def test_run_back():
    name = "test_run_back" + random_string()
    run = Run.create(name)
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        # call with str to make json serializable
        file_path=f"{PROJECT_PATH}/tests/proteinGroups_small_cut.txt",
        intensity_name="Intensity",
    )
    df1 = run.df
    run.calculate_and_next(
        data_preprocessing.filter_proteins.by_low_frequency, threshold=1
    )
    df2 = run.df
    assert not df1.equals(df2)
    run.back_step()
    assert run.df.equals(df1)
    run.back_step()
    assert run.df is None
    rmtree(RUNS_PATH / name)


def test_run_continue():
    run_name = "test_run_continue" + random_string()
    run = Run.create(run_name, df_mode="disk")

    run.calculate_and_next(
        ms_data_import.max_quant_import,
        file_path=f"{PROJECT_PATH}/tests/proteinGroups_small_cut.txt",
        intensity_name="Intensity",
    )
    df = run.df
    del run
    run2 = Run.continue_existing(run_name)
    assert df.equals(run2.df)
    rmtree(RUNS_PATH / run_name)


def test_current_run_location():
    run_name = "test_run_current_location" + random_string()
    run = Run.create(
        run_name, df_mode="disk", workflow_config_name="test_data_preprocessing"
    )
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        file_path=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
        intensity_name="Intensity",
    )
    run.calculate_and_next(
        data_preprocessing.filter_proteins.by_low_frequency, threshold=1
    )
    assert run.current_run_location() == (
        "data_preprocessing",
        "filter_samples",
        "protein_intensity_sum_filter",
    )
    run.back_step()
    assert run.current_run_location() == (
        "data_preprocessing",
        "filter_proteins",
        "low_frequency_filter",
    )
    rmtree(RUNS_PATH / run_name)


def test_perform_calculation_logging(caplog):
    run_name = "test_run_logging" + random_string()
    run = Run.create(run_name, df_mode="disk")
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        file_path=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
        intensity_name="Intensity",
    )

    run.perform_calculation_from_location(
        "data_preprocessing",
        "outlier_detection",
        "local_outlier_factor",
        {"number_of_neighbors": 3},
    )

    assert "ERROR" in caplog.text
    assert "LocalOutlierFactor" in caplog.text
    assert "NaN values" in caplog.text
    rmtree(RUNS_PATH / run_name)


def test_insert_step(example_workflow_short):
    run_name = "test_insert_as_next_step" + random_string()
    run = Run.create(run_name)

    run.workflow_config = example_workflow_short
    importing_steps = run.workflow_config["sections"]["importing"]
    assert len(importing_steps["steps"]) == 1
    run.insert_step("metadata_import", "importing", "metadata_import_method", 1)
    assert len(importing_steps["steps"]) == 2

    assert importing_steps["steps"][1] == {
        "name": "metadata_import",
        "method": "metadata_import_method",
        "parameters": {
            "feature_orientation": "Columns (samples in rows, features in columns)",
            "file_path": None,
        },
    }
    rmtree(RUNS_PATH / run_name)


def test_insert_at_next_position_correct_location(example_workflow):
    run_name = "test_insert_as_next_step_correct_location" + random_string()
    run = Run.create(run_name)

    run.workflow_config = example_workflow
    preprocessing_steps = run.workflow_config["sections"]["data_preprocessing"]

    # test correct inserting section
    step_count = len(preprocessing_steps["steps"])
    run.insert_at_next_position(
        "metadata_import", "importing", "metadata_import_method"
    )
    assert len(preprocessing_steps["steps"]) == step_count
    run.insert_at_next_position("outlier_detection", "data_preprocessing", "pca")
    assert len(preprocessing_steps["steps"]) == step_count + 1

    # test added step is in first position
    assert preprocessing_steps["steps"][0]["name"] == "outlier_detection"

    rmtree(RUNS_PATH / run_name)


def test_delete_step(example_workflow_short):
    run_name = "test_delete_step" + random_string()
    run = Run.create(run_name)

    run.workflow_config = example_workflow_short
    importing_steps = run.workflow_config["sections"]["importing"]
    count = len(importing_steps["steps"])
    run.delete_step("importing", 0)
    assert len(importing_steps["steps"]) == count - 1
    rmtree(RUNS_PATH / run_name)


def test_export_plot():
    run_name = "test_export_plot" + random_string()
    run = Run.create(run_name)

    run.calculate_and_next(
        ms_data_import.max_quant_import,
        file_path=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
        intensity_name="Intensity",
    )
    run.perform_calculation(
        data_preprocessing.filter_proteins.by_low_frequency, dict(threshold=1)
    )
    run.create_plot(
        data_preprocessing.filter_proteins.by_low_frequency_plot,
        dict(graph_type="Pie chart"),
    )
    for plot in run.export_plots("png"):
        Image.open(plot).verify()
    run.next_step()
    run.perform_calculation(data_preprocessing.imputation.by_min_per_sample, {})
    run.create_plot(
        data_preprocessing.imputation.by_min_per_sample_plot,
        dict(graph_type="Boxplot", graph_type_quantites="Bar chart", group_by="Sample"),
    )
    assert len(run.plots) > 1
    for plot in run.export_plots("tiff"):
        Image.open(plot).verify()
    for plot in run.export_plots("eps"):
        Image.open(plot).verify()
    rmtree(RUNS_PATH / run_name)


def test_last_step_handling(example_workflow_short):
    run_name = "last_step_handling" + random_string()
    run = Run.create(run_name)
    run.workflow_config = example_workflow_short

    run.calculate_and_next(
        ms_data_import.max_quant_import,
        file_path=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
        intensity_name="Intensity",
    )
    run.perform_calculation(
        data_preprocessing.filter_proteins.by_low_frequency, dict(threshold=1)
    )
    previous_step_index = run.step_index
    previous_location = (run.section, run.step, run.method)
    run.next_step()
    assert run.step_index == previous_step_index
    assert (run.section, run.step, run.method) == previous_location

    rmtree(RUNS_PATH / run_name)
