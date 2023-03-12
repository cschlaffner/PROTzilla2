from shutil import rmtree

from protzilla import data_preprocessing
from protzilla.constants.constants import PATH_TO_PROJECT, PATH_TO_RUNS
from protzilla.importing import main_data_import
from protzilla.run import Run


def test_run_create():
    # here the run should be used like in the CLI
    rmtree(PATH_TO_RUNS / "test_run", ignore_errors=True)
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


def test_run_calculate_from_location():
    rmtree(PATH_TO_RUNS / "test_run_calculate_from_location", ignore_errors=True)
    run = Run.create("test_run_calculate_from_location")
    run.perform_calculation_from_location(
        "importing",
        "main-data-import",
        "ms-data-import",
        dict(
            file=PATH_TO_PROJECT / "tests/proteinGroups_small.txt",
            intensity_name="Intensity",
        ),
    )
    run.next_step()
    run.perform_calculation_from_location(
        "data-preprocessing",
        "filter-proteins",
        "low-frequency-filter",
        dict(threshold=1),
    )
    run.create_plot_from_location(
        "data-preprocessing",
        "filter-proteins",
        "low-frequency-filter",
        dict(graph_type="Pie chart"),
    )
    run.perform_calculation_from_location(
        "data_preprocessing",
        "normalisation",
        "median",
        dict(q=0.2),
    )
    run.create_plot_from_location(
        "data_preprocessing",
        "normalisation",
        "median",
        dict(graph_type="Boxplot", group_by="Sample"),
    )
