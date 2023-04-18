from protzilla.utilities.transform_dfs import long_to_wide, is_long_format
import plotly.express as px
import pandas as pd


# Test if input handling works in frontend
def scatter_plot_2d(
    input_df,
    color_df,
):
    intensity_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    try:
        assert intensity_df_wide.shape[1] == 2

        intensity_df_wide = pd.concat([intensity_df_wide, color_df], axis=1)
        x_name = intensity_df_wide.columns[0]
        y_name = intensity_df_wide.columns[1]
        color_name = color_df.columns[0]
        fig = px.scatter(intensity_df_wide, x=x_name, y=y_name, color=color_name)
        return [fig]
    except AssertionError as e:
        msg = ""
        if intensity_df_wide.shape[1] < 2:
            msg = (
                f"The input dataframe has {intensity_df_wide.shape[1]} feature. "
                f"Consider using another plot to visualize your data"
            )
        elif intensity_df_wide.shape[1] > 2:
            msg = (
                f"The input dataframe has {intensity_df_wide.shape[1]} features. "
                f"Consider reducing the dimensionality of your data"
            )
        return [{}, msg]


def scatter_plot_3d(
    input_df,
    color_df,
):
    intensity_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    try:
        assert intensity_df_wide.shape[1] == 3

        intensity_df_wide = pd.concat([intensity_df_wide, color_df], axis=1)
        x_name = intensity_df_wide.columns[0]
        y_name = intensity_df_wide.columns[1]
        z_name = intensity_df_wide.columns[2]
        color_name = color_df.columns[0]
        fig = px.scatter_3d(
            intensity_df_wide, x=x_name, y=y_name, z=z_name, color=color_name
        )
        return [fig]
    except AssertionError as e:
        msg = ""
        if intensity_df_wide.shape[1] < 3:
            msg = (
                f"The input dataframe has {intensity_df_wide.shape[1]} features. "
                f"Consider using a 2d scatter plot to visualize your data"
            )
        elif intensity_df_wide.shape[1] > 3:
            msg = (
                f"The input dataframe has {intensity_df_wide.shape[1]} features. "
                f"Consider reducing the dimensionality of your data"
            )
        return [{}, msg]
