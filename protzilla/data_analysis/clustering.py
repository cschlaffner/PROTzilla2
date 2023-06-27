import pandas as pd
from django.contrib import messages
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.mixture import GaussianMixture

from protzilla.data_analysis.classification_helper import (
    perform_grid_search_cv,
    create_dict_with_lists_as_values,
    create_model_evaluation_df_grid_search,
    evaluate_clustering_with_scoring,
    create_model_evaluation_df_grid_search_manual,
    encode_labels,
)
from protzilla.utilities.transform_dfs import is_long_format, long_to_wide


def k_means(
    input_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    labels_column: str,
    positive_label: str = None,
    model_selection: str = "Grid search",
    scoring: list[str] = ["completeness_score"],
    n_clusters: int = 8,
    random_state: int = 6,
    init_centroid_strategy: str = "random",
    n_init: int = 10,
    max_iter: int = 300,
    tolerance: float = 1e-4,
    **kwargs,
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
        input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
        input_df_wide.sort_values(by="Sample", inplace=True)
        labels_df = (
            metadata_df[["Sample", labels_column]]
            .set_index("Sample")
            .sort_values(by="Sample")
        )

        encoding_mapping, labels_df = encode_labels(
            labels_df, labels_column, positive_label
        )

        clf = KMeans()

        clf_parameters = dict(
            n_clusters=n_clusters,
            random_state=random_state,
            init=init_centroid_strategy,
            n_init=n_init,
            max_iter=max_iter,
            tol=tolerance,
        )

        scoring = [scoring] if isinstance(scoring, str) else scoring

        model, model_evaluation_df = perform_clustering(
            input_df_wide,
            model_selection,
            clf,
            clf_parameters,
            scoring,
            labels_df=labels_df["Encoded Label"],
            **kwargs,
        )
        cluster_labels_df = pd.DataFrame(
            {"Sample": input_df_wide.index, "Cluster Labels": model.labels_}
        )
        cluster_centers_df = (
            pd.DataFrame(data=model.cluster_centers_, columns=input_df_wide.columns)
            .transpose()
            .reset_index()
        )
        return dict(
            model=model,
            model_evaluation_df=model_evaluation_df,
            cluster_labels_df=cluster_labels_df,
            cluster_centers_df=cluster_centers_df,
        )
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


def expectation_maximisation(
    input_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    labels_column: str,
    positive_label: str = None,
    model_selection: str = "Grid search",
    scoring: list[str] = ["completeness_score"],
    n_components: int = 1,
    covariance_type: str = "full",
    reg_covar: float = 1e-6,
    init_params: str = "kmeans",
    max_iter: int = 100,
    random_state=42,
    **kwargs,
):
    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    input_df_wide.sort_values(by="Sample", inplace=True)
    labels_df = (
        metadata_df[["Sample", labels_column]]
        .set_index("Sample")
        .sort_values(by="Sample")
    )
    encoding_mapping, labels_df = encode_labels(
        labels_df, labels_column, positive_label
    )

    clf = GaussianMixture()

    clf_parameters = dict(
        n_components=n_components,
        covariance_type=covariance_type,
        init_params=init_params,
        max_iter=max_iter,
        reg_covar=reg_covar,
        random_state=random_state,
    )

    scoring = [scoring] if isinstance(scoring, str) else scoring

    model, model_evaluation_df = perform_clustering(
        input_df_wide,
        model_selection,
        clf,
        clf_parameters,
        scoring,
        labels_df=labels_df["Encoded Label"],
        **kwargs,
    )
    cluster_labels_df = pd.DataFrame(
        {"Sample": input_df_wide.index, "Cluster Labels": model.predict(input_df_wide)}
    )
    cluster_labels_probabilities_df = pd.DataFrame(
        model.predict_proba(input_df_wide),
    )
    cluster_labels_probabilities_df.insert(0, "Sample", input_df_wide.index)
    return dict(
        model=model,
        model_evaluation_df=model_evaluation_df,
        cluster_labels_df=cluster_labels_df,
        cluster_labels_probabilities_df=cluster_labels_probabilities_df,
    )


def hierarchical_agglomerative_clustering(
    input_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    labels_column: str,
    positive_label: str = None,
    model_selection: str = "Grid search",
    scoring: list[str] = ["completeness_score"],
    n_clusters: int = 2,
    metric: str = "euclidean",
    linkage: str = "ward",
    **kwargs,
):
    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    input_df_wide.sort_values(by="Sample", inplace=True)
    labels_df = (
        metadata_df[["Sample", labels_column]]
        .set_index("Sample")
        .sort_values(by="Sample")
    )
    encoding_mapping, labels_df = encode_labels(
        labels_df, labels_column, positive_label
    )

    clf = AgglomerativeClustering()

    clf_parameters = dict(
        n_clusters=n_clusters,
        metric=metric,
        linkage=linkage,
    )

    model, model_evaluation_df = perform_clustering(
        input_df_wide,
        model_selection,
        clf,
        clf_parameters,
        scoring,
        labels_df=labels_df["Encoded Label"],
        **kwargs,
    )
    cluster_labels_df = pd.DataFrame(
        {"Sample": input_df_wide.index, "Cluster Labels": model.labels_}
    )
    return dict(
        model=model,
        model_evaluation_df=model_evaluation_df,
        cluster_labels_df=cluster_labels_df,
    )


def perform_clustering(
    input_df,
    model_selection,
    clf,
    clf_parameters,
    scoring,
    labels_df=None,  # optional
    model_selection_scoring=None,
    **parameters,
):
    if model_selection == "Manual":
        model = clf.set_params(**clf_parameters)
        labels_pred = model.fit_predict(input_df)
        scores = evaluate_clustering_with_scoring(
            scoring, input_df, labels_pred, labels_df
        )
        model_evaluation_df = create_model_evaluation_df_grid_search_manual(
            clf_parameters,
            scores,
        )
        return model, model_evaluation_df
    else:
        clf_parameters = create_dict_with_lists_as_values(clf_parameters)
        model = perform_grid_search_cv(
            model_selection,
            clf,
            clf_parameters,
            scorer(scoring),
            model_selection_scoring,
        )
        model.fit(input_df, labels_df)
        model_evaluation_df = create_model_evaluation_df_grid_search(
            pd.DataFrame(model.cv_results_),
            clf_parameters,
            scoring,
        )
        best_estimator = model.best_estimator_
        return best_estimator, model_evaluation_df


def scorer(scoring):
    def _scorer(estimator, X, y=None):
        y_pred = estimator.fit_predict(X)
        return evaluate_clustering_with_scoring(scoring, X, y_pred, y)

    return _scorer
