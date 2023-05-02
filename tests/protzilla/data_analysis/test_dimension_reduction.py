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
def dimension_reduction_four_proteins_df():
    dimension_reduction_list = (
        ["Sample1", "Protein1", "Gene1", 18],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample1", "Protein4", "Gene1", 13],
        ["Sample1", "Protein5", "Gene1", 13],
        ["Sample2", "Protein1", "Gene1", 20],
        ["Sample2", "Protein2", "Gene1", 18],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample2", "Protein4", "Gene1", 4],
        ["Sample2", "Protein5", "Gene1", 13],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 19],
        ["Sample3", "Protein3", "Gene1", 3],
        ["Sample3", "Protein4", "Gene1", 7],
        ["Sample3", "Protein5", "Gene1", 13],
        ["Sample4", "Protein1", "Gene1", 8],
        ["Sample4", "Protein2", "Gene1", 15],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample4", "Protein4", "Gene1", 7],
        ["Sample4", "Protein5", "Gene1", 13],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 14],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample5", "Protein4", "Gene1", 8],
        ["Sample5", "Protein5", "Gene1", 13],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", 13],
        ["Sample6", "Protein3", "Gene1", 3],
        ["Sample6", "Protein4", "Gene1", 3],
        ["Sample6", "Protein5", "Gene1", 13],
        ["Sample7", "Protein1", "Gene1", 12],
        ["Sample7", "Protein2", "Gene1", 13],
        ["Sample7", "Protein3", "Gene1", 3],
        ["Sample7", "Protein4", "Gene1", 10],
        ["Sample7", "Protein5", "Gene1", 13],
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


@pytest.fixture
def umap_assertion_df():
    assertion_umap_list = (
        [22.050823, 5.450951],
        [22.405716, 5.8017206],
        [21.766651, 5.1627417],
        [4.2950587, 3.7172985],
        [4.787037, 3.20218],
        [5.1595345, 4.0933995],
        [5.458093, 3.3993974],
    )

    umap_assertion_df = pd.DataFrame(
        data=assertion_umap_list,
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
    umap_assertion_df.index.name = "Sample"

    return umap_assertion_df


# TODO: find out why tsne is not reproducible even-though random_state is set
# def test_tsne_reproducibility(dimension_reduction_df, tsne_assertion_df):
#     _, current_out = t_sne(
#         pd.DataFrame(),  # Remove when intensity_df is removed
#         dimension_reduction_df,
#         n_components=2,
#         perplexity=4,
#         random_state=42,
#     )
#
#     pd.testing.assert_frame_equal(
#         current_out["embedded_data_df"], tsne_assertion_df, check_dtype=False
#     )


def test_tsne_nan_handling(df_with_nan):
    current_out = t_sne(
        df_with_nan,
        n_components=2,
        perplexity=4,
    )

    assert "messages" in current_out
    assert "NaN values" in current_out["messages"][0]["msg"]


def test_tsne_perplexity(dimension_reduction_df):
    current_out = t_sne(
        dimension_reduction_df,
        n_components=2,
        perplexity=30,
    )
    assert "messages" in current_out
    assert (
        "Perplexity must be less than the number of samples"
        in current_out["messages"][0]["msg"]
    )


def test_tsne_n_components(dimension_reduction_df):
    current_out = t_sne(
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


def test_tsne_n_components_barnes_hut(dimension_reduction_four_proteins_df):
    current_out = t_sne(
        dimension_reduction_four_proteins_df,
        n_components=4,
        perplexity=4,
        random_state=42,
    )
    assert "messages" in current_out
    assert (
        "'n_components' should be inferior to 4 for the barnes_hut algorithm "
        "as it relies on quad-tree or oct-tree." in current_out["messages"][0]["msg"]
    )


# TODO: find out why umap is not reproducible eventhough random_state is set
# def test_umap_reproducibility(dimension_reduction_df, umap_assertion_df):
#     _, current_out = umap(
#         pd.DataFrame(),  # Remove when intensity_df is removed
#         dimension_reduction_df,
#         n_components=2,
#         n_neighbors=3,
#         random_state=42,
#         transform_seed=42,
#     )
#     pd.testing.assert_frame_equal(
#         current_out["embedded_data_df"], umap_assertion_df, check_dtype=False
#     )


def test_umap_nan_handling(df_with_nan):
    current_out = umap(
        df_with_nan,
    )
    assert "messages" in current_out
    assert "NaN values" in current_out["messages"][0]["msg"]
