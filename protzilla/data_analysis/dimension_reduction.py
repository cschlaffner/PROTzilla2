import pandas as pd
from django.contrib import messages
from sklearn.manifold import TSNE
from umap import UMAP

from protzilla.utilities.transform_dfs import long_to_wide


def t_sne(
    intensity_df: pd.DataFrame,
    n_components: int = 2,
    perplexity: float = 30.0,
    random_state: int = 42,
    n_iter: int = 1000,
    n_iter_without_progress: int = 300,
    method: str = "barnes_hut",
):
    intensity_df_wide = long_to_wide(intensity_df)
    try:
        embedded_data = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            random_state=random_state,
            n_iter=n_iter,
            n_iter_without_progress=n_iter_without_progress,
            method=method,
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
    n_neighbors: float = 15,
    n_components: int = 2,
    min_dist: float = 0.1,
    random_state: int = 42,
):
    intensity_df_wide = long_to_wide(intensity_df)
    try:
        embedded_data = UMAP(
            n_neighbors=n_neighbors,
            n_components=n_components,
            min_dist=min_dist,
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
