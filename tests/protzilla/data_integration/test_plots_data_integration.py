import base64
import io

import pandas as pd
import pytest
from PIL import Image

from protzilla.constants.paths import PROJECT_PATH
from protzilla.data_integration.di_plots import (
    go_enrichment_bar_plot,
    go_enrichment_dot_plot,
    gsea_dot_plot,
)


@pytest.fixture
def data_folder_tests():
    return PROJECT_PATH / "tests/test_data/enrichment_data"


def open_graph_from_base64(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    image_stream = io.BytesIO(decoded_bytes)
    image = Image.open(image_stream)
    image.show()


def test_enrichment_bar_plot_restring(show_figures, data_folder_tests):
    result = pd.read_csv(data_folder_tests / "merged_KEGG_process.csv", header=0)
    bar_base64 = go_enrichment_bar_plot(
        input_df=result,
        categories=["KEGG", "Process"],
        top_terms=10,
        cutoff=0.05,
        value="fdr",
    )
    if show_figures:
        open_graph_from_base64(bar_base64[0])

    bar_base64 = go_enrichment_bar_plot(
        input_df=result,
        categories=["KEGG", "Process"],
        top_terms=10,
        cutoff=0.05,
        value="p_value",
    )
    if show_figures:
        open_graph_from_base64(bar_base64[0])


def test_enrichment_bar_plot(show_figures, data_folder_tests):
    enrichment_df = pd.read_csv(
        data_folder_tests / "Reactome_enrichment_enrichr.csv", sep="\t"
    )
    bar_base64 = go_enrichment_bar_plot(
        input_df=enrichment_df,
        categories=["Reactome_2013"],
        top_terms=10,
        cutoff=0.05,
        value="p_value",
    )
    if show_figures:
        open_graph_from_base64(bar_base64[0])


def test_enrichment_bar_plot_wrong_value(data_folder_tests):
    enrichment_df = pd.read_csv(
        data_folder_tests / "Reactome_enrichment_enrichr.csv", sep="\t"
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


def test_enrichment_bar_plot_no_category(data_folder_tests):
    enrichment_df = pd.read_csv(
        data_folder_tests / "Reactome_enrichment_enrichr.csv", sep="\t"
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


def test_enrichment_bar_plot_cutoff(data_folder_tests):
    result = pd.read_csv(data_folder_tests / "merged_KEGG_process.csv", header=0)
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
        data_folder_tests / "Reactome_enrichment_enrichr.csv", sep="\t"
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
def test_enrichment_dot_plot(show_figures, x_axis_type, data_folder_tests):
    enrichment_df = pd.read_csv(
        data_folder_tests / "Reactome_enrichment_enrichr.csv", header=0
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
        open_graph_from_base64(dot_base64[0])


def test_enrichment_dot_plot_wrong_df(data_folder_tests):
    result = pd.read_csv(data_folder_tests / "merged_KEGG_process.csv", header=0)
    current_out = go_enrichment_dot_plot(
        input_df=result,
        categories=["KEGG", "Process"],
        top_terms=10,
        cutoff=0.05,
    )[0]

    assert "messages" in current_out
    assert "Please input a dataframe from" in current_out["messages"][0]["msg"]


def test_gsea_dot_plot(show_figures, data_folder_tests):
    enrichment_df = pd.read_csv(
        data_folder_tests / "gsea_result_sig_prot.csv", header=0
    )
    dot_base64 = gsea_dot_plot(
        input_df=enrichment_df,
        gene_sets=["KEGG_2016"],
        top_terms=10,
        cutoff=0.25,
        dot_size=3,
        title="KEGG GSEA dotplot test",
        show_ring=False,
    )[0]
    if show_figures:
        open_graph_from_base64(dot_base64["plot_base64"])


def test_gsea_dot_plot_remove_names(show_figures, data_folder_tests):
    enrichment_df = pd.read_csv(
        data_folder_tests / "gsea_preranked_enriched.csv", header=0
    )
    dot_base64 = gsea_dot_plot(
        input_df=enrichment_df,
        gene_sets=["KEGG_2016"],
        top_terms=10,
        cutoff=0.25,
        dot_size=3,
        title="KEGG GSEA dotplot test",
        show_ring=False,
        remove_library_names=True,
    )[0]
    if show_figures:
        open_graph_from_base64(dot_base64["plot_base64"])


def test_gsea_dot_plot_wrong_df(data_folder_tests):
    enrichment_df = pd.read_csv(
        data_folder_tests / "Reactome_enrichment_enrichr.csv", header=0
    )
    current_out = gsea_dot_plot(
        input_df=enrichment_df,
        top_terms=10,
        cutoff=0.25,
    )[0]

    assert "messages" in current_out
    assert "Please input a dataframe from GSEA" in current_out["messages"][0]["msg"]


def test_gsea_dot_plot_empty_df():
    df = pd.DataFrame({"NES": [], "FDR q-val": [], "lead_genes": []})
    current_out = gsea_dot_plot(
        input_df=df,
        top_terms=10,
        cutoff=0.25,
    )[0]

    assert "messages" in current_out
    assert "No data to plot" in current_out["messages"][0]["msg"]


def test_gsea_dot_plot_cutoff(data_folder_tests):
    df = pd.read_csv(data_folder_tests / "gsea_result_sig_prot.csv", header=0)
    current_out = gsea_dot_plot(
        input_df=df,
        gene_sets=["KEGG_2016"],
        top_terms=10,
        cutoff=0,
        dot_size=3,
        title="KEGG GSEA dotplot test",
    )[0]
    assert "messages" in current_out
    assert "No data to plot when applying cutoff" in current_out["messages"][0]["msg"]
