from protzilla.data_analysis.plots import *
from tests.protzilla.data_analysis.test_clustering import *
import pytest


@pytest.fixture
def wide_df():
    return pd.DataFrame(
        np.array(
            [
                [4, 10],
                [8, 2],
                [2, 7],
                [13, 5],
            ]
        ),
        columns=["Protein1", "Protein2"],
        index=["Sample1", "Sample2", "Sample3", "Sample4"],
    )


@pytest.fixture
def color_df():
    return pd.DataFrame(
        np.array(
            [
                ["Color1"],
                ["Color2"],
                ["Color1"],
                ["Color1"],
            ]
        ),
        columns=["Color"],
        index=["Sample1", "Sample2", "Sample3", "Sample4"],
    )


def test_scatter_plot_2d(wide_df, color_df, show_figures=True):
    fig = scatter_plot_2d(wide_df, color_df)
    if show_figures:
        fig.show()
    return
