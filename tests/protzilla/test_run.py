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
    r = Run.create("test_run")
    r.calculate_and_next(
        main_data_import.max_quant_import,
        file=PATH_TO_PROJECT / "tests/proteinGroups_small.txt",
        intensity_name="Intensity",
    )
    r.calculate_and_next(
        data_preprocessing.filter_proteins.by_low_frequency, threshold=1
    )
    r.calculate_and_next(
        data_preprocessing.filter_samples.by_protein_intensity_sum, threshold=1
    )
    print([s.outputs for s in r.history.steps])
    # to get a history that can be used to create a worklow, the section, step, method
    # should be set by calculate_and_next


# think more about different run interfaces
# CLI: steps, complete workflow
# UI: location, back+next, workflow defaults
# different classes?
