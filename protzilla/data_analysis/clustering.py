import pandas as pd
from django.contrib import messages
from sklearn.cluster import KMeans

from protzilla.utilities.transform_dfs import is_long_format, long_to_wide


def k_means(
    intensity_df: pd.DataFrame,
    input_df: pd.DataFrame,
    n_clusters: int = 8,
    random_state: int = 6,
    init_centroid_strategy: str = "random",
    n_init: int = 10,
    max_iter: int = 300,
    tolerance: float = 1e-4,
):
    """
    A method that uses k-means to partition a number of samples in k clusters. The \
    function returns a dataframe with the corresponding cluster of each point and \
    another dataframe with the coordinates of the cluster centers.

    :param input_df: the dataframe that should be clustered in wide or long format
    :type input_df: pd.DataFrame
    :param n_clusters: the number of clusters to form as well as the number of \
    centroids to generate.
    :type n_clusters: int
    :param random_state: Determines random number generation for centroid initialization
    :type random_state: int
    :param init_centroid_strategy: method for centroid initialization
    :type init_centroid_strategy: str
    :param n_init: Number of times the k-means algorithm is run with different centroid\
     seeds.
    :type n_init: int
    :param max_iter: Maximum number of iterations of the k-means algorithm for a single\
     run.
    :type max_iter: int
    :param tolerance: Relative tolerance with regards to Frobenius norm of the \
    difference in the cluster centers of two consecutive iterations to declare\
     convergence.
    :type tolerance: float
    """
    intensity_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    try:
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
        centroids = kmeans.cluster_centers_.tolist()
        return intensity_df, dict(centroids=centroids, labels_df=labels_df)

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
        else:
            msg = ""
        return intensity_df, dict(
            centroids=None,
            labels=None,
            messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))],
        )


# Note that when we are applying k-means to real-world data using a Euclidean distance
# metric, we want to make sure that the features are measured on the same scale and
# apply z-score standardization or min-max scaling if necessary.
