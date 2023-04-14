import pandas as pd
from sklearn.manifold import TSNE
from protzilla.utilities.transform_dfs import long_to_wide
from django.contrib import messages


def t_sne(
    intensity_df: pd.DataFrame,
    n_components: int = 2,
    perplexity: int = 30.0,
    random_state: int = 42,
    n_iter: int = 1000,
    n_iter_without_progress: int = 300,
):
    intensity_df_wide = long_to_wide(intensity_df)
    try:
        embedded_data = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            random_state=random_state,
            n_iter=n_iter,
            n_iter_without_progress=n_iter_without_progress,
        ).fit_transform(intensity_df_wide)

        embedded_data_df = pd.DataFrame(embedded_data, index=intensity_df_wide.index)
        return intensity_df, dict(embedded_data_df=embedded_data_df)
    except ValueError as e:
        if intensity_df_wide.isnull().sum().any():
            msg = (
                "T-SNE does not accept missing values encoded as NaN. Consider"
                "preprocessing your data to remove NaN values."
            )
        if perplexity >= intensity_df_wide.shape[0]:
            msg = (
                "Perplexity must be less than the number of samples. In the selected "
                f"dataframe there is {intensity_df_wide.shape[0]} samples"
            )
        return intensity_df, dict(
            embedded_data_df=None,
            messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))],
        )
