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
    run.prepare_calculation("max_quant_import")
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        # call with str to make json serializable
        file=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
        intensity_name="Intensity",
    )
    run.prepare_calculation("filter_proteins")
    run.calculate_and_next(
        data_preprocessing.filter_proteins.by_low_frequency, threshold=1
    )
    run.prepare_calculation("filter_samples")
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

    run.prepare_calculation("max_quant_import")
    run.perform_calculation(
        ms_data_import.max_quant_import,
        parameters={
            # call with str to make json serializable
            "file": str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
            "intensity_name": "Intensity",
        },
    )
    df1 = run.result_df
    run.next_step()

    run.prepare_calculation("filter_proteins")
    assert run.input_data.equals(df1)
    run.perform_calculation(
        data_preprocessing.filter_proteins.by_low_frequency, parameters={"threshold": 1}
    )
    df2 = run.result_df
    run.next_step()

    assert not df1.equals(df2)
    run.back_step()
    assert run.input_data.equals(df1)
    run.back_step()
    assert run.input_data is None
    rmtree(RUNS_PATH / name)


# think more about different run interfaces
# CLI: steps, complete workflow
# UI: location, back+next, workflow defaults
# different classes?


def test_run_continue():
    run_name = "test_run_continue" + random_string()
    run = Run.create(run_name, df_mode="disk")

    run.prepare_calculation("max_quant_import")
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        # call with str to make json serializable
        file=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
        intensity_name="Intensity",
    )

    run.prepare_calculation("filter_proteins")
    run.perform_calculation(
        data_preprocessing.filter_proteins.by_low_frequency, parameters={"threshold": 1}
    )
    df = run.input_data
    run.next_step()

    del run
    
    # run will be continued from beginning of last step
    run2 = Run.continue_existing(run_name)
    assert df.equals(run2.input_data)
    rmtree(RUNS_PATH / run_name)


def test_insert_as_next_step():
    # TODO: not ready
    run_name = "test_insert_as_next_step" + random_string()
    run = Run.create(run_name, df_mode="disk")
    run.calculate_and_next(
        ms_data_import.max_quant_import,
        file=str(PROJECT_PATH / "tests/proteinGroups_small_cut.txt"),
        intensity_name="Intensity",
    )
    print("\n\n", run)
