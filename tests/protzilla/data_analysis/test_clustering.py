import numpy as np
import pandas as pd
import pytest

from protzilla.data_analysis.clustering import (
    expectation_maximisation,
    hierarchical_agglomerative_clustering,
    k_means,
)


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


@pytest.fixture
def meta_df():
    meta_list = (
        ["Sample1", "AD"],
        ["Sample2", "AD"],
        ["Sample3", "AD"],
        ["Sample4", "CTR"],
        ["Sample5", "CTR"],
        ["Sample6", "CTR"],
        ["Sample7", "CTR"],
    )
    meta_df = pd.DataFrame(
        data=meta_list,
        columns=["Sample", "Group"],
    )

    return meta_df


def test_k_means(clustering_df, meta_df):
    centroids_assertion = [[10.5, 13.75, 2.25], [20.0, 17.666666666666668, 2.0]]
    cluster_labels_df_assertion = pd.DataFrame(
        {
            "Sample": [
                "Sample1",
                "Sample2",
                "Sample3",
                "Sample4",
                "Sample5",
                "Sample6",
                "Sample7",
            ],
            "Cluster Labels": [1, 1, 1, 0, 0, 0, 0],
        }
    )
    current_out = k_means(
        input_df=clustering_df,
        metadata_df=meta_df,
        labels_column="Group",
        positive_label="AD",
        model_selection="Manual",
        scoring=["completeness_score"],
        n_clusters=2,
        random_state=6,
        init_centroid_strategy="random",
        n_init=10,
        max_iter=300,
        tolerance=1e-4,
    )

    pd.testing.assert_frame_equal(
        current_out["cluster_labels_df"],
        cluster_labels_df_assertion,
        check_names=False,
        check_dtype=False,
    )

    np.array_equal(centroids_assertion, current_out["model"].cluster_centers_)


def test_k_means_nan_handling(df_with_nan, meta_df):
    current_out = k_means(
        input_df=df_with_nan,
        metadata_df=meta_df,
        labels_column="Group",
        positive_label="AD",
        model_selection="Manual",
        scoring=["completeness_score"],
        n_clusters=4,
        init_centroid_strategy="k-means++",
    )
    assert "messages" in current_out
    assert "NaN values" in current_out["messages"][0]["msg"]


def test_k_means_n_clusters(clustering_df, meta_df):
    current_out = k_means(
        input_df=clustering_df,
        metadata_df=meta_df,
        labels_column="Group",
        positive_label="AD",
        model_selection="Manual",
        scoring=["completeness_score"],
        n_clusters=10,
        init_centroid_strategy="k-means++",
    )
    assert "messages" in current_out
    assert (
        "The number of clusters should be less or equal than the number of samples."
        in current_out["messages"][0]["msg"]
    )


def test_expectation_maximisation(clustering_df, meta_df):
    cluster_labels_df_assertion = pd.DataFrame(
        {
            "Sample": [
                "Sample1",
                "Sample2",
                "Sample3",
                "Sample4",
                "Sample5",
                "Sample6",
                "Sample7",
            ],
            "Cluster Labels": [0, 0, 0, 0, 0, 0, 0],
        }
    )
    cluster_labels_probabilities_df_assertion = pd.DataFrame(
        {
            "Sample": [
                "Sample1",
                "Sample2",
                "Sample3",
                "Sample4",
                "Sample5",
                "Sample6",
                "Sample7",
            ],
            0: [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        }
    )
    current_out = expectation_maximisation(
        clustering_df, meta_df, "Group", "AD", "Manual"
    )

    pd.testing.assert_frame_equal(
        current_out["cluster_labels_df"],
        cluster_labels_df_assertion,
        check_names=False,
        check_dtype=False,
    )
    pd.testing.assert_frame_equal(
        current_out["cluster_labels_probabilities_df"],
        cluster_labels_probabilities_df_assertion,
        check_names=False,
        check_dtype=False,
    )


def test_hierarchical_agglomerative_clustering(clustering_df, meta_df):
    current_out = hierarchical_agglomerative_clustering(
        input_df=clustering_df,
        metadata_df=meta_df,
        labels_column="Group",
        positive_label="AD",
        model_selection="Manual",
    )
    cluster_labels_df_assertion = pd.DataFrame(
        {
            "Sample": [
                "Sample1",
                "Sample2",
                "Sample3",
                "Sample4",
                "Sample5",
                "Sample6",
                "Sample7",
            ],
            "Cluster Labels": [1, 1, 1, 0, 0, 0, 0],
        }
    )
    pd.testing.assert_frame_equal(
        current_out["cluster_labels_df"],
        cluster_labels_df_assertion,
        check_names=False,
        check_dtype=False,
    )
