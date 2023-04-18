import pandas as pd
from sklearn.cluster import KMeans
from protzilla.utilities.transform_dfs import long_to_wide, is_long_format
from django.contrib import messages


def k_means(
    input_df: pd.DataFrame,
    n_clusters: int = 8,
    random_state: int = 6,
    init_centroid_strategy: str | list = "random",
    n_init: int = 10,
    max_iter: int = 300,
    tolerance: float = 1e-4,
):
    intensity_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    try:
        if type(init_centroid_strategy) is list:
            init_centroid_strategy = intensity_df_wide.loc[init_centroid_strategy]
            # The sklearn methods fails to set n_init=1 when the user enters
            # n_init="auto" and the centroid seeds (init_centroid_strategy) manually as
            # a pd.Dataframe
            if n_init == "auto":
                n_init = 1
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            init=init_centroid_strategy,
            n_init=n_init,
            max_iter=max_iter,
            tol=tolerance,
        )
        labels = kmeans.fit_predict(intensity_df_wide)
        labels_df = pd.DataFrame(labels, index=intensity_df_wide.index)
        centroids = kmeans.cluster_centers_
        return input_df, dict(centroids=centroids, labels_df=labels_df)

    except ValueError as e:
        if intensity_df_wide.isnull().sum().any():
            msg = (
                "KMeans does not accept missing values encoded as NaN. Consider"
                "preprocessing your data to remove NaN values."
            )
        elif intensity_df_wide.shape[0] < n_clusters:
            msg = (
                f"The number of clusters should be less or equal than the number of "
                f"samples. In the selected dataframe there is {intensity_df_wide.shape[0]}"
                f"samples"
            )
        elif init_centroid_strategy.shape[0] != n_clusters:
            msg = (
                f"The number of clusters {n_clusters} should match the number of "
                f"chosen centroids {init_centroid_strategy.shape[0]}"
            )
        else:
            msg = ""
        return input_df, dict(
            centroids=None,
            labels=None,
            messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))],
        )


# Note that when we are applying k-means to real-world data using a Euclidean distance
# metric, we want to make sure that the features are measured on the same scale and
# apply z-score standardization or min-max scaling if necessary.
