import numpy as np
import pandas as pd
import pytest

from protzilla.data_analysis.clustering import k_means


@pytest.fixture
def clustering_df():
    clustering_list = (
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

    clustering_df = pd.DataFrame(
        data=clustering_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return clustering_df


def test_k_means(clustering_df):
    centroids_assertion = [[10.5, 13.75, 2.25], [20.0, 17.666666666666668, 2.0]]
    cluster_labels_df_assertion = pd.DataFrame(
        data=(
            ["Cluster 1"],
            ["Cluster 1"],
            ["Cluster 1"],
            ["Cluster 0"],
            ["Cluster 0"],
            ["Cluster 0"],
            ["Cluster 0"],
        ),
        index=[
            "Sample1",
            "Sample2",
            "Sample3",
            "Sample4",
            "Sample5",
            "Sample6",
            "Sample7",
        ],
        columns=["Cluster Labels"],
    )
    _, current_out = k_means(
        pd.DataFrame(),  # Remove when intensity_df is removed
        clustering_df,
        n_clusters=2,
        random_state=6,
        init_centroid_strategy="random",
        n_init=10,
        max_iter=300,
        tolerance=1e-4,
    )

    pd.testing.assert_frame_equal(
        current_out["cluster_labels_df"], cluster_labels_df_assertion, check_names=False
    )
    assert centroids_assertion == current_out["centroids"]


def test_k_means_nan_handling(df_with_nan):
    _, current_out = k_means(
        pd.DataFrame(),  # Remove when intensity_df is removed
        df_with_nan,
        n_clusters=4,
        init_centroid_strategy="k-means++",
    )
    assert "messages" in current_out
    assert "NaN values" in current_out["messages"][0]["msg"]


def test_k_means_n_clusters(clustering_df):
    _, current_out = k_means(
        pd.DataFrame(),  # Remove when intensity_df is removed
        clustering_df,
        n_clusters=10,
        init_centroid_strategy="k-means++",
    )
    assert "messages" in current_out
    assert (
        "The number of clusters should be less or equal than the number of samples."
        in current_out["messages"][0]["msg"]
    )
