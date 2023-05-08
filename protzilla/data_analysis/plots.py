import dash_bio as dashbio
import numpy as np
import pandas as pd
import plotly.express as px
from django.contrib import messages

from protzilla.utilities.transform_dfs import is_long_format, long_to_wide


def scatter_plot(
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
        color_df = (
            pd.DataFrame() if not isinstance(color_df, pd.DataFrame) else color_df
        )

        if color_df.shape[1] > 1:
            raise ValueError("The color dataframe should have 1 dimension only")

        if intensity_df_wide.shape[1] == 2:
            intensity_df_wide = pd.concat([intensity_df_wide, color_df], axis=1)
            x_name, y_name = intensity_df_wide.columns[:2]
            color_name = color_df.columns[0] if not color_df.empty else None
            fig = px.scatter(intensity_df_wide, x=x_name, y=y_name, color=color_name)
        elif intensity_df_wide.shape[1] == 3:
            intensity_df_wide = pd.concat([intensity_df_wide, color_df], axis=1)
            x_name, y_name, z_name = intensity_df_wide.columns[:3]
            color_name = color_df.columns[0] if not color_df.empty else None
            fig = px.scatter_3d(
                intensity_df_wide, x=x_name, y=y_name, z=z_name, color=color_name
            )
        else:
            raise ValueError(
                "The dimensions of the DataFrame are either too high or too low."
            )

        return [fig]
    except ValueError as e:
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
        return [dict(messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))])]


def create_volcano_plot(
    p_values, log2_fc, fc_threshold, alpha, proteins_of_interest=None
):
    """
    Function to create a volcano plot from p values and log2 fold change with the
    possibility to annotate proteins of interest.
    
    :param p_values:dataframe with p values
    :type p_values: pd.Dataframe
    :param log2_fc: dataframe with log2 fold change
    :type log2_fc: pd.Dataframe
    :param fc_threshold: the threshold for the fold change to show
    :type fc_threshold: float
    :param alpha: the alpha value for the significance line
    :type alpha: float
    :param proteins_of_interest: the proteins that should be annotated in the plot
    :type proteins_of_interest: list or None
    """

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

    if proteins_of_interest is None:
        proteins_of_interest = []

    # annotate the proteins of interest permanently in the plot
    for protein in proteins_of_interest:
        fig.add_annotation(
            x=plot_df.loc[
                plot_df["Protein ID"] == protein,
                "log2_fold_change",
            ].values[0],
            y=-np.log10(
                plot_df.loc[
                    plot_df["Protein ID"] == protein,
                    "corrected_p_value",
                ].values[0]
            ),
            text=protein,
            showarrow=True,
            arrowhead=1,
            font=dict(color="#ffffff"),
            align="center",
            arrowcolor="#4A536A",
            bgcolor="#4A536A",
            opacity=0.8,
            ax=0,
            ay=-20,
        )

    new_names = {
        "Point(s) of interest": "Significant Proteins",
        "Dataset": "Not Significant Proteins",
    }

    fig.for_each_trace(
        lambda t: t.update(
            name=new_names[t.name],
            legendgroup=new_names[t.name],
        )
    )

    return [fig]
