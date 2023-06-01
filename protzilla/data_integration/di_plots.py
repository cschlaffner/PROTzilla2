import io
import base64
import gseapy as gp
import numpy as np
from django.contrib import messages

from ..constants.colors import PROTZILLA_DISCRETE_COLOR_SEQUENCE


def go_enrichment_bar_plot(
    input_df,
    top_terms,
    cutoff,
    categories=[],
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

    # This method can be used for both restring and gseapy results
    # restring results are different from the expected gseapy results
    # and need to be converted.
    # This is done by renaming the columns accordingly and adding missing
    # columns with placeholder values (since they are not used in the plot).
    # Example files can be found in the tests/test_data/enrichment_data folder.
    restring_input = False
    if "score" in input_df.columns and "ID" in input_df.columns:
        # df is a restring summary file
        restring_input = True
        input_df = input_df.rename(columns={"ID": "Term"})
        fdr_column = "score"
    elif "term" in input_df.columns and "common" in input_df.columns:
        # df is a restring results file
        restring_input = True
        input_df = input_df.rename(columns={"term": "Term"})
        fdr_column = input_df.columns[2]
    elif not "Term" in input_df.columns:
        msg = "Please choose an enrichment result dataframe to plot."
        return [dict(messages=[dict(level=messages.ERROR, msg=msg)])]

    if not isinstance(categories, list):
        categories = [categories]
    if len(categories) == 0:
        msg = "Please select at least one category to plot."
        return [dict(messages=[dict(level=messages.ERROR, msg=msg)])]

    # remove all Gene_sets that are not in categories
    df = input_df[input_df["Gene_set"].isin(categories)]

    if colors == "" or colors is None or len(colors) == 0:
        colors = PROTZILLA_DISCRETE_COLOR_SEQUENCE

    if restring_input:
        # manual cutoff because gseapy does not support cutoffs for restring files
        # and user expects the supplied cutoff to be applied
        df = df[df[fdr_column] <= cutoff]
        if len(df) == 0:
            msg = f"No data to plot when applying cutoff {cutoff}. Check your input data or choose a different cutoff."
            return [dict(messages=[dict(level=messages.WARNING, msg=msg)])]

        column = "-log10(FDR)"
        df[column] = -1 * np.log10(df[fdr_column])
        df["Overlap"] = "0/0"
        # prevent cutoff from being applied again by barplot method
        cutoff = df[column].max()
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
