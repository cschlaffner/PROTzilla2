from shutil import rmtree

from protzilla import data_preprocessing
from protzilla.constants.constants import PATH_TO_PROJECT, PATH_TO_RUNS
from protzilla.importing import main_data_import
from protzilla.run import Run


def test_run_create():
    # here the run should be used like in the CLI
    rmtree(PATH_TO_RUNS / "test_run")
    run = Run.create("test_run")
    run.calculate_and_next(
        main_data_import.max_quant_import,
        file=PATH_TO_PROJECT / "tests/proteinGroups_small_cut.txt",
        intensity_name="Intensity",
    )
    run.calculate_and_next(
        data_preprocessing.filter_proteins.by_low_frequency, threshold=1
    )
    run.calculate_and_next(
        data_preprocessing.filter_samples.by_protein_intensity_sum, threshold=1
    )
    # print([s.outputs for s in run.history.steps])
    # to get a history that can be used to create a worklow, the section, step, method
    # should be set by calculate_and_next


def test_run_back():
    rmtree(PATH_TO_RUNS / "test_run_back", ignore_errors=True)
    run = Run.create("test_run_back")
    run.calculate_and_next(
        main_data_import.max_quant_import,
        file=PATH_TO_PROJECT / "tests/proteinGroups_small_cut.txt",
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


# think more about different run interfaces
# CLI: steps, complete workflow
# UI: location, back+next, workflow defaults
# different classes?


def test_run_continue():
    run_name = "test_run_continue"
    rmtree(PATH_TO_RUNS / run_name)
    run = Run.create(run_name, df_mode="disk")
    run.calculate_and_next(
        main_data_import.max_quant_import,
        file=PATH_TO_PROJECT / "tests/proteinGroups_small_cut.txt",
        intensity_name="Intensity",
    )
    df = run.df
    del run
    run2 = Run.continue_existing(run_name)
    assert df.equals(run2.df)
