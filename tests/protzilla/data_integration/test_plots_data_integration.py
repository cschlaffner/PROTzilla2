import base64
import io
import pytest

import pandas as pd
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


@pytest.mark.parametrize("x_axis", ["Gene Sets", "Combined Score"])
def test_enrichment_dot_plot(show_figures, x_axis):
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    enrichment_df = pd.read_csv(
        f"{test_data_folder}/Reactome_enrichment_enrichr.csv", header=0
    )
    bar_base64 = go_enrichment_dot_plot(
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
        open_graph_from_base64(bar_base64[0])
