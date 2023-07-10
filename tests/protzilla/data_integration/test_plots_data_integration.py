import json

import pandas as pd
import pytest

from protzilla.constants.paths import PROJECT_PATH
from protzilla.data_integration.di_plots import (
    GO_enrichment_bar_plot,
    GO_enrichment_dot_plot,
    gsea_dot_plot,
    gsea_enrichment_plot,
)


@pytest.fixture
def data_folder_tests():
    return PROJECT_PATH / "tests/test_data/enrichment_data"


def test_enrichment_bar_plot_restring(show_figures, helpers):
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    result = pd.read_csv(f"{test_data_folder}/merged_KEGG_process.csv", header=0)
    bar_base64 = GO_enrichment_bar_plot(
        input_df=result,
        top_terms=10,
        cutoff=0.05,
        value="fdr",
        categories=["KEGG", "Process"],
    )
    if show_figures:
        helpers.open_graph_from_base64(bar_base64[0])

    bar_base64 = GO_enrichment_bar_plot(
        input_df=result,
        top_terms=10,
        cutoff=0.05,
        value="p_value",
        categories=["KEGG", "Process"],
    )
    if show_figures:
        helpers.open_graph_from_base64(bar_base64[0])


def test_enrichment_bar_plot(show_figures, helpers, data_folder_tests):
    enrichment_df = pd.read_csv(
        data_folder_tests / "Reactome_enrichment_enrichr.csv", sep="\t"
    )
    bar_base64 = GO_enrichment_bar_plot(
        input_df=enrichment_df,
        top_terms=10,
        cutoff=0.05,
        value="p_value",
        categories=["Reactome_2013"],
    )
    if show_figures:
        helpers.open_graph_from_base64(bar_base64[0])


def test_enrichment_bar_plot_wrong_value(data_folder_tests):
    enrichment_df = pd.read_csv(
        data_folder_tests / "Reactome_enrichment_enrichr.csv", sep="\t"
    )
    current_out = GO_enrichment_bar_plot(
        input_df=enrichment_df,
        top_terms=10,
        cutoff=0.05,
        value="fdr",
        categories=["Reactome_2013"],
    )[0]
    assert "messages" in current_out
    assert "FDR is not available" in current_out["messages"][0]["msg"]


def test_enrichment_bar_plot_empty_df():
    empty_df = pd.DataFrame()
    current_out = GO_enrichment_bar_plot(
        input_df=empty_df,
        top_terms=10,
        cutoff=0.05,
        value="p_value",
        categories=["Reactome_2013"],
    )[0]
    assert "messages" in current_out
    assert "No data to plot" in current_out["messages"][0]["msg"]


def test_enrichment_bar_plot_no_category(data_folder_tests):
    enrichment_df = pd.read_csv(
        data_folder_tests / "Reactome_enrichment_enrichr.csv", sep="\t"
    )
    current_out = GO_enrichment_bar_plot(
        input_df=enrichment_df,
        top_terms=10,
        cutoff=0.05,
        value="p_value",
        categories=[],
    )[0]
    assert "messages" in current_out
    assert "Please select at least one category" in current_out["messages"][0]["msg"]


def test_enrichment_bar_plot_wrong_df():
    enrichment_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    current_out = GO_enrichment_bar_plot(
        input_df=enrichment_df,
        top_terms=10,
        cutoff=0.05,
        value="p_value",
        categories=["KEGG"],
    )[0]
    assert "messages" in current_out
    assert (
        "Please choose an enrichment result dataframe"
        in current_out["messages"][0]["msg"]
    )


def test_enrichment_bar_plot_cutoff(data_folder_tests):
    result = pd.read_csv(data_folder_tests / "merged_KEGG_process.csv", header=0)
    current_out = GO_enrichment_bar_plot(
        input_df=result,
        top_terms=10,
        cutoff=0,
        value="fdr",
        categories=["KEGG", "Process"],
    )[0]

    assert "messages" in current_out
    assert "No data to plot when applying cutoff" in current_out["messages"][0]["msg"]

    enrichment_df = pd.read_csv(
        data_folder_tests / "Reactome_enrichment_enrichr.csv", sep="\t"
    )
    current_out = GO_enrichment_bar_plot(
        input_df=enrichment_df,
        top_terms=10,
        cutoff=0,
        value="p_value",
        categories=["Reactome_2013"],
    )[0]
    assert "messages" in current_out
    assert "No data to plot when applying cutoff" in current_out["messages"][0]["msg"]


@pytest.mark.parametrize("x_axis_type", ["Gene Sets", "Combined Score"])
def test_GO_enrichment_dot_plot(helpers, show_figures, x_axis_type, data_folder_tests):
    enrichment_df = pd.read_csv(
        data_folder_tests / "Reactome_enrichment_enrichr.csv", header=0, sep="\t"
    )
    dot_base64 = GO_enrichment_dot_plot(
        input_df=enrichment_df,
        top_terms=5,
        cutoff=0.05,
        categories=["Reactome_2013"],
        x_axis_type=x_axis_type,
        title="Reactome Enrichment Test",
        rotate_x_labels=False,
        show_ring=False,
        dot_size=40,
    )[0]
    if show_figures:
        helpers.open_graph_from_base64(dot_base64["plot_base64"])


def test_enrichment_dot_plot_wrong_df(data_folder_tests):
    result = pd.read_csv(data_folder_tests / "merged_KEGG_process.csv", header=0)
    current_out = GO_enrichment_dot_plot(
        input_df=result, top_terms=10, cutoff=0.05, categories=["KEGG", "Process"]
    )[0]

    assert "messages" in current_out
    assert "Please input a dataframe from" in current_out["messages"][0]["msg"]


def test_gsea_dot_plot(show_figures, data_folder_tests, helpers):
    enrichment_df = pd.read_csv(
        data_folder_tests / "gsea_result_sig_prot.csv", header=0
    )
    dot_base64 = gsea_dot_plot(
        input_df=enrichment_df,
        gene_sets=["KEGG_2016"],
        cutoff=0.25,
        dot_size=3,
        title="KEGG GSEA dotplot test",
        show_ring=False,
    )[0]
    if show_figures:
        helpers.open_graph_from_base64(dot_base64["plot_base64"])


def test_gsea_dot_plot_remove_names(show_figures, data_folder_tests, helpers):
    enrichment_df = pd.read_csv(
        data_folder_tests / "gsea_preranked_enriched.csv", header=0
    )
    dot_base64 = gsea_dot_plot(
        input_df=enrichment_df,
        gene_sets=["KEGG_2019"],
        cutoff=1,
        dot_size=3,
        title="KEGG GSEA dotplot test",
        show_ring=False,
        remove_library_names=True,
    )[0]
    if show_figures:
        helpers.open_graph_from_base64(dot_base64["plot_base64"])


def test_gsea_dot_plot_wrong_df(data_folder_tests):
    enrichment_df = pd.read_csv(
        data_folder_tests / "Reactome_enrichment_enrichr.csv", header=0
    )
    current_out = gsea_dot_plot(
        input_df=enrichment_df,
        cutoff=0.25,
    )[0]

    assert "messages" in current_out
    assert "Please input a dataframe from GSEA" in current_out["messages"][0]["msg"]


def test_gsea_dot_plot_empty_df():
    df = pd.DataFrame({"NES": [], "FDR q-val": [], "lead_genes": []})
    current_out = gsea_dot_plot(
        input_df=df,
        cutoff=0.25,
    )[0]

    assert "messages" in current_out
    assert "No data to plot" in current_out["messages"][0]["msg"]


def test_gsea_dot_plot_cutoff(data_folder_tests):
    df = pd.read_csv(data_folder_tests / "gsea_result_sig_prot.csv", header=0)
    current_out = gsea_dot_plot(
        input_df=df,
        gene_sets=["KEGG_2016"],
        cutoff=0,
        dot_size=3,
        title="KEGG GSEA dotplot test",
    )[0]
    assert "messages" in current_out
    assert "No data to plot when applying cutoff" in current_out["messages"][0]["msg"]


def test_gsea_dot_plot_gene_sets(data_folder_tests, helpers, show_figures):
    df = pd.read_csv(data_folder_tests / "gsea_result_sig_prot.csv", header=0)
    dot_base64 = gsea_dot_plot(
        input_df=df,
        gene_sets="KEGG_2016",
        cutoff=0.25,
        dot_size=3,
        title="KEGG GSEA dotplot test",
    )[0]
    if show_figures:
        helpers.open_graph_from_base64(dot_base64["plot_base64"])

    dot_base64 = gsea_dot_plot(
        input_df=df,
        gene_sets="all",
        cutoff=0.25,
        dot_size=3,
        title="KEGG GSEA dotplot test",
    )[0]
    if show_figures:
        helpers.open_graph_from_base64(dot_base64["plot_base64"])


def test_gsea_enrichment_plot(data_folder_tests, helpers, show_figures):
    ranking = pd.Series(
        sorted([i / 41 for i in range(42)], reverse=True)
    )  # mock ranking
    ranking.index.name = "Gene symbol"
    with open(data_folder_tests / "KEGG_2015__alzheimers disease.json") as json_file:
        enrichment_details = json.load(json_file)

    enrichment_plot = gsea_enrichment_plot(
        term_dict=enrichment_details,
        term_name="KEGG_2015__alzheimers disease",
        ranking=ranking,
    )[0]
    if show_figures:
        helpers.open_graph_from_base64(enrichment_plot["plot_base64"])


def test_gsea_enrichment_plot_wrong_term_dict():
    current_out = gsea_enrichment_plot(
        term_dict=dict(awrongdictkey="wrongdictvalue"),
    )[0]
    assert "messages" in current_out
    assert (
        "Please input a dictionary with enrichment details"
        in current_out["messages"][0]["msg"]
    )


def test_gsea_enrichment_plot_no_term_name():
    current_out = gsea_enrichment_plot(
        term_dict=dict(nes=0),
        term_name="",
    )[0]
    assert "messages" in current_out
    assert "Please input a term name" in current_out["messages"][0]["msg"]


def test_gsea_enrichment_plot_wrong_ranking(data_folder_tests):
    ranking = pd.Series(sorted([i / 41 for i in range(42)]))  # mock ranking
    ranking.index.name = "wrongindexname"
    with open(data_folder_tests / "KEGG_2015__alzheimers disease.json") as json_file:
        enrichment_details = json.load(json_file)

    current_out = gsea_enrichment_plot(
        term_dict=enrichment_details,
        term_name="KEGG_2015__alzheimers disease",
        ranking=ranking,
    )[0]
    assert "messages" in current_out
    assert (
        "Please input a ranking output dataframe" in current_out["messages"][0]["msg"]
    )


def test_gsea_enrichment_plot_fails(data_folder_tests):
    ranking = pd.Series(
        sorted([i / 41 for i in range(42)], reverse=True)
    )  # mock ranking
    ranking.index.name = "Gene symbol"
    ranking = ranking[:-1]  # drop last row to make it fail because of size mismatch
    with open(data_folder_tests / "KEGG_2015__alzheimers disease.json") as json_file:
        enrichment_details = json.load(json_file)

    current_out = gsea_enrichment_plot(
        term_dict=enrichment_details,
        term_name="KEGG_2015__alzheimers disease",
        ranking=ranking,
    )[0]
    assert "messages" in current_out
    assert "Could not plot enrichment" in current_out["messages"][0]["msg"]
