import json
import sys
from shutil import rmtree

from protzilla.constants.paths import UI_PATH

sys.path.append(f"{UI_PATH}")

from protzilla import data_preprocessing
from protzilla.constants.paths import PROJECT_PATH, RUNS_PATH
from protzilla.run_v2 import Run
from protzilla.utilities import random_string
from ui.runs.views import active_runs, all_button_parameters


def assert_response(
    run_name,
    current_plot_parameters,
    plotted_for_parameters,
    current_parameters,
    chosen_method,
):
    data = json.loads(all_button_parameters(None, run_name).content)
    assert data["current_plot_parameters"] == current_plot_parameters
    assert data["plotted_for_parameters"] == plotted_for_parameters
    assert data["current_parameters"] == current_parameters
    assert data["chosen_method"] == chosen_method


def test_all_button_parameters():
    run_name = "test_all_button_params" + random_string()
    run = Run.create(run_name)
    active_runs[run_name] = run

    assert_response(
        run_name,
        current_plot_parameters=dict(),
        plotted_for_parameters=dict(),
        current_parameters=dict(),
        chosen_method=dict(),
    )

    parameters = {
        "intensity_name": "Intensity",
        "file_path": f"{PROJECT_PATH}/tests/proteinGroups_small_cut.txt",
    }
    run.perform_calculation_from_location(
        "importing", "ms_data_import", "max_quant_import", parameters
    )

    assert_response(
        run_name,
        current_plot_parameters=dict(),
        plotted_for_parameters=dict(),
        current_parameters=parameters,
        chosen_method="max_quant_import",
    )

    run.next_step()
    run.step_index = 2

    assert_response(
        run_name,
        current_plot_parameters=dict(),
        plotted_for_parameters=dict(),
        current_parameters=dict(),
        chosen_method=dict(),
    )

    parameters2 = dict(percentage=1)
    run.perform_calculation(
        data_preprocessing.filter_proteins.by_samples_missing, parameters2
    )

    plot_parameters = dict(graph_type="Pie chart")
    run.create_plot_from_current_location(plot_parameters)

    assert_response(
        run_name,
        current_plot_parameters=plot_parameters,
        plotted_for_parameters=parameters2,
        current_parameters=parameters2,
        chosen_method="samples_missing_filter",
    )

    parameters3 = dict(percentage=2)
    run.perform_calculation(
        data_preprocessing.filter_proteins.by_samples_missing, parameters3
    )

    assert_response(
        run_name,
        current_plot_parameters=plot_parameters,
        plotted_for_parameters=parameters2,
        current_parameters=parameters3,
        chosen_method="samples_missing_filter",
    )

    run.next_step()
    run.back_step()

    assert_response(
        run_name,
        current_plot_parameters=dict(),
        plotted_for_parameters=dict(),
        current_parameters=parameters3,
        chosen_method="samples_missing_filter",
    )

    rmtree(RUNS_PATH / run_name)


def test_step_finished():
    run_name = "test_step_finished" + random_string()
    run = Run.create(run_name)
    active_runs[run_name] = run

    assert not run.current_step.finished

    parameters = {
        "file_path": f"{PROJECT_PATH}/tests/proteinGroups_small_cut.txt",
        "intensity_name": "Intensity",
    }
    run.perform_calculation_from_location(
        "importing", "ms_data_import", "max_quant_import", parameters
    )

    assert run.current_step.finished

    run.next_step()
    run.step_index = 1

    assert not run.current_step.finished

    parameters = {
        "file_path": f"",
        "feature_orientation": "Columns (samples in rows, features in columns)",
    }
    run.perform_calculation_from_location(
        "importing", "metadata_import", "metadata_import_method", parameters
    )

    assert not run.current_step.finished

    parameters = {
        "file_path": f"{PROJECT_PATH}/tests/nonexistent_file.txt",
        "feature_orientation": "Columns (samples in rows, features in columns)",
    }
    run.perform_calculation_from_location(
        "importing", "metadata_import", "metadata_import_method", parameters
    )

    assert not run.current_step.finished

    parameters = {
        "file_path": f"{PROJECT_PATH}/tests/metadata_cut_columns.csv",
        "feature_orientation": "Columns (samples in rows, features in columns)",
    }
    run.perform_calculation_from_location(
        "importing", "metadata_import", "metadata_import_method", parameters
    )

    assert run.current_step.finished

    rmtree(RUNS_PATH / run_name)
