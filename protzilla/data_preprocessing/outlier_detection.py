import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.decomposition import PCA
from ..utilities.transform_dfs import long_to_wide


def with_isolation_forest(
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
    :return: returns a Dataframe containing all samples that are not outliers and a\
    dict with list of outlier sample names
    :rtype: Tuple[pandas DataFrame, dict]
    """
    transformed_df = long_to_wide(intensity_df)

    clf = IsolationForest(
        random_state=0,
        max_samples=(len(transformed_df) // 2),
        n_jobs=n_jobs,
        n_estimators=n_estimators,
    )

    df_isolation_forest_data = pd.DataFrame(index=transformed_df.index)
    df_isolation_forest_data["IF Outlier"] = clf.fit_predict(
        transformed_df.loc[:, transformed_df.columns != "Sample"]
    )
    df_isolation_forest_data["Anomaly Score"] = clf.decision_function(transformed_df)
    df_isolation_forest_data["Outlier"] = df_isolation_forest_data["IF Outlier"] == -1
    outlier_list = df_isolation_forest_data[
        df_isolation_forest_data["Outlier"]
    ].index.tolist()

    intensity_df = intensity_df[~(intensity_df["Sample"].isin(outlier_list))]

    return intensity_df, dict(outlier_list=outlier_list)


def with_local_outlier_factor(
    intensity_df: pd.DataFrame,
    number_of_neighbors: int = 35,
    n_jobs: int = -1,
):
    """
    This function filters out outliers using a clustering
    Local Outlier Factor approach based on k nearest
    neighbors clustering.
    https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html

    :param intensity_df: a dataframe in typical protzilla long format
    on which the outlier detection is performed
    :type intensity_df: pandas DataFrame
    :param number_of_neighbors: number of neighbors used by the
    algorithm, default: 35
    :type number_of_neighbors: int
    :param n_jobs: Number kernels used by algorithm, default:
    all kernels (-1)
    :type n_jobs: int
    :return: returns a Dataframe containing all samples that are not outliers and a\
    dict with list of outlier sample names
    :rtype: Tuple[pandas DataFrame, dict]
    """
    transformed_df = long_to_wide(intensity_df)

    clf = LocalOutlierFactor(n_neighbors=number_of_neighbors, n_jobs=n_jobs)

    df_lof_data = pd.DataFrame(index=transformed_df.index)
    df_lof_data["LOF Outlier"] = clf.fit_predict(
        transformed_df.loc[:, transformed_df.columns != "Sample"]
    )
    df_lof_data["Anomaly Score"] = clf.negative_outlier_factor_

    df_lof_data["Outlier"] = df_lof_data["LOF Outlier"] == -1

    outlier_list = df_lof_data[df_lof_data["Outlier"]].index.tolist()

    intensity_df = intensity_df[~(intensity_df["Sample"].isin(outlier_list))]
    return intensity_df, dict(outlier_list=outlier_list)


def with_pca(
    intensity_df: pd.DataFrame,
    threshold: int = 2,
    number_of_components: int = 3,
):
    """
    This function filters out outliers using a PCA
    based approach based geometrical distance to the median
    and returns a list of samples that are inliers.
    Allows 2D (using an ellipse) or 3D (using an ellipsoid)
    analysis. Based on
    https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html

    :param intensity_df: a dataframe in typical protzilla long format
    on which the outlier detection is performed
    :type intensity_df: pandas DataFrame
    :param threshold: distance from the median in
    number of standard deviations to be included,
    default: 2
    :type threshold: float
    :param number_of_components: number of principal components
    used in the PCA. Allowed: 2 or 3. Default: 3
    :type number_of_components: integer (2 or 3)
    :return: returns a Dataframe containing all samples that are not outliers and a\
    dict with list of outlier sample names
    :rtype: Tuple[pandas DataFrame, dict]
    """

    assert number_of_components in {
        2,
        3,
    }, f"Wrong number of components. \
        Should be 2 or 3, but is {number_of_components}."

    transformed_df = long_to_wide(intensity_df)

    pca_model = PCA(n_components=number_of_components)

    pca_model.fit(transformed_df)

    if number_of_components == 2:
        df_transformed_pca_data = pd.DataFrame(
            pca_model.transform(transformed_df),
            index=transformed_df.index,
            columns=["Component 1", "Component 2"],
        )
    elif number_of_components == 3:
        df_transformed_pca_data = pd.DataFrame(
            pca_model.transform(transformed_df),
            index=transformed_df.index,
            columns=["Component 1", "Component 2", "Component 3"],
        )

    # Detect outliers in the transformed data.

    medians = df_transformed_pca_data.median()
    stdevs = df_transformed_pca_data.std()

    if number_of_components == 2:
        df_transformed_pca_data["Outlier"] = [
            (x - medians[0]) ** 2 / (threshold * stdevs[0]) ** 2
            + (y - medians[1]) ** 2 / (threshold * stdevs[1]) ** 2
            > 1
            for x, y in zip(
                df_transformed_pca_data["Component 1"],
                df_transformed_pca_data["Component 2"],
            )
        ]
        outlier_list = df_transformed_pca_data[
            df_transformed_pca_data["Outlier"]
        ].index.tolist()

    elif number_of_components == 3:
        df_transformed_pca_data["Outlier"] = [
            (x - medians[0]) ** 2 / (threshold * stdevs[0]) ** 2
            + (y - medians[1]) ** 2 / (threshold * stdevs[1]) ** 2
            + (z - medians[2]) ** 2 / (threshold * stdevs[2]) ** 2
            > 1
            for x, y, z in zip(
                df_transformed_pca_data["Component 1"],
                df_transformed_pca_data["Component 2"],
                df_transformed_pca_data["Component 3"],
            )
        ]
        outlier_list = df_transformed_pca_data[
            df_transformed_pca_data["Outlier"]
        ].index.tolist()

    intensity_df = intensity_df[~(intensity_df["Sample"].isin(outlier_list))]

    return intensity_df, dict(outlier_list=outlier_list)
