import logging

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

from protzilla.data_preprocessing.plots import (
    create_anomaly_score_bar_plot,
    create_pca_2d_scatter_plot,
    create_pca_3d_scatter_plot,
)
from ..utilities.transform_dfs import long_to_wide


def by_isolation_forest(
    protein_df: pd.DataFrame, n_estimators: int = 100, n_jobs: int = -1
) -> dict:
    """
    This function filters out outliers using a clustering
    isolation forest approach.

    :param protein_df: a dataframe in typical protzilla long format
        on which the outlier detection is performed
    :type protein_df: pandas DataFrame
    :param n_estimators: the number of estimators used by the algorithm,
        default: 100
    :type n_estimators: integer
    :param n_jobs: Number kernels used by algorithm, default:
        all kernels (-1)
    :type n_jobs: integer

    :return: returns a Dataframe containing all samples that are not outliers and a
        dict with list of outlier sample names
    :rtype: Tuple[pandas DataFrame, dict]
    """
    try:
        transformed_df = long_to_wide(protein_df)

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
        df_isolation_forest_data["Anomaly Score"] = clf.decision_function(
            transformed_df
        )
        df_isolation_forest_data["Outlier"] = (
            df_isolation_forest_data["IF Outlier"] == -1
        )
        outlier_list = df_isolation_forest_data[
            df_isolation_forest_data["Outlier"]
        ].index.tolist()

        protein_df = protein_df[~(protein_df["Sample"].isin(outlier_list))]

        return dict(
            protein_df=protein_df,
            outlier_list=outlier_list,
            anomaly_df=df_isolation_forest_data[["Anomaly Score", "Outlier"]],
        )
    except ValueError as e:
        msg = "Outlier Detection by IsolationForest does not accept missing values \
            encoded as NaN. Consider preprocessing your data to remove NaN values."
        return dict(
            protein_df=protein_df,
            outlier_list=None,
            anomaly_df=None,
            messages=[dict(level=logging.ERROR, msg=msg, trace=str(e))],
        )


def by_local_outlier_factor(
    protein_df: pd.DataFrame,
    number_of_neighbors: int = 20,
    n_jobs: int = -1,
) -> dict:
    """
    This function filters out outliers using a clustering
    Local Outlier Factor approach based on k nearest
    neighbors clustering.
    https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html

    :param protein_df: a dataframe in typical protzilla long format
        on which the outlier detection is performed
    :type protein_df: pandas DataFrame
    :param number_of_neighbors: number of neighbors used by the
        algorithm, default: 20
    :type number_of_neighbors: int
    :param n_jobs: Number kernels used by algorithm, default:
        all kernels (-1)
    :type n_jobs: int

    :return: returns a Dataframe containing all samples that are not outliers and a
        dict with list of outlier sample names
    :rtype: Tuple[pandas DataFrame, dict]
    """
    try:
        transformed_df = long_to_wide(protein_df)

        clf = LocalOutlierFactor(n_neighbors=number_of_neighbors, n_jobs=n_jobs)

        df_lof_data = pd.DataFrame(index=transformed_df.index)
        df_lof_data["LOF Outlier"] = clf.fit_predict(
            transformed_df.loc[:, transformed_df.columns != "Sample"]
        )
        df_lof_data["Anomaly Score"] = clf.negative_outlier_factor_

        df_lof_data["Outlier"] = df_lof_data["LOF Outlier"] == -1

        outlier_list = df_lof_data[df_lof_data["Outlier"]].index.tolist()

        protein_df = protein_df[~(protein_df["Sample"].isin(outlier_list))]
        return dict(
            protein_df=protein_df,
            outlier_list=outlier_list,
            anomaly_df=df_lof_data[["Anomaly Score", "Outlier"]],
        )
    except ValueError as e:
        msg = f"Outlier Detection by LocalOutlierFactor does not accept missing values \
            encoded as NaN. Consider preprocessing your data to remove NaN values."
        return dict(
            protein_df=protein_df,
            outlier_list=None,
            anomaly_df=None,
            messages=[dict(level=logging.ERROR, msg=msg, trace=str(e))],
        )


def by_pca(
    protein_df: pd.DataFrame,
    threshold: int = 2,
    number_of_components: int = 3,
) -> dict:
    """
    This function filters out outliers using a PCA
    based approach based geometrical distance to the median
    and returns a list of samples that are inliers.
    Allows 2D (using an ellipse) or 3D (using an ellipsoid)
    analysis. Based on
    https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html

    :param protein_df: a dataframe in typical protzilla long format
        on which the outlier detection is performed
    :type protein_df: pandas DataFrame
    :param threshold: distance from the median in
        number of standard deviations to be included,
        default: 2
    :type threshold: float
    :param number_of_components: number of principal components
        used in the PCA. Allowed: 2 or 3. Default: 3
    :type number_of_components: integer (2 or 3)

    :return: returns a Dataframe containing all samples that are not outliers.
        A dict with list of inlier sample names, a DataFrame that contains the projection
        of the intensity_df on first principal components, a list that contains the
        explained variation for each component and an int, the number of components
        the calculations were executed with
    :rtype: Tuple[pandas DataFrame, dict]
    """
    try:
        assert number_of_components in {
            2,
            3,
        }, f"Wrong number of components. \
            Should be 2 or 3, but is {number_of_components}."

        transformed_df = long_to_wide(protein_df)
        pca_model = PCA(n_components=number_of_components)
        pca_model.fit(transformed_df)

        if number_of_components == 2:
            df_transformed_pca_data = pd.DataFrame(
                pca_model.transform(transformed_df),
                index=transformed_df.index,
                columns=["Component 1", "Component 2"],
            )
        else:
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
        else:
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
        protein_df = protein_df[~(protein_df["Sample"].isin(outlier_list))]

        return dict(
            protein_df=protein_df,
            outlier_list=outlier_list,
            pca_df=df_transformed_pca_data,
            explained_variance_ratio=list(pca_model.explained_variance_ratio_),
            number_of_components=number_of_components,
        )
    except ValueError as e:
        msg = "Outlier Detection by PCA does not accept missing values \
        encoded as NaN. Consider preprocessing your data to remove NaN values."
        return dict(
            protein_df=protein_df,
            outlier_list=None,
            anomaly_df=None,
            messages=[dict(level=logging.ERROR, msg=msg, trace=str(e))],
        )


def by_isolation_forest_plot(method_inputs, method_outputs):
    return [create_anomaly_score_bar_plot(method_outputs["anomaly_df"])]


def by_local_outlier_factor_plot(method_inputs, method_outputs):
    return [create_anomaly_score_bar_plot(method_outputs["anomaly_df"])]


def by_pca_plot(method_inputs, method_outputs):
    pca_df = method_outputs["pca_df"]
    number_of_components = method_outputs["number_of_components"]
    explained_variance_ratio = method_outputs["explained_variance_ratio"]
    if number_of_components == 2:
        return [create_pca_2d_scatter_plot(pca_df, explained_variance_ratio)]
    if number_of_components == 3:
        return [create_pca_3d_scatter_plot(pca_df, explained_variance_ratio)]
