import json

from protzilla import data_preprocessing
from protzilla.constants.paths import PROJECT_PATH
from protzilla.run import Run
from protzilla.utilities.random import random_string
from ui.runs.views import active_runs, all_button_parameters


def test_all_button_parameters():
    # settings.configure()
    run_name = "test_all_button_params" + random_string()
    run = Run.create(run_name)
    active_runs[run_name] = run

    data = json.loads(all_button_parameters(None, run_name).content)
    assert data["current_plot_parameters"] == dict()
    assert data["plotted_for_parameters"] == dict()
    assert data["current_parameters"] == dict()
    assert data["chosen_method"] == dict()

    parameters = {
        "intensity_name": "Intensity",
        "file_path": f"{PROJECT_PATH}/tests/proteinGroups_small_cut.txt",
    }
    run.perform_calculation_from_location(
        "importing", "ms_data_import", "max_quant_import", parameters
    )

    data = json.loads(all_button_parameters(None, run_name).content)
    print(data)

    assert data["current_plot_parameters"] == dict()
    assert data["plotted_for_parameters"] == dict()
    assert data["current_parameters"] == parameters
    assert data["chosen_method"] == "max_quant_import"

    run.next_step()

    data2 = json.loads(all_button_parameters(None, run_name).content)
    assert data2["current_plot_parameters"] == dict()
    assert data2["plotted_for_parameters"] == dict()
    assert data2["current_parameters"] == dict()
    assert data2["chosen_method"] == dict()

    parameters2 = dict(threshold=1)
    run.perform_calculation(
        data_preprocessing.filter_proteins.by_low_frequency, parameters2
    )

    plot_parameters = dict(graph_type="Pie chart")
    run.create_plot_from_location(
        "data_preprocessing", "filter_proteins", "low_frequency_filter", plot_parameters
    )

    data3 = json.loads(all_button_parameters(None, run_name).content)
    assert data3["current_plot_parameters"] == plot_parameters
    assert data3["plotted_for_parameters"] == parameters2
    assert data3["current_parameters"] == parameters2
    assert data3["chosen_method"] == "low_frequency_filter"

    parameters3 = dict(threshold=2)
    run.perform_calculation(
        data_preprocessing.filter_proteins.by_low_frequency, parameters3
    )

    data3 = json.loads(all_button_parameters(None, run_name).content)
    assert data3["current_plot_parameters"] == plot_parameters
    assert data3["plotted_for_parameters"] == parameters2
    assert data3["current_parameters"] == parameters3
    assert data3["chosen_method"] == "low_frequency_filter"
