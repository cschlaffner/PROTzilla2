import pandas as pd
from django.contrib import messages
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.mixture import GaussianMixture

from protzilla.data_analysis.classification_helper import (
    create_dict_with_lists_as_values,
    create_model_evaluation_df_grid_search,
    create_model_evaluation_df_grid_search_manual,
    encode_labels,
    evaluate_clustering_with_scoring,
    perform_grid_search_cv,
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
    A method that uses k-means to partition a number of samples in k clusters. The
    function returns a dataframe with the corresponding cluster of each sample and
    another dataframe with the coordinates of the cluster centers.

    :param input_df: The dataframe that should be clustered in wide or long format
    :type input_df: pd.DataFrame
    :param metadata_df: A separate dataframe containing additional metadata information.
    :type metadata_df: pd.DataFrame
    :param labels_column: The column name in the `metadata_df` dataframe that contains
        the true labels of the data
    :type labels_column: str
    :param positive_label: The positive label for clustering.
    :type positive_label: str
    :param model_selection: The model selection method for hyperparameter tuning.
    :type model_selection: str
    :param scoring: The scoring metric(s) used for model evaluation.
    :type scoring: list[str]
    :param n_clusters: the number of clusters to form as well as the number of
        centroids to generate.
    :type n_clusters: int
    :param random_state: Determines random number generation for centroid initialization
    :type random_state: int
    :param init_centroid_strategy: method for centroid initialization. Possible methods
        are: k-means++ and random
    :type init_centroid_strategy: str
    :param n_init: Number of times the k-means algorithm is run with different centroid
        seeds.
    :type n_init: int
    :param max_iter: Maximum number of iterations of the k-means algorithm for a single
        run.
    :type max_iter: int
    :param tolerance: Relative tolerance with regards to Frobenius norm of the
        difference in the cluster centers of two consecutive iterations to declare
        convergence.
    :type tolerance: float
    :returns: A dictionary containing the following elements:
        - model: The trained Gaussian Mixture Model.
        - model_evaluation_df:  dataframe consisting of the model's parameters and the
        evaluation metrics
        - cluster_labels_df: The dataframe with sample IDs and assigned cluster labels.
    :rtype: dict
    """
    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    try:
        # prepare input_df and labels_df dataframes for clustering
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

        # create dataframes for ouput dict
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
    """
    Performs expectation maximization clustering with a Gaussian Mixture Model, using
    the GaussianMixture estimator from the sklearn package. It returns a dataframe with
    the assigned Gaussian for each sample and a dataframe with the component's density
    for each sample.

    :param input_df: The dataframe that should be clustered in wide or long format
    :type input_df: pd.DataFrame
    :param metadata_df: A separate dataframe containing additional metadata information.
    :type metadata_df: pd.DataFrame
    :param labels_column: The column name in the `metadata_df` dataframe that contains
        the true labels of the data
    :type labels_column: str
    :param positive_label: The positive label for clustering.
    :type positive_label: str
    :param model_selection: The model selection method for hyperparameter tuning.
    :type model_selection: str
    :param scoring: The scoring metric(s) used for model evaluation.
    :type scoring: list[str]
    :param n_components: The number of mixture components in the Gaussian Mixture Model.
    :type n_components: int, optional
    :param covariance_type: The covariance type for the Gaussian Mixture Model.
    :type covariance_type: str, optional
    :param reg_covar: Non-negative regularization added to the diagonal of covariance
        matrices.
    :type reg_covar: float
    :param init_params: The method used to initialize the weights, the means and
        the precisions.
    :type init_params: str
    :param max_iter: The number of EM iterations to perform.
    :type max_iter: int, optional
    :param random_state: The random seed for reproducibility.
    :type random_state: int
    :param **kwargs: Additional keyword arguments to be passed to the
        `perform_clustering` function.
    :returns: A dictionary containing the following elements:
        - model: The trained Gaussian Mixture Model.
        - model_evaluation_df:  dataframe consisting of the model's parameters and the
        evaluation metrics
        - cluster_labels_df: The dataframe with sample IDs and assigned cluster labels.
        - cluster_labels_probabilities_df: The dataframe with sample IDs and predicted
          cluster probabilities.
    :rtype: dict
    """
    # prepare input_df and labels_df dataframes for clustering
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
    """
    Performs Agglomerative Clustering by recursively merging a pair of clusters of
    sample data. The strategy to merge a pair of clusters is determined by the linkage
    distance, which uses the chosen metric to compute the distances between data points.
    The function returns a dataframe with the corresponding cluster of each sample.

    :param input_df: The dataframe that should be clustered in wide or long format
    :type input_df: pd.DataFrame
    :param metadata_df: A separate dataframe containing additional metadata information.
    :type metadata_df: pd.DataFrame
    :param labels_column: The column name in the `metadata_df` dataframe that contains
        the true labels of the data
    :type labels_column: str
    :param positive_label: The positive label for clustering.
    :type positive_label: str
    :param model_selection: The model selection method for hyperparameter tuning.
    :type model_selection: str
    :param scoring: The scoring metric(s) used for model evaluation.
    :type scoring: list[str]
    :param n_clusters: the number of clusters to find
    :type n_clusters: int
    :param metric: Metric used to compute the linkage.
    :type metric: str
    :param linkage: Which linkage criterion to use. The linkage criterion determines
        which distance to use between sets of observation
    :type linkage: str
    :returns: A dictionary containing the following elements:
        - model: The trained Gaussian Mixture Model.
        - model_evaluation_df:  dataframe consisting of the model's parameters and the
        evaluation metrics
        - cluster_labels_df: The dataframe with sample IDs and assigned cluster labels.
    :rtype: dict
    """
    # prepare input_df and labels_df dataframes for clustering
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
    labels_df=None,
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
