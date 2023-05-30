import pandas as pd
from django.contrib import messages
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

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


def perform_grid_search(grid_search_model, model, param_grid: dict, scoring, cv=None):
    if grid_search_model == "Grid search":
        clf = GridSearchCV(model, param_grid=param_grid, scoring=scoring)
    elif grid_search_model == "Randomized search":
        clf = RandomizedSearchCV(model, param_distributions=param_grid, scoring=scoring)
    return clf


def gmm_bic_score(estimator, X):
    """Callable to pass to GridSearchCV that will use the BIC score."""
    # Make it negative since GridSearchCV expects a score to maximize
    return -estimator.bic(X)


def expectation_maximisation(
    input_df: pd.DataFrame,
    model_selection: str = "Grid search",
    n_components: int = 1,
    covariance_type: str = "full",
    init_params: str = "kmeans",
    max_iter: int = 100,
):
    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    try:
        if model_selection == "Manual":
            clf = GaussianMixture(
                n_components=n_components,
                covariance_type=covariance_type,
                init_params=init_params,
                max_iter=max_iter,
            )
            clf.fit(input_df_wide)
            model_parameters = clf.get_params()
            model_evaluation_df = pd.DataFrame(model_parameters, index=[0])
            model_evaluation_df = model_evaluation_df[
                ["n_components", "covariance_type", "init_params", "max_iter"]
            ]
            model_evaluation_df = model_evaluation_df.rename(
                columns={
                    "n_components": "Number of components",
                    "covariance_type": "Type of covariance",
                    "init_params": "Initialisation parameters",
                    "max_iter": "Maximum Number of Iterations",
                }
            )
            model_evaluation_df.insert(4, "BIC Score", [clf.bic(input_df_wide)], True)
        else:
            param_grid = {
                "n_components": [n_components, 3],
                "covariance_type": [covariance_type],
                "init_params": [init_params],
                "max_iter": [max_iter],
            }
            clf = perform_grid_search(
                model_selection,
                GaussianMixture(),
                param_grid=param_grid,
                scoring=gmm_bic_score,
            )
            clf.fit(input_df_wide)
            model_evaluation_df = pd.DataFrame(clf.cv_results_)[
                [
                    "param_n_components",
                    "param_covariance_type",
                    "param_init_params",
                    "param_max_iter",
                    "mean_test_score",
                ]
            ]
            model_evaluation_df["mean_test_score"] = -model_evaluation_df[
                "mean_test_score"
            ]
            model_evaluation_df = model_evaluation_df.rename(
                columns={
                    "param_n_components": "Number of components",
                    "param_covariance_type": "Type of covariance",
                    "param_init_params": "Initialisation parameters",
                    "param_max_iter": "Maximum Number of Iterations",
                    "mean_test_score": "BIC Score",
                }
            )
            model_evaluation_df.sort_values(by="BIC Score").head()
            model_parameters = clf.best_params_

        class_probabilities = pd.DataFrame(
            data=clf.predict_proba(input_df_wide), index=input_df_wide.index
        )
        labels = pd.DataFrame(
            data=clf.predict(input_df_wide),
            index=input_df_wide.index,
            columns=["Cluster Labels"],
        )
        return dict(
            model_parameters=model_parameters,
            class_probabilities_df=class_probabilities,
            labels=labels,
        )
    except Exception as e:
        return dict(messages="")
