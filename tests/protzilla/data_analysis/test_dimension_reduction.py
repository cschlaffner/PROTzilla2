import numpy as np
import pandas as pd
import pytest

from protzilla.data_analysis.dimension_reduction import t_sne, umap


@pytest.fixture
def dimension_reduction_df():
    dimension_reduction_list = (
        ["Sample1", "Protein1", "Gene1", 18],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample2", "Protein1", "Gene1", 20],
        ["Sample2", "Protein2", "Gene1", 18],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 19],
        ["Sample3", "Protein3", "Gene1", 3],
        ["Sample4", "Protein1", "Gene1", 8],
        ["Sample4", "Protein2", "Gene1", 15],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 14],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", 13],
        ["Sample6", "Protein3", "Gene1", 3],
        ["Sample7", "Protein1", "Gene1", 12],
        ["Sample7", "Protein2", "Gene1", 13],
        ["Sample7", "Protein3", "Gene1", 3],
    )

    dimension_reduction_df = pd.DataFrame(
        data=dimension_reduction_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return dimension_reduction_df


@pytest.fixture
def dimension_reduction_df_with_nan():
    dimension_reduction_list = (
        ["Sample1", "Protein1", "Gene1", 18],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample2", "Protein1", "Gene1", np.nan],
        ["Sample2", "Protein2", "Gene1", 18],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 19],
        ["Sample3", "Protein3", "Gene1", 3],
        ["Sample4", "Protein1", "Gene1", 8],
        ["Sample4", "Protein2", "Gene1", np.nan],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 14],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", 13],
        ["Sample6", "Protein3", "Gene1", 3],
        ["Sample7", "Protein1", "Gene1", 12],
        ["Sample7", "Protein2", "Gene1", 13],
        ["Sample7", "Protein3", "Gene1", 3],
    )

    dimension_reduction_df = pd.DataFrame(
        data=dimension_reduction_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return dimension_reduction_df


@pytest.fixture
def tsne_assertion_df():
    assertion_tsne_list = (
        [815.3974, 669.66266],
        [-183.04214, -1213.9768],
        [1293.7623, -86.70343],
        [-1140.1017, 220.61826],
        [-470.62607, 681.9605],
        [-78.51375, -112.844124],
        [-78.51375, -112.844124],
    )
    tsne_assertion_df = pd.DataFrame(
        data=assertion_tsne_list,
        index=[
            "Sample1",
            "Sample2",
            "Sample3",
            "Sample4",
            "Sample5",
            "Sample6",
            "Sample7",
        ],
    )
    tsne_assertion_df.index.name = "Sample"

    return tsne_assertion_df


def test_tsne_reproducibility(dimension_reduction_df, tsne_assertion_df):
    _, current_out = t_sne(
        dimension_reduction_df, n_components=2, perplexity=4, random_state=42
    )

    pd.testing.assert_frame_equal(
        current_out["embedded_data_df"], tsne_assertion_df, check_dtype=False
    )


def test_tsne_nan_handling(dimension_reduction_df_with_nan):
    _, current_out = t_sne(
        dimension_reduction_df_with_nan, n_components=2, perplexity=4
    )

    assert "messages" in current_out
    assert "NaN values" in current_out["messages"][0]["msg"]


def test_tsne_perplexity(dimension_reduction_df):
    _, current_out = t_sne(dimension_reduction_df, n_components=2, perplexity=30)
    assert "messages" in current_out
    assert (
        "Perplexity must be less than the number of samples"
        in current_out["messages"][0]["msg"]
    )


def test_tsne_n_components(dimension_reduction_df):
    _, current_out = t_sne(
        dimension_reduction_df,
        n_components=8,
        perplexity=4,
        random_state=42,
        method="exact",
    )
    assert "messages" in current_out
    assert (
        "n_components=8 must be between 1 and min(n_samples, n_features)"
        in current_out["messages"][0]["msg"]
    )


def test_tsne_n_components_barnes_hut(dimension_reduction_df):
    _, current_out = t_sne(
        dimension_reduction_df, n_components=8, perplexity=4, random_state=42
    )
    assert "messages" in current_out
    assert (
        "'n_components' should be inferior to 4 for the barnes_hut algorithm "
        "as it relies on quad-tree or oct-tree." in current_out["messages"][0]["msg"]
    )


def test_umap_reproducibility(dimension_reduction_df, tsne_assertion_df):
    _, current_out = umap(dimension_reduction_df, n_components=6)
    # fails


def test_umap_nan_handling(dimension_reduction_df_with_nan):
    _, current_out = umap(dimension_reduction_df_with_nan)
    assert "messages" in current_out
    assert "NaN values" in current_out["messages"][0]["msg"]
