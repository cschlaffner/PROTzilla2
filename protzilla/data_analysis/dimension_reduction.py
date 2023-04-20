import pandas as pd
from django.contrib import messages
from sklearn.manifold import TSNE
from umap import UMAP

from protzilla.utilities.transform_dfs import long_to_wide


def t_sne(
    intensity_df: pd.DataFrame,
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
    t-sne bblablabla
    :param input_df: the dataframe, whose dimensions should be reduced.
    :type input_df: pd.DataFrame
    :param n_components: The dimension of the space to embed into.
    :type n_components: int
    :param perplexity: the perplexity is related to the number of nearest neighbors
    :type perplexity: float
    :param metric: The metric to use when calculating distance between instances in a \
    feature array.
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
    intensity_df_wide = long_to_wide(input_df)
    try:
        embedded_data = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            random_state=random_state,
            n_iter=n_iter,
            n_iter_without_progress=n_iter_without_progress,
            method=method,
            metric=metric,
        ).fit_transform(intensity_df_wide)

        embedded_data_df = pd.DataFrame(embedded_data, index=intensity_df_wide.index)
        return intensity_df, dict(embedded_data_df=embedded_data_df)

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
        return intensity_df, dict(
            embedded_data_df=None,
            messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))],
        )


def umap(
    intensity_df: pd.DataFrame,
    input_df: pd.DataFrame,
    n_neighbors: float = 15,
    n_components: int = 2,
    min_dist: float = 0.1,
    metric: str = "euclidean",
    random_state: int = 42,
):
    """
    umap blablabalba

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
    intensity_df_wide = long_to_wide(input_df)
    try:
        embedded_data = UMAP(
            n_neighbors=n_neighbors,
            n_components=n_components,
            min_dist=min_dist,
            metric=metric,
            random_state=random_state,
        ).fit_transform(intensity_df_wide)

        embedded_data_df = pd.DataFrame(embedded_data, index=intensity_df_wide.index)
        return intensity_df, dict(embedded_data_df=embedded_data_df)

    except ValueError as e:
        if intensity_df_wide.isnull().sum().any():
            msg = (
                "T-SNE does not accept missing values encoded as NaN. Consider"
                "preprocessing your data to remove NaN values."
            )
        else:
            msg = ""
        return intensity_df, dict(
            embedded_data_df=None,
            messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))],
        )
