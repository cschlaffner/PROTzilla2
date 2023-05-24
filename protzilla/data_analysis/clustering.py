import pandas as pd
from django.contrib import messages
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import GridSearchCV

from protzilla.utilities.transform_dfs import is_long_format, long_to_wide


def k_means(
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
    :param init_centroid_strategy: method for centroid initialization. Possible methods\
     are: k-means++ and random
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
    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    try:
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            init=init_centroid_strategy,
            n_init=n_init,
            max_iter=max_iter,
            tol=tolerance,
        )
        labels = kmeans.fit_predict(input_df_wide)
        cluster_labels_df = pd.DataFrame(
            labels, index=input_df_wide.index, columns=["Cluster Labels"]
        )
        cluster_labels_df["Cluster Labels"] = cluster_labels_df["Cluster Labels"].apply(
            lambda x: f"Cluster {x}"
        )
        centroids = kmeans.cluster_centers_.tolist()
        return dict(centroids=centroids, cluster_labels_df=cluster_labels_df)

    except ValueError as e:
        if input_df_wide.isnull().sum().any():
            msg = (
                "KMeans does not accept missing values encoded as NaN. Consider"
                "preprocessing your data to remove NaN values."
            )
        elif input_df_wide.shape[0] < n_clusters:
            msg = (
                f"The number of clusters should be less or equal than the number of "
                f"samples. In the selected dataframe there is {input_df_wide.shape[0]}"
                f"samples"
            )
        else:
            msg = ""
        return dict(
            centroids=None,
            labels=None,
            messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))],
        )


def gmm_bic_score(estimator, X):
    """Callable to pass to GridSearchCV that will use the BIC score."""
    # Make it negative since GridSearchCV expects a score to maximize
    return -estimator.bic(X)


def expectation_maximisation(
    input_df: pd.DataFrame,
    model_selection: bool,
    n_components: int,
    covariance_type: str,
    init_params: str,
    max_iter: int,
):
    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    try:
        if model_selection:
            param_grid = {
                "n_components": n_components,
                "covariance_type": covariance_type,
                "init_params": init_params,
                "max_iter": max_iter,
            }
            grid_search = GridSearchCV(
                GaussianMixture(), param_grid=param_grid, scoring=gmm_bic_score
            )
            # GridSearchCV searches for the model with the best score
            grid_search.fit(input_df_wide)
            # The best model found is called on the data
            labels = grid_search.predict(input_df_wide)
            return dict(
                model=grid_search.best_estimator_,
                labels=labels,
            )
        else:
            model = GaussianMixture(
                n_components=n_components,
                covariance_type=covariance_type,
                init_params=init_params,
                max_iter=max_iter,
            )
            labels = model.fit_predict(input_df_wide)
            return dict(
                model=model,
                labels=labels,
            )
    except:
        pass
