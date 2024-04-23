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
    method_inputs = {
        "protein_df": outlier_detection_df,
        "n_estimators": 50,
        "n_jobs": -1,
    }
    method_outputs = by_isolation_forest(**method_inputs)
    fig = by_isolation_forest_plot(method_inputs, method_outputs)[0]
    if show_figures:
        fig.show()


def test_outlier_detection_with_isolation_forest_and_nan(outlier_detection_df_with_nan):
    method_inputs = {
        "protein_df": outlier_detection_df_with_nan,
        "n_estimators": 50,
        "n_jobs": -1,
    }
    methtod_outputs = by_isolation_forest(**method_inputs)

    assert "messages" in methtod_outputs
    assert "NaN values" in methtod_outputs["messages"][0]["msg"]


def test_outlier_detection_by_local_outlier_factor(show_figures, outlier_detection_df):
    method_inputs = {
        "protein_df": outlier_detection_df,
        "number_of_neighbors": 35,
        "n_jobs": -1,
    }
    method_outputs = by_local_outlier_factor(**method_inputs)
    fig = by_local_outlier_factor_plot(method_inputs, method_outputs)[0]
    if show_figures:
        fig.show()


def test_outlier_detection_by_local_outlier_factor_and_nan(
    outlier_detection_df_with_nan,
):
    method_inputs = {
        "protein_df": outlier_detection_df_with_nan,
        "number_of_neighbors": 35,
        "n_jobs": -1,
    }
    method_outputs = by_local_outlier_factor(**method_inputs)

    assert "messages" in method_outputs
    assert "NaN values" in method_outputs["messages"][0]["msg"]


def test_outlier_detection_with_pca(show_figures, outlier_detection_df):
    method_inputs = {
        "protein_df": outlier_detection_df,
        "threshold": 2,
        "number_of_components": 3,
    }
    method_outputs = by_pca(**method_inputs)
    fig = by_pca_plot(method_inputs, method_outputs)[0]
    if show_figures:
        fig.show()


def test_outlier_detection_with_pca_and_nan(outlier_detection_df_with_nan):
    method_inputs = {
        "protein_df": outlier_detection_df_with_nan,
        "threshold": 2,
        "number_of_components": 3,
    }
    method_outputs = by_pca(**method_inputs)

    assert "messages" in method_outputs
    assert "NaN values" in method_outputs["messages"][0]["msg"]
