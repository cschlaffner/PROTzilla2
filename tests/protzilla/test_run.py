from shutil import rmtree

from protzilla import data_preprocessing
from protzilla.constants.paths import PROJECT_PATH, RUNS_PATH
from protzilla.importing import ms_data_import
from protzilla.run import Run
from protzilla.utilities.random import random_string


def test_run_create():
    # here the run should be used like in the CLI
    name = "test_run" + random_string()
    run = Run.create(name)
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        # call with str to make json serializable
        file=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
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
        file=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
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


# think more about different run interfaces
# CLI: steps, complete workflow
# UI: location, back+next, workflow defaults
# different classes?


def test_run_continue():
    run_name = "test_run_continue" + random_string()
    run = Run.create(run_name, df_mode="disk")
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        file=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
        intensity_name="Intensity",
    )
    df = run.df
    del run
    run2 = Run.continue_existing(run_name)
    assert df.equals(run2.df)
    rmtree(RUNS_PATH / run_name)

def test_perform_calculation_logging(caplog):
    run_name = "test_run_logging" + random_string()
    run = Run.create(run_name, df_mode="disk")
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        file=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
        intensity_name="Intensity",
    )

    run.perform_calculation_from_location("data_preprocessing", 
                                          "outlier_detection", 
                                          "local_outlier_factor", 
                                          {"number_of_neighbors": 3})
    
    assert "ERROR" in caplog.text
    assert "Outlier Detection with LocalOutlierFactor does not accept missing values"\
        "encoded as NaN. Consider preprocessing your data to remove NaN values." in caplog.text
    rmtree(RUNS_PATH / run_name)