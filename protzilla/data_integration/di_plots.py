import io
import base64
import gseapy as gp
import numpy as np
import pandas as pd
from django.contrib import messages

from ..constants.colors import PROTZILLA_DISCRETE_COLOR_SEQUENCE

from shutil import get_terminal_size


def go_enrichment_bar_plot(
    input_df,
    categories,
    top_terms,
    cutoff,
    title="",
    colors=PROTZILLA_DISCRETE_COLOR_SEQUENCE,
):
    """
    Create a bar plot for the GO enrichment results. The plot is created using the gseapy library.
    Groups the bars by the enrichment categories (e.g. KEGG, Reactome, etc.) and sorts the bars by
    the adjusted p-value or FDR, whichever is available in the input data. A cutoff can be applied
    to the data to only show significant results or results with a low FDR.

    :param input_df: GO enrichment results
    :type input_df: pandas.DataFrame
    :param categories: Categories/Sets from enrichment to plot
    :type categories: list
    :param top_terms: Number of top enriched terms per category
    :type top_terms: int
    :param cutoff: Cutoff for the Adjusted p-value or FDR. Only terms with
        Adjusted P-value (or FDR) < cutoff will be shown.
    :type cutoff: float
    :param title: Title of the plot, defaults to ""
    :type title: str, optional
    :param colors: Colors to use for the bars, defaults to PROTZILLA_DISCRETE_COLOR_SEQUENCE
    :type colors: list, optional
    :return: Base64 encoded image of the plot
    :rtype: bytes
    """

    if input_df is None or len(input_df) == 0 or input_df.empty:
        msg = "No data to plot. Please check your input data or run enrichment again."
        return [dict(messages=[dict(level=messages.ERROR, msg=msg)])]

    if not isinstance(categories, list):
        categories = [categories]

    # remove all Gene_sets that are not in categories
    df = input_df[input_df["Gene_set"].isin(categories)]

    if colors == "" or colors is None or len(colors) == 0:
        colors = PROTZILLA_DISCRETE_COLOR_SEQUENCE

    restring_input = False
    if "score" in df.columns and "ID" in df.columns:
        # df is a restring summary file
        restring_input = True
        df = df.rename(columns={"ID": "Term"})
        fdr_column = "score"
    elif "term" in df.columns and "common" in df.columns:
        # df is a restring results file
        restring_input = True
        df = df.rename(columns={"term": "Term"})
        fdr_column = df.columns[2]

    if restring_input:
        # manual cutoff because gseapy does not support cutoffs for restring files
        df = df[df[fdr_column] <= cutoff]
        if len(df) == 0:
            msg = f"No data to plot when applying cutoff {cutoff}. Check your input data or choose a different cutoff."
            return [dict(messages=[dict(level=messages.WARNING, msg=msg)])]

        column = "-log10(FDR)"
        df[column] = -1 * np.log10(df[fdr_column])
        # prevent cutoff being applied again
        cutoff = df[column].max()
        df["Overlap"] = "0/0"
    else:
        column = "Adjusted P-value"

    size_y = top_terms * 0.5 * len(categories)
    try:
        ax = gp.barplot(
            df=df,
            column=column,
            cutoff=cutoff,
            group="Gene_set",
            figsize=(10, size_y),
            top_term=top_terms,
            color=colors,
            title=title,
        )
    except ValueError as e:
        msg = f"No data to plot when applying cutoff {cutoff}. Check your input data or choose a different cutoff."
        return [dict(messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))])]
    return [fig_to_base64(ax.get_figure())]


def fig_to_base64(fig):
    """
    Convert a matplotlib figure to base64. This is used to display the figure in the browser.

    :param fig: matplotlib figure
    :type fig: matplotlib.figure.Figure
    :return: base64 encoded image
    :rtype: bytes
    """
    img = io.BytesIO()
    fig.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    return base64.b64encode(img.getvalue())