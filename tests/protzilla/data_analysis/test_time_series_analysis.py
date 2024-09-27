import pandas as pd
import pytest

from protzilla.data_analysis.time_series_regression_analysis import (
    time_series_linear_regression,
    time_series_ransac_regression,
    adfuller_test,
    time_series_auto_arima,
    time_series_arima,
)


@pytest.fixture
def time_series_test_data():
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 20],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample1", "Protein4", "Gene1", 14],
        ["Sample2", "Protein1", "Gene1", 20],
        ["Sample2", "Protein2", "Gene1", 15],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample2", "Protein4", "Gene1", 15],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 14],
        ["Sample3", "Protein3", "Gene1", 3],
        ["Sample3", "Protein4", "Gene1", 16],
        ["Sample4", "Protein1", "Gene1", 8],
        ["Sample4", "Protein2", "Gene1", 15],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample4", "Protein4", "Gene1", 9],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 14],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample5", "Protein4", "Gene1", 10],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", 13],
        ["Sample6", "Protein3", "Gene1", 3],
        ["Sample6", "Protein4", "Gene1", 11],
        ["Sample7", "Protein1", "Gene1", 12],
        ["Sample7", "Protein2", "Gene1", 13],
        ["Sample7", "Protein3", "Gene1", 3],
        ["Sample7", "Protein4", "Gene1", 11],
        ["Sample1", "Protein1", "Gene2", 10],
        ["Sample1", "Protein2", "Gene2", 14],
        ["Sample1", "Protein3", "Gene2", 2],
        ["Sample1", "Protein4", "Gene2", 10],
        ["Sample2", "Protein1", "Gene2", 12],
        ["Sample2", "Protein1", "Gene3", 13],

    )

    test_intensity_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    test_metadata_df = (
        ["Sample1", "2", "1"],
        ["Sample2", "6", "1"],
        ["Sample3", "7", "1"],
         ["Sample4", "8", "1"],
        ["Sample5", "2", "2"],
        ["Sample6", "6", "2"],
        ["Sample7", "7", "2"],
    )
    test_metadata_df = pd.DataFrame(
        data=test_metadata_df,
        columns=["Sample", "Time", "Group"],
    )
    return test_intensity_df, test_metadata_df

def test_linear_regression_plot_with_grouping(show_figures, time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs = time_series_linear_regression(
        test_intensity,
        test_metadata,
        "Time",
        0.8,
        "Protein1",
        "Group",
        "With Grouping"
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return

def test_linear_regression_plot_without_grouping(show_figures, time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs = time_series_linear_regression(
        test_intensity,
        test_metadata,
        "Time",
        0.8,
        "Protein1",
        "With Grouping",
        "Group",
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return

def test_linear_regression_plot_invalid_train_size(time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    with pytest.raises(ValueError):
        time_series_linear_regression(
            test_intensity,
            test_metadata,
            "Time",
            2,
            "Protein1",
            "With Grouping",
            "Group",
        )
    return

def test_linear_regression_outputs(time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs = time_series_linear_regression(
        test_intensity,
        test_metadata,
        "Time",
        0.8,
        "Protein1",
        "With Grouping",
        "Group",
    )
    assert "scores" in outputs
    return


def test_ransac_regression_plot_with_grouping(show_figures, time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs = time_series_ransac_regression(
        test_intensity,
        test_metadata,
        "Time",
        "Protein1",
        100,
        0.99,
        "absolute_error",
        0.8,
        "With Grouping",
        "Group",
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return

def test_ransac_regression_plot_without_grouping(show_figures, time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs = time_series_ransac_regression(
        test_intensity,
        test_metadata,
        "Time",
        "Protein1",
        100,
        0.99,
        "absolute_error",
        0.8,
        "With Grouping",
        "Group",

    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return

def test_ransac_plot_invalid_train_size(time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    with pytest.raises(ValueError):
        time_series_ransac_regression(
            test_intensity,
            test_metadata,
            "Time",
            "Protein1",
            100,
            0.99,
            "absolute_error",
            2,
            "With Grouping",
            "Group",
        )
    return

def test_ransac_regression_outputs(time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs = time_series_ransac_regression(
        test_intensity,
        test_metadata,
        "Time",
        "Protein1",
        100,
        0.99,
        "absolute_error",
        0.8,
        "With Grouping",
        "Group",
    )
    assert "scores" in outputs
    return


def test_adfuller_test(time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs = adfuller_test(test_intensity, test_metadata, "Time", "Protein1")

    assert "test_statistic" in outputs
    assert "p_value" in outputs
    assert "critical_values" in outputs
    assert "is_stationary" in outputs
    assert "messages" in outputs
    return


def test_auto_arima_plot_with_grouping(show_figures, time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs = time_series_auto_arima(
        test_intensity,
        test_metadata,
        "Time",
        "Protein1",
        "No",
        1,
        0.5,
        "With Grouping",
        "Group",
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return

def test_auto_arima_plot_without_grouping(show_figures, time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs =  time_series_auto_arima(
        test_intensity,
        test_metadata,
        "Time",
        "Protein1",
        "No",
        1,
        0.5,
        "With Grouping",
        "Group",
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return

def test_auto_arima_plot_invalid_train_size(time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    with pytest.raises(ValueError):
        time_series_auto_arima(
            test_intensity,
            test_metadata,
            "Time",
            "Protein1",
            "No",
            1,
            2,
            "With Grouping",
            "Group",
        )
    return


def test_auto_arima_outputs(time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs =  time_series_auto_arima(
        test_intensity,
        test_metadata,
        "Time",
        "Protein1",
        "No",
        1,
        0.5,
        "With Grouping",
        "Group",
    )
    assert "scores" in outputs
    return


def test_arima_plot_with_grouping(show_figures, time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs = time_series_arima(
        test_intensity,
        test_metadata,
        "Time",
        "Protein1",
        "No",
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        0.5,
        "With Grouping",
        "Group",
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return

def test_arima_plot_seasonal_with_grouping(show_figures, time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs = time_series_arima(
        test_intensity,
        test_metadata,
        "Time",
        "Protein1",
        "No",
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        0.5,
        "With Grouping",
        "Group",
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return

def test_arima_plot_without_grouping(show_figures, time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs = time_series_arima(
        test_intensity,
        test_metadata,
        "Time",
        "Protein1",
        "No",
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        0.5,
        "With Grouping",
        "Group",
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return

def test_arima_plot_invalid_train_size(time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    with pytest.raises(ValueError):
        time_series_arima(
            test_intensity,
            test_metadata,
            "Time",
            "Protein1",
            "No",
            1,
            1,
            1,
            0,
            0,
            0,
            0,
            2,
            "With Grouping",
            "Group",
        )
    return


def test_arima_outputs(time_series_test_data):
    test_intensity, test_metadata = time_series_test_data
    outputs = time_series_arima(
        test_intensity,
        test_metadata,
        "Time",
        "Protein1",
        "No",
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        0.5,
        "With Grouping",
        "Group",
    )
    assert "scores" in outputs
    return