import pandas as pd
from sklearn.cluster import KMeans
from protzilla.utilities.transform_dfs import long_to_wide
from django.contrib import messages


def k_means(
    intensity_df: pd.DataFrame,
    n_clusters: int = 8,
    random_state: int = None,
    init_centroid_strategy: str | list = "k-means++",
    n_init: int | str = "auto",
    max_iter: int = 300,
    tolerance: float = 1e-4,
):
    # think about n_init (initializasion strategies, how to choose centroids) and error handling?
    transformed_df = long_to_wide(intensity_df)
    try:
        if type(init_centroid_strategy) is list:
            init_centroid_strategy = transformed_df.loc[init_centroid_strategy]
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
        labels = kmeans.fit_predict(transformed_df)
        centroids = kmeans.cluster_centers_
        return intensity_df, dict(centroids=centroids, labels=labels)

    except ValueError as e:
        # is there a better way to implement this if?
        if "Input X contains NaN." in str(e):
            msg = "KMeans does not accept missing values encoded as NaN. Consider \
                preprocessing your data to remove NaN values."
            return intensity_df, dict(
                centroids=None,
                labels=None,
                messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))],
            )
        if (
            f"n_samples={transformed_df.shape[0]} should be >= n_clusters={n_clusters}."
            in str(e)
        ):
            msg = f"The number of clusters should be less or equal than the number of \
                samples. In the selected dataframe there is {transformed_df.shape[0]} \
                samples"
            return intensity_df, dict(
                centroids=None,
                labels=None,
                messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))],
            )
        # implement error handling n_clusters and init_centroid_strategyshould be
        # the same or fill dinamically?

    # Think about what should be returned as intensity_df.
    # Does it make sense to return an intensity_df?


# Note that when we are applying k-means to real-world data using a Euclidean distance
# metric, we want to make sure that the features are measured on the same scale and
# apply z-score standardization or min-max scaling if necessary.
