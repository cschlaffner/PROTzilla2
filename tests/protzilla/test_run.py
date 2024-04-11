import json
from shutil import rmtree

import numpy as np
import pandas as pd
import pytest
from PIL import Image

from protzilla import data_integration, data_preprocessing
from protzilla.constants.paths import PROJECT_PATH, RUNS_PATH
from protzilla.importing import metadata_import, ms_data_import
from protzilla.run import Run
from protzilla.utilities import random_string
from protzilla.workflow_helper import get_workflow_default_param_value


@pytest.fixture
def example_workflow():
    with open(f"{PROJECT_PATH}/tests/test_workflows/example_workflow.json", "r") as f:
        return json.load(f)


@pytest.fixture
def example_workflow_short_updated():
    with open(
        f"{PROJECT_PATH}/tests/test_workflows/example_workflow_short_updated.json", "r"
    ) as f:
        return json.load(f)


def test_updated_params_in_workflow_config(example_workflow_short, tests_folder_name):
    run_name = tests_folder_name + "/test_export_workflow_" + random_string()

    run = Run.create(run_name, df_mode="memory")
    run.workflow_config = example_workflow_short

    run.perform_current_calculation_step_and_next(
        dict(
            file_path=f"{PROJECT_PATH}/tests/proteinGroups_small_cut.txt",
            intensity_name="Intensity",
        )
    )
    run.perform_current_calculation_step(
        {"percentage": 0.5},
    )
    assert (
        run.workflow_config["sections"]["data_preprocessing"]["steps"][0]["parameters"][
            "percentage"
        ]
        == 0.5
    )

    run.perform_calculation_from_location(
        "data_preprocessing",
        "filter_proteins",
        "samples_missing_filter",
        {"percentage": 1},
    )
    assert (
        run.workflow_config["sections"]["data_preprocessing"]["steps"][0]["parameters"][
            "percentage"
        ]
        == 1
    )


def test_run_create(tests_folder_name):
    run_name = tests_folder_name + "/test_run_create_" + random_string()

    # here the run should be used like in the CLI
    run = Run.create(run_name)
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        # call with str to make json serializable
        file_path=f"{PROJECT_PATH}/tests/proteinGroups_small_cut.txt",
        intensity_name="Intensity",
    )

    # skip metadata import
    run.step_index += 1

    run.calculate_and_next(
        data_preprocessing.filter_proteins.by_samples_missing, percentage=1
    )
    run.calculate_and_next(
        data_preprocessing.filter_samples.by_protein_intensity_sum,
        deviation_threshold=1,
    )
    # print([s.outputs for s in run.history.steps])
    # to get a history that can be used to create a worklow, the section, step, method
    # should be set by calculate_and_next


def test_run_back(tests_folder_name):
    run_name = tests_folder_name + "/test_run_back_" + random_string()

    run = Run.create(run_name)
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        # call with str to make json serializable
        file_path=f"{PROJECT_PATH}/tests/proteinGroups_small_cut.txt",
        intensity_name="Intensity",
    )
    df1 = run.df
    run.step_index += 1
    run.calculate_and_next(data_preprocessing.transformation.by_log)
    df2 = run.df
    assert not df1.equals(df2)
    run.back_step()
    assert run.df.equals(df1)
    run.back_step()
    assert run.df is None


def test_run_navigate(tests_folder_name):
    run_name = tests_folder_name + "/test_run_back_" + random_string()

    run = Run.create(run_name)
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        # call with str to make json serializable
        file_path=f"{PROJECT_PATH}/tests/proteinGroups_small_cut.txt",
        intensity_name="Intensity",
    )
    run.calculate_and_next(
        metadata_import.metadata_import_method,
        name="metadata_import",
        file_path=f"{PROJECT_PATH}/tests/metadata_cut_columns.csv",
        feature_orientation="Columns (samlpes in rows, features in columns)",
    )
    run.calculate_and_next(
        data_preprocessing.filter_proteins.by_samples_missing,
        percentage=0.2,
    )
    run.calculate_and_next(
        data_preprocessing.filter_samples.by_protein_intensity_sum,
        deviation_threshold=1,
    )

    # test navigate within section
    run.navigate("data_preprocessing", 1)
    assert run.section == "data_preprocessing"
    assert run.step == "filter_samples"
    assert run.method == "protein_intensity_sum_filter"
    assert run.step_index == 3

    # test navigate between sections
    run.navigate("importing", 0)
    assert run.section == "importing"
    assert run.step == "ms_data_import"
    assert run.method == "max_quant_import"
    assert run.step_index == 0

    run.next_step()
    run.calculate_and_next(data_preprocessing.filter_proteins.by_samples_missing)
    run.calculate_and_next(data_preprocessing.filter_samples.by_protein_intensity_sum)

    # test navigate to future step
    with pytest.raises(Exception):
        run.navigate("data_preprocessing", 3)


def test_run_continue(tests_folder_name):
    run_name = tests_folder_name + "/test_run_continue_" + random_string()

    run = Run.create(run_name, df_mode="disk")

    run.calculate_and_next(
        ms_data_import.max_quant_import,
        name="ms_import",
        file_path=f"{PROJECT_PATH}/tests/proteinGroups_small_cut.txt",
        intensity_name="Intensity",
    )
    run.calculate_and_next(
        metadata_import.metadata_import_method,
        name="metadata_import",
        file_path=f"{PROJECT_PATH}/tests/metadata_cut_columns.csv",
        feature_orientation="Columns (samlpes in rows, features in columns)",
    )
    df = run.df
    del run

    run2 = Run.continue_existing(run_name)
    assert df.equals(run2.df)

    del run2
    # delete dataframes and history_dfs folder of run
    folder_path = RUNS_PATH / run_name
    rmtree(folder_path / "dataframes")
    rmtree(folder_path / "history_dfs")
    # run should be started at the beginning
    run3 = Run.continue_existing(run_name)
    assert run3.df is None
    assert any("Restarted" in message["msg"] for message in run3.current_messages)


def test_current_run_location(tests_folder_name):
    run_name = tests_folder_name + "/test_run_current_location_" + random_string()
    run = Run.create(
        run_name, df_mode="disk", workflow_config_name="test_data_preprocessing"
    )
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        file_path=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
        intensity_name="Intensity",
    )
    run.calculate_and_next(
        data_preprocessing.filter_proteins.by_samples_missing, percentage=1
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
        "samples_missing_filter",
    )


def test_perform_calculation_error_handling(caplog, tests_folder_name):
    # test specific error handling
    run_name = tests_folder_name + "/test_run_error_handling_" + random_string()
    run = Run.create(run_name, df_mode="disk")
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        file_path=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
        intensity_name="Intensity",
    )
    run.df["Intensity"] = np.nan

    run.perform_calculation_from_location(
        "data_preprocessing",
        "outlier_detection",
        "local_outlier_factor",
        {"number_of_neighbors": 3},
    )

    assert any(message["level"] == 40 for message in run.current_messages)


def test_insert_step(example_workflow_short, tests_folder_name):
    run_name = tests_folder_name + "/test_insert_as_next_step_" + random_string()
    run = Run.create(run_name)

    run.workflow_config = example_workflow_short
    importing_steps = run.workflow_config["sections"]["importing"]
    assert len(importing_steps["steps"]) == 1
    run.insert_step("metadata_import", "importing", "metadata_import_method", 1)
    assert len(importing_steps["steps"]) == 2

    assert importing_steps["steps"][1] == {
        "name": "metadata_import",
        "method": "metadata_import_method",
        "parameters": {},
    }


def test_insert_at_next_position_correct_location(example_workflow, tests_folder_name):
    run_name = (
        tests_folder_name
        + "/test_insert_as_next_step_correct_location_"
        + random_string()
    )
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


def test_delete_step(example_workflow_short, tests_folder_name):
    run_name = tests_folder_name + "/test_delete_step_" + random_string()
    run = Run.create(run_name)

    run.workflow_config = example_workflow_short
    importing_steps = run.workflow_config["sections"]["importing"]
    count = len(importing_steps["steps"])
    run.delete_step("importing", 0)
    assert len(importing_steps["steps"]) == count - 1


def test_export_plot(tests_folder_name):
    run_name = tests_folder_name + "/test_export_plot_" + random_string()

    run = Run.create(run_name)

    run.calculate_and_next(
        ms_data_import.max_quant_import,
        file_path=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
        intensity_name="Intensity",
    )
    run.step_index += 1
    run.perform_calculation(
        data_preprocessing.filter_proteins.by_samples_missing, dict(percentage=1)
    )
    run.create_plot(
        data_preprocessing.filter_proteins.by_samples_missing_plot,
        dict(graph_type="Pie chart"),
    )
    for plot in run.export_plots("png"):
        Image.open(plot).verify()
    run.next_step()
    run.perform_calculation(data_preprocessing.imputation.by_min_per_sample, {})
    run.create_plot(
        data_preprocessing.imputation.by_min_per_sample_plot,
        dict(
            graph_type="Boxplot",
            graph_type_quantities="Bar chart",
            group_by="Sample",
            proteins_of_interest=None,
            visual_transformation="linear",
        ),
    )
    assert len(run.plots) > 1
    for plot in run.export_plots("tiff"):
        Image.open(plot).verify()
    for plot in run.export_plots("eps"):
        Image.open(plot).verify()


def test_export_plot_base64(tests_folder_name):
    run_name = tests_folder_name + "/test_export_plot_" + random_string()
    input_df_path = (
        PROJECT_PATH
        / "tests/test_data/enrichment_data"
        / "Reactome_enrichment_enrichr.csv"
    )

    run = Run.create(run_name)
    run.create_step_plot(
        data_integration.di_plots.GO_enrichment_bar_plot,
        dict(
            input_df=pd.read_csv(input_df_path, sep="\t"),
            gene_sets=["Reactome_2013"],
            top_terms=10,
            cutoff=0.05,
            value="p_value",
        ),
    )
    for plot in run.export_plots("png"):
        Image.open(plot).verify()
    for plot in run.export_plots("tiff"):
        Image.open(plot).verify()
    for plot in run.export_plots("eps"):
        Image.open(plot).verify()


def test_next_step_error_handling(caplog, tests_folder_name):
    run_name = tests_folder_name + "/test_next_step_error_handling_" + random_string()
    run = Run.create(run_name)
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        "duplicate_name",
        file_path=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
        intensity_name="Intensity",
    )

    run.calculate_and_next(
        metadata_import.metadata_import_method,
        "duplicate_name",
        file_path=str(PROJECT_PATH / "tests/metadata_cut_columns.csv"),
        feature_orientation="Columns (samlpes in rows, features in columns)",
    )

    assert any(message["level"] == 40 for message in run.current_messages)


def test_name_step(example_workflow_short, tests_folder_name):
    # depends on test_read_write_local_workflow, test_get_workflow_default_param_value

    run_name = tests_folder_name + "/test_name_step_" + random_string()
    run = Run.create(run_name)

    run.history.step_names.append(None)
    run.name_step(0, "first_step")
    run.workflow_config = None
    run.read_local_workflow()
    output_name = get_workflow_default_param_value(
        run.workflow_config,
        "importing",
        "ms_data_import",
        "max_quant_import",
        run.step_index_in_current_section(),
        "output_name",
    )

    assert output_name == "first_step"


def test_read_write_local_workflow(example_workflow_short, tests_folder_name):
    run_name = tests_folder_name + "/test_read_write_local_workflow_" + random_string()

    run = Run.create(run_name)
    run.workflow_config = example_workflow_short
    run.write_local_workflow()
    run.workflow_config = None
    assert run.read_local_workflow() == example_workflow_short


def test_integration_updated_workflow_file(
    example_workflow_short, example_workflow_short_updated, tests_folder_name
):
    # depends on test_read_write_local_workflow

    run_name = (
        tests_folder_name + "/test_integration_updated_workflow_file_" + random_string()
    )
    run = Run.create(run_name)
    run.workflow_config = example_workflow_short

    run.calculate_and_next(
        ms_data_import.ms_fragger_import,
        file_path=f"{PROJECT_PATH}/tests/combined_protein_method_small_cut.tsv",
        intensity_name="Intensity",
    )
    run.perform_current_calculation_step({"percentage": 0.1})
    run.next_step("output_name1")

    run.insert_step(
        "filter_proteins", "data_preprocessing", "samples_missing_filter", 1
    )
    run.insert_step("filter_samples", "data_preprocessing", "protein_count_filter", 2)
    run.insert_step("dimension_reduction", "data_analysis", "umap", 3)

    run.workflow_config = None
    assert run.read_local_workflow() == example_workflow_short_updated


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
        data_preprocessing.filter_proteins.by_samples_missing, dict(percentage=1)
    )
    previous_step_index = run.step_index
    previous_location = (run.section, run.step, run.method)
    run.next_step()
    assert run.step_index > previous_step_index
    assert (run.section, run.step, run.method) != previous_location
    assert not run.step

    rmtree(RUNS_PATH / run_name)
