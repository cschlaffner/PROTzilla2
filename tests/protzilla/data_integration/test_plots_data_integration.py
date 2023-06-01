import base64
import io

import pandas as pd
import pytest
from PIL import Image

from protzilla.constants.paths import PROJECT_PATH
from protzilla.data_integration.di_plots import (
    go_enrichment_bar_plot,
    go_enrichment_dot_plot,
)


def open_graph_from_base64(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    image_stream = io.BytesIO(decoded_bytes)
    image = Image.open(image_stream)
    image.show()


def test_enrichment_bar_plot_restring(show_figures):
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    result = pd.read_csv(f"{test_data_folder}/merged_results.csv", header=0)
    bar_base64 = go_enrichment_bar_plot(
        input_df=result,
        categories=["KEGG", "Process"],
        top_terms=10,
        cutoff=0.05,
    )
    if show_figures:
        open_graph_from_base64(bar_base64[0])

    summary = pd.read_csv(f"{test_data_folder}/merged_summaries.csv", header=0)
    bar_base64 = go_enrichment_bar_plot(
        input_df=summary,
        categories=["KEGG", "Process"],
        top_terms=10,
        cutoff=0.05,
    )
    if show_figures:
        open_graph_from_base64(bar_base64[0])


def test_enrichment_bar_plot(show_figures):
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    enrichment_df = pd.read_csv(
        f"{test_data_folder}/Reactome_enrichment_enrichr.csv", header=0
    )
    bar_base64 = go_enrichment_bar_plot(
        input_df=enrichment_df,
        categories=["Reactome_2013"],
        top_terms=10,
        cutoff=0.05,
    )
    if show_figures:
        open_graph_from_base64(bar_base64[0])


def test_enrichment_bar_plot_empty_df():
    empty_df = pd.DataFrame()
    current_out = go_enrichment_bar_plot(
        input_df=empty_df,
        categories=["Reactome_2013"],
        top_terms=10,
        cutoff=0.05,
    )[0]
    assert "messages" in current_out
    assert "No data to plot" in current_out["messages"][0]["msg"]


def test_enrichment_bar_plot_no_category():
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    enrichment_df = pd.read_csv(
        f"{test_data_folder}/Reactome_enrichment_enrichr.csv", header=0
    )
    current_out = go_enrichment_bar_plot(
        input_df=enrichment_df,
        categories=[],
        top_terms=10,
        cutoff=0.05,
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
    )[0]
    assert "messages" in current_out
    assert (
        "Please choose an enrichment result dataframe"
        in current_out["messages"][0]["msg"]
    )


def test_enrichment_bar_plot_cutoff():
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    result = pd.read_csv(f"{test_data_folder}/merged_results.csv", header=0)
    current_out = go_enrichment_bar_plot(
        input_df=result,
        categories=["KEGG", "Process"],
        top_terms=10,
        cutoff=0,
    )[0]

    assert "messages" in current_out
    assert "No data to plot when applying cutoff" in current_out["messages"][0]["msg"]

    enrichment_df = pd.read_csv(
        f"{test_data_folder}/Reactome_enrichment_enrichr.csv", header=0
    )
    current_out = go_enrichment_bar_plot(
        input_df=enrichment_df,
        categories=["Reactome_2013"],
        top_terms=10,
        cutoff=0,
    )[0]
    assert "messages" in current_out
    assert "No data to plot when applying cutoff" in current_out["messages"][0]["msg"]


@pytest.mark.parametrize("x_axis", ["Gene Sets", "Combined Score"])
def test_enrichment_dot_plot(show_figures, x_axis):
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    enrichment_df = pd.read_csv(
        f"{test_data_folder}/Reactome_enrichment_enrichr.csv", header=0
    )
    dot_base64 = go_enrichment_dot_plot(
        input_df=enrichment_df,
        categories=["Reactome_2013"],
        x_axis=x_axis,
        top_terms=5,
        cutoff=0.05,
        dot_size=40,
        title="Reactome Enrichment Test",
        rotate_x_labels=False,
        show_ring=False,
    )
    if show_figures:
        open_graph_from_base64(dot_base64[0])


def test_enrichment_bar_plot_wrong_df():
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    result = pd.read_csv(f"{test_data_folder}/merged_results.csv", header=0)
    current_out = go_enrichment_dot_plot(
        input_df=result,
        categories=["KEGG", "Process"],
        top_terms=10,
        cutoff=0.05,
    )[0]

    assert "messages" in current_out
    assert "Please input a dataframe from" in current_out["messages"][0]["msg"]
