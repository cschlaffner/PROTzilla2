import numpy as np
import pandas as pd
from django.contrib import messages
from sklearn.manifold import TSNE

from protzilla.utilities.transform_dfs import is_long_format, long_to_wide


def t_sne(
    input_df: pd.DataFrame,
    n_components: int = 2,
    perplexity: float = 30.0,
    metric: str = "euclidean",
    random_state: int = 42,
    n_iter: int = 1000,
    n_iter_without_progress: int = 300,
    method: str = "barnes_hut",
):
    """
    A function that uses t-SNE to reduce the dimension of a dataframe and returns a \
    dataframe in wide format with the entered number of components.
    Please note that this function is a simplified version of t-SNE, and it only \
    enables you to adjust the most significant parameters that affect the output. \
    You can find the default values for the non-adjustable parameters here:
    https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html

    :param input_df: the dataframe, whose dimensions should be reduced.
    :type input_df: pd.DataFrame
    :param n_components: The dimension of the space to embed into.
    :type n_components: int
    :param perplexity: the perplexity is related to the number of nearest neighbors
    :type perplexity: float
    :param metric: The metric to use when calculating distance between instances in a \
        feature array. Possible metrics are: euclidean, manhattan, cosine and haversine
    :type metric: str
    :param random_state: determines the random number generator.
    :type random_state: int
    :param n_iter: maximum number of iterations for the optimization
    :type n_iter: int
    :param n_iter_without_progress: Maximum number of iterations without progress \
        before we abort the optimization, used after 250 initial iterations with early \
        exaggeration. Note that progress is only checked every 50 iterations so this \
        value is rounded to the next multiple of 50.
    :type n_iter_without_progress: int
    :param method: the method exact will run on the slower, but exact, algorithm in \
        O(N^2) time. However, the exact method cannot scale to millions of examples. \
        Barnes-Hut approximation will run faster, but not exact, in O(NlogN) time.
    :type method: str
    """
    intensity_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    try:
        embedded_data_model = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            random_state=random_state,
            n_iter=n_iter,
            n_iter_without_progress=n_iter_without_progress,
            method=method,
            metric=metric,
        ).fit_transform(intensity_df_wide)

        embedded_data = pd.DataFrame(
            embedded_data_model,
            index=intensity_df_wide.index,
            columns=["Component1", "Component2"],
        )
        return dict(embedded_data=embedded_data)

    except ValueError as e:
        if intensity_df_wide.isnull().sum().any():
            msg = (
                "T-SNE does not accept missing values encoded as NaN. Consider"
                "preprocessing your data to remove NaN values."
            )
        elif perplexity >= intensity_df_wide.shape[0]:
            msg = (
                "Perplexity must be less than the number of samples. In the selected "
                f"dataframe there is {intensity_df_wide.shape[0]} samples"
            )
        elif (
            min(intensity_df_wide.shape[0], intensity_df_wide.shape[1]) <= n_components
            or n_components <= 1
        ):
            msg = (
                f"n_components={n_components} must be between 1 and "
                f"min(n_samples, n_features)"
                f"={min(intensity_df_wide.shape[0], intensity_df_wide.shape[1])}"
            )
        elif n_components > 3 and method == "barnes_hut":
            msg = (
                "'n_components' should be inferior to 4 for the barnes_hut algorithm "
                "as it relies on quad-tree or oct-tree."
            )
        else:
            msg = ""
        return dict(
            embedded_data=None,
            messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))],
        )


def umap(
    input_df: pd.DataFrame,
    n_neighbors: float = 15,
    n_components: int = 2,
    min_dist: float = 0.1,
    metric: str = "euclidean",
    random_state: int = 42,
    transform_seed: int = 42,
):
    """
    A function that uses UMAP to reduce the dimension of a dataframe and returns a \
    dataframe in wide format with the entered number of components.
    Please note that this function is a simplified version of UMAP, and it only \
    enables you to adjust the most significant parameters that affect the output. \
    You can find the default values for the non-adjustable parameters here:
    https://umap-learn.readthedocs.io/en/latest/api.html

    :param input_df: the dataframe, whose dimensions should be reduced.
    :type input_df: pd.DataFrame
    :param n_components: The dimension of the space to embed into.
    :type n_components: int
    :param n_neighbors: The size of local neighborhood in terms of number of \
        neighboring sample points
    :type n_neighbors: float
    :param min_dist: the effective minimum distance between embedded points. Smaller \
        values will result in a more clustered/clumped embedding where nearby points on \
        the manifold are drawn closer together, while larger values will result on a more \
        even dispersal of points.
    :type min_dist: float
    :param metric: The metric to use when calculating distance between instances in a \
        feature array.
    :type metric: str
    :param random_state: determines the random number generator.
    :type random_state: int
    """

    # umap import is slow, so it should only get imported when needed
    from umap import UMAP

    intensity_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    try:
        embedded_data_model = UMAP(
            n_neighbors=n_neighbors,
            n_components=n_components,
            min_dist=min_dist,
            metric=metric,
            random_state=random_state,
            transform_seed=transform_seed,
        ).fit_transform(intensity_df_wide)

        embedded_data = pd.DataFrame(
            embedded_data_model,
            index=intensity_df_wide.index,
            columns=["Component1", "Component2"],
        )
        return dict(embedded_data=embedded_data)

    except ValueError as e:
        if intensity_df_wide.isnull().sum().any():
            msg = (
                "UMAP does not accept missing values encoded as NaN. Consider "
                "preprocessing your data to remove NaN values."
            )
        else:
            msg = ""
        return dict(
            embedded_data=None,
            messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))],
        )
