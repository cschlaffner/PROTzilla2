import numpy as np
import pandas as pd
import pytest

from protzilla.data_preprocessing.outlier_detection import (
    by_isolation_forest,
    by_isolation_forest_plot,
    by_local_outlier_factor,
    by_local_outlier_factor_plot,
    by_pca,
    by_pca_plot,
)

# TODO #21: implement actual tests for outlier detection


@pytest.fixture
def outlier_detection_df():
    outlier_detection_df = (
        ["Sample1", "Protein1", "Gene1", 5],
        ["Sample1", "Protein2", "Gene2", 2],
        ["Sample1", "Protein3", "Gene3", 4],
        ["Sample2", "Protein1", "Gene1", 1],
        ["Sample2", "Protein2", "Gene2", 3],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 50],
        ["Sample3", "Protein3", "Gene3", 80],
    )

    outlier_detection_df = pd.DataFrame(
        data=outlier_detection_df,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return outlier_detection_df


@pytest.fixture
def outlier_detection_df_with_nan():
    outlier_detection_df = (
        ["Sample1", "Protein1", "Gene1", np.nan],
        ["Sample1", "Protein2", "Gene2", 2],
        ["Sample1", "Protein3", "Gene3", np.nan],
        ["Sample2", "Protein1", "Gene1", np.nan],
        ["Sample2", "Protein2", "Gene2", 3],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", np.nan],
        ["Sample3", "Protein3", "Gene3", 80],
    )

    outlier_detection_df = pd.DataFrame(
        data=outlier_detection_df,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return outlier_detection_df


def test_outlier_detection_with_isolation_forest(show_figures, outlier_detection_df):
    result_df, dropouts = by_isolation_forest(outlier_detection_df, 50, -1)
    fig = by_isolation_forest_plot(outlier_detection_df, result_df, dropouts)[0]
    if show_figures:
        fig.show()


def test_outlier_detection_with_isolation_forest_and_nan(outlier_detection_df_with_nan):
    _, current_out = by_isolation_forest(outlier_detection_df_with_nan, 50, -1)

    assert "messages" in current_out
    assert "NaN values" in current_out["messages"][0]["msg"]


def test_outlier_detection_by_local_outlier_factor(show_figures, outlier_detection_df):
    result_df, dropouts = by_local_outlier_factor(outlier_detection_df, 35, -1)
    fig = by_local_outlier_factor_plot(outlier_detection_df, result_df, dropouts)[0]
    if show_figures:
        fig.show()


def test_outlier_detection_by_local_outlier_factor_and_nan(
    outlier_detection_df_with_nan,
):
    _, current_out = by_local_outlier_factor(outlier_detection_df_with_nan, 35, -1)

    assert "messages" in current_out
    assert "NaN values" in current_out["messages"][0]["msg"]


def test_outlier_detection_with_pca(show_figures, outlier_detection_df):
    result_df, dropouts = by_pca(outlier_detection_df, 2, 3)
    fig = by_pca_plot(outlier_detection_df, result_df, dropouts)[0]
    if show_figures:
        fig.show()


def test_outlier_detection_with_pca_and_nan(outlier_detection_df_with_nan):
    _, current_out = by_pca(outlier_detection_df_with_nan, 2, 3)

    assert "messages" in current_out
    assert "NaN values" in current_out["messages"][0]["msg"]