import pandas as pd
from sklearn.cluster import KMeans
from protzilla.utilities.transform_dfs import long_to_wide


def k_means(
    intensity_df: pd.DataFrame,
    n_clusters: int = 8,
    random_state: int = None,
    max_iter: int = 300,
    tolerance: float = 1e-4,
):
    transformed_df = long_to_wide(intensity_df)
    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init="auto",
        max_iter=max_iter,
        tol=tolerance,
    )
    labels = kmeans.fit_predict(transformed_df)
    centroids = kmeans.cluster_centers_
    # Think about what should be returned as intensity_df.
    # Does it make sense to return an intensity_df?
    # THink about NaN handling
    return intensity_df, dict(centroids=centroids, labels=labels)


# Note that when we are applying k-means to real-world data using a Euclidean distance
# metric, we want to make sure that the features are measured on the same scale and
# apply z-score standardization or min-max scaling if necessary.
