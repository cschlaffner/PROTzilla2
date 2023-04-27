import pandas as pd
import plotly.express as px
from django.contrib import messages
import dash_bio as dashbio

from protzilla.utilities.transform_dfs import is_long_format, long_to_wide


# TODO: remove intensity_df parameter when plots as steps is already implemented
def scatter_plot(
    intensity_df: pd.DataFrame,
    input_df: pd.DataFrame,
    color_df: pd.DataFrame | None = None,
):
    """
    Function to create a scatter plot from data. 
    
    :param input_df: the dataframe that should be plotted. It should have either 2 \
    or 3 dimension
    :type input_df: pd.Dataframe
    :param color_df: the Dataframe with one column according to which the marks should \
    be colored. This is an optional parameter
    :type color_df: pd.Dataframe
    """
    intensity_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    try:
        if color_df.shape[1] == 1:
            if intensity_df_wide.shape[1] == 2:
                intensity_df_wide = pd.concat([intensity_df_wide, color_df], axis=1)
                x_name = intensity_df_wide.columns[0]
                y_name = intensity_df_wide.columns[1]
                color_name = color_df.columns[0]
                fig = px.scatter(
                    intensity_df_wide, x=x_name, y=y_name, color=color_name
                )
            elif intensity_df_wide.shape[1] == 3:
                intensity_df_wide = pd.concat([intensity_df_wide, color_df], axis=1)
                x_name = intensity_df_wide.columns[0]
                y_name = intensity_df_wide.columns[1]
                z_name = intensity_df_wide.columns[2]
                color_name = color_df.columns[0]
                fig = px.scatter_3d(
                    intensity_df_wide, x=x_name, y=y_name, z=z_name, color=color_name
                )
            else:
                raise Exception(
                    "The dimensions of the DataFrame are either too high or too low."
                )
        else:
            raise Exception("The color dataframe should have 1 dimension only")
        return [fig]
    except Exception as e:
        msg = ""
        if intensity_df_wide.shape[1] < 2:
            msg = (
                f"The input dataframe has {intensity_df_wide.shape[1]} feature. "
                f"Consider using another plot to visualize your data"
            )
        elif intensity_df_wide.shape[1] > 3:
            msg = (
                f"The input dataframe has {intensity_df_wide.shape[1]} features. "
                f"Consider reducing the dimensionality of your data"
            )
        elif color_df.shape[1] != 1:
            msg = "The color dataframe should have 1 dimension only"
        return [
            dict(),
            dict(messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))]),
        ]


def create_volcano_plot(p_values, log2_fc, fc_threshold, alpha):
    plot_df = p_values.join(log2_fc.set_index("Protein ID"), on="Protein ID")
    fig = dashbio.VolcanoPlot(
        dataframe=plot_df,
        effect_size="log2_fold_change",
        p="corrected_p_value",
        snp=None,
        gene=None,
        genomewideline_value=alpha,
        effect_size_line=[-fc_threshold, fc_threshold],
        xlabel="log2(fc)",
        ylabel="-log10(p)",
        title="Volcano Plot",
        annotation="Protein ID",
    )
    return [fig]
