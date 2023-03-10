from shutil import rmtree

from protzilla.constants.constants import PATH_TO_PROJECT, PATH_TO_RUNS
from protzilla.run import Run


def test_plotting():
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
        dict(graph_type="Pie Chart"),
    )
