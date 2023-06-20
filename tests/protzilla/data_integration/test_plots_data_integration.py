import pandas as pd
import pytest

from protzilla.constants.paths import PROJECT_PATH
from protzilla.data_integration.di_plots import (
    go_enrichment_bar_plot,
    go_enrichment_dot_plot,
)


def test_enrichment_bar_plot_restring(show_figures, helpers):
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    result = pd.read_csv(f"{test_data_folder}/merged_KEGG_process.csv", header=0)
    bar_base64 = go_enrichment_bar_plot(
        input_df=result,
        categories=["KEGG", "Process"],
        top_terms=10,
        cutoff=0.05,
        value="fdr",
    )
    if show_figures:
        helpers.open_graph_from_base64(bar_base64[0])

    bar_base64 = go_enrichment_bar_plot(
        input_df=result,
        categories=["KEGG", "Process"],
        top_terms=10,
        cutoff=0.05,
        value="p_value",
    )
    if show_figures:
        helpers.open_graph_from_base64(bar_base64[0])


def test_enrichment_bar_plot(show_figures, helpers):
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    enrichment_df = pd.read_csv(
        f"{test_data_folder}/Reactome_enrichment_enrichr.csv", sep="\t"
    )
    bar_base64 = go_enrichment_bar_plot(
        input_df=enrichment_df,
        categories=["Reactome_2013"],
        top_terms=10,
        cutoff=0.05,
        value="p_value",
    )
    if show_figures:
        helpers.open_graph_from_base64(bar_base64[0])


def test_enrichment_bar_plot_wrong_value():
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    enrichment_df = pd.read_csv(
        f"{test_data_folder}/Reactome_enrichment_enrichr.csv", sep="\t"
    )
    current_out = go_enrichment_bar_plot(
        input_df=enrichment_df,
        categories=["Reactome_2013"],
        top_terms=10,
        cutoff=0.05,
        value="fdr",
    )[0]
    assert "messages" in current_out
    assert "FDR is not available" in current_out["messages"][0]["msg"]


def test_enrichment_bar_plot_empty_df():
    empty_df = pd.DataFrame()
    current_out = go_enrichment_bar_plot(
        input_df=empty_df,
        categories=["Reactome_2013"],
        top_terms=10,
        cutoff=0.05,
        value="p_value",
    )[0]
    assert "messages" in current_out
    assert "No data to plot" in current_out["messages"][0]["msg"]


def test_enrichment_bar_plot_no_category():
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    enrichment_df = pd.read_csv(
        f"{test_data_folder}/Reactome_enrichment_enrichr.csv", sep="\t"
    )
    current_out = go_enrichment_bar_plot(
        input_df=enrichment_df,
        categories=[],
        top_terms=10,
        cutoff=0.05,
        value="p_value",
    )[0]
    assert "messages" in current_out
    assert "Please select at least one category" in current_out["messages"][0]["msg"]


def test_enrichment_bar_plot_wrong_df():
    enrichment_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    current_out = go_enrichment_bar_plot(
        input_df=enrichment_df,
        categories=["KEGG"],
        top_terms=10,
        cutoff=0.05,
        value="p_value",
    )[0]
    assert "messages" in current_out
    assert (
        "Please choose an enrichment result dataframe"
        in current_out["messages"][0]["msg"]
    )


def test_enrichment_bar_plot_cutoff():
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    result = pd.read_csv(f"{test_data_folder}/merged_KEGG_process.csv", header=0)
    current_out = go_enrichment_bar_plot(
        input_df=result,
        categories=["KEGG", "Process"],
        top_terms=10,
        cutoff=0,
        value="fdr",
    )[0]

    assert "messages" in current_out
    assert "No data to plot when applying cutoff" in current_out["messages"][0]["msg"]

    enrichment_df = pd.read_csv(
        f"{test_data_folder}/Reactome_enrichment_enrichr.csv", sep="\t"
    )
    current_out = go_enrichment_bar_plot(
        input_df=enrichment_df,
        categories=["Reactome_2013"],
        top_terms=10,
        cutoff=0,
        value="p_value",
    )[0]
    assert "messages" in current_out
    assert "No data to plot when applying cutoff" in current_out["messages"][0]["msg"]


@pytest.mark.parametrize("x_axis_type", ["Gene Sets", "Combined Score"])
def test_enrichment_dot_plot(
    helpers,
    show_figures,
    x_axis_type,
):
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    enrichment_df = pd.read_csv(
        f"{test_data_folder}/Reactome_enrichment_enrichr.csv", header=0
    )
    dot_base64 = go_enrichment_dot_plot(
        input_df=enrichment_df,
        categories=["Reactome_2013"],
        x_axis_type=x_axis_type,
        top_terms=5,
        cutoff=0.05,
        dot_size=40,
        title="Reactome Enrichment Test",
        rotate_x_labels=False,
        show_ring=False,
    )
    if show_figures:
        helpers.open_graph_from_base64(dot_base64[0])


def test_enrichment_dot_plot_wrong_df():
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    result = pd.read_csv(f"{test_data_folder}/merged_KEGG_process.csv", header=0)
    current_out = go_enrichment_dot_plot(
        input_df=result,
        categories=["KEGG", "Process"],
        top_terms=10,
        cutoff=0.05,
    )[0]

    assert "messages" in current_out
    assert "Please input a dataframe from" in current_out["messages"][0]["msg"]
