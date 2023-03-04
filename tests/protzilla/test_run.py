from protzilla.run import Run
from shutil import rmtree
from protzilla.constants.constants import PATH_TO_RUNS
from protzilla import data_preprocessing
import pandas as pd


def test_run_create():
    # here the run should be used like in the CLI
    # add an option to get the data from a csv df file

    rmtree(PATH_TO_RUNS / "test_run")
    r = Run.create("test_run")

    # r.calculate_and_next(
    #     data_preprocessing.filter_samples.by_protein_intensity_sum, threshold=1
    # )
    # to get a history that can be used to create a worklow, the section, step, method
    # should be set by calculate_and_next


# think more about different run interfaces
# CLI: steps, complete workflow
# UI: location, back+next, workflow defaults
# different classes?
