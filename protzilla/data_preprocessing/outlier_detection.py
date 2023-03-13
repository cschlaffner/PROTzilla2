def get_outlier_detection_results(
    intensity_df: pd.DataFrame, n_estimators: int = 50, n_jobs: int = -1
):
    """
    This function filters out outliers using a clustering
    isolation forest approach.

    :param intensity_df: a dataframe in typical protzilla long format
    on which the outlier detection is performed
    :type intensity_df: pandas DataFrame
    :param n_estimators: the number of estimators used by the algorithm,
    default: 50
    :type n_estimators: integer
    :param n_jobs: Number kernels used by algorithm, default:
    all kernels (-1)
    :type n_jobs: integer
    :param **kwargs: additional keyword arguments passed to
    sklearn.ensemble IsolationForest
    :type **kwargs: dict
    :return: returns a list of outlier sample names
    :rtype: list
    """
    # Transform long to wide dataframe
    transformed_df = transform_protein_df_long_to_wide(intensity_df)

    # Build IsolationForest
    clf = IsolationForest(
        random_state=0,
        max_samples=(len(transformed_df) // 2),
        n_jobs=n_jobs,
        n_estimators=n_estimators,
        **kwargs,
    )

    self.df_isolation_forest_data = pd.DataFrame(index=transformed_df.index)
    self.df_isolation_forest_data["IF Outlier"] = clf.fit_predict(
        transformed_df.loc[:, transformed_df.columns != "Sample"]
    )
    self.df_isolation_forest_data["Anomaly Score"] = clf.decision_function(
        transformed_df
    )
    self.df_isolation_forest_data["Outlier"] = (
        self.df_isolation_forest_data["IF Outlier"] == -1
    )
    self.outlier_list = self.df_isolation_forest_data[
        self.df_isolation_forest_data["Outlier"]
    ].index.tolist()

    return self.outlier_list
