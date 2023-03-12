from protzilla.run import Run
from shutil import rmtree
from protzilla.constants.constants import PATH_TO_RUNS, PATH_TO_PROJECT
from protzilla import data_preprocessing

# no idea why this is necessary
from protzilla.importing import main_data_import


def test_run_create():
    # here the run should be used like in the CLI
    # add an option to get the data from a csv df file
    rmtree(PATH_TO_RUNS / "test_run")
    run = Run.create("test_run")
    run.calculate_and_next(
        main_data_import.max_quant_import,
        file=PATH_TO_PROJECT / "tests/proteinGroups_small.txt",
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
        file=PATH_TO_PROJECT / "tests/proteinGroups_small.txt",
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
    rmtree(PATH_TO_RUNS / "test_plotting", ignore_errors=True)
    run = Run.create("test_plotting")
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
