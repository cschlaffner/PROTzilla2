import numpy as np
import pytest

from protzilla.data_analysis.plots import *
from tests.protzilla.data_analysis.test_clustering import *


@pytest.fixture
def wide_2d_df():
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
def wide_3d_df():
    return pd.DataFrame(
        np.array(
            [
                [4, 10, 3],
                [8, 2, 4],
                [2, 7, 1],
                [13, 5, 7],
            ]
        ),
        columns=["Protein1", "Protein2", "Protein3"],
        index=["Sample1", "Sample2", "Sample3", "Sample4"],
    )


@pytest.fixture
def wide_4d_df():
    return pd.DataFrame(
        np.array(
            [
                [4, 10, 3, 2],
                [8, 2, 4, 7],
                [2, 7, 1, 4],
                [13, 5, 7, 1],
            ]
        ),
        columns=["Protein1", "Protein2", "Protein3", "Protein4"],
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


def test_scatter_plot_2d(show_figures, wide_2d_df, color_df):
    fig = scatter_plot(wide_2d_df, color_df)[0]
    if show_figures:
        fig.show()
    return


def test_scatter_plot_no_color_df(show_figures, wide_2d_df):
    fig = scatter_plot(wide_2d_df)[0]
    if show_figures:
        fig.show()
    return


def test_scatter_plot_3d(show_figures, wide_3d_df, color_df):
    fig = scatter_plot(wide_3d_df, color_df)[0]
    if show_figures:
        fig.show()
    return


def test_scatter_plot_4d_df(wide_4d_df, color_df):
    result = scatter_plot(wide_4d_df, color_df)

    assert any(isinstance(p, dict) for p in result)
    assert "Consider reducing the dimensionality" in result[0]["messages"][0]["msg"]


def test_scatter_plot_color_df_2d(show_figures, wide_2d_df):
    result = scatter_plot(wide_2d_df, wide_2d_df)
    assert any(isinstance(p, dict) for p in result)
    assert (
        "The color dataframe should have 1 dimension only"
        in result[0]["messages"][0]["msg"]
    )


def test_clustergram(show_figures, wide_4d_df, color_df):
    fig = clustergram_plot(wide_4d_df, color_df, "no")[0]
    if show_figures:
        fig.show()
    return


def test_prot_quant_plot(show_figures, wide_4d_df):
    fig = prot_quant_plot(wide_4d_df, "")[0]
    if show_figures:
        fig.show()
    return


def test_clustergram_no_sample_group_df(show_figures, wide_4d_df):
    fig = clustergram_plot(wide_4d_df, "", "no")[0]
    if show_figures:
        fig.show()
    return


def test_clustergram_input_not_right_type(wide_4d_df):
    result1 = clustergram_plot([1, 2, 3, 4, 5], "", "no")
    result2 = clustergram_plot(wide_4d_df, [1, 2, 3, 4, 5], "no")
    assert any(isinstance(p, dict) for p in result1)
    assert (
        'The selected input for "input dataframe" is not a dataframe'
        in result1[0]["messages"][0]["msg"]
    )
    assert any(isinstance(p, dict) for p in result2)
    assert (
        'The selected input for "grouping dataframe" is not a dataframe, '
        in result2[0]["messages"][0]["msg"]
    )


def test_clustergram_dimension_mismatch(wide_4d_df):
    sample_group_df_5_samples = pd.DataFrame(
        np.array(
            [
                [4, 10, 3],
                [8, 2, 4],
                [2, 7, 1],
                [13, 5, 7],
                [13, 3, 9],
            ]
        ),
        columns=["Protein1", "Protein2", "Protein3"],
        index=["Sample1", "Sample2", "Sample3", "Sample4", "Sample5"],
    )
    result = clustergram_plot(
        wide_4d_df,
        sample_group_df_5_samples,
        "no",
    )
    assert any(isinstance(p, dict) for p in result)
    assert "There is a dimension mismatch" in result[0]["messages"][0]["msg"]


def test_clustergram_different_samples(wide_4d_df):
    sample_group_df_different_samples = pd.DataFrame(
        np.array(
            [
                [4, 10, 3],
                [8, 2, 4],
                [2, 7, 1],
                [13, 5, 7],
            ]
        ),
        columns=["Protein1", "Protein2", "Protein3"],
        index=["Sample1", "Sample2", "Sample5", "Sample4"],
    )
    result = clustergram_plot(
        wide_4d_df,
        sample_group_df_different_samples,
        "no",
    )
    assert any(isinstance(p, dict) for p in result)
    assert (
        "The input dataframe and the grouping contain different samples"
        in result[0]["messages"][0]["msg"]
    )
