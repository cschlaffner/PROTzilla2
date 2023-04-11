from protzilla.run import Run
from protzilla.utilities.random import random_string
from ui.runs.views import active_runs, all_button_parameters


def test_all_button_parameters():
    run_name = "test_all_button_params" + random_string()
    run = Run.create(
        run_name, df_mode="disk", workflow_config_name="test_data_preprocessing"
    )
    active_runs[run_name] = run
    print(all_button_parameters(None, run_name))
