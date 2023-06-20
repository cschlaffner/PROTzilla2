import gseapy
import numpy as np
import pandas as pd
from django.contrib import messages

from ..constants.colors import PROTZILLA_DISCRETE_COLOR_SEQUENCE
from protzilla.utilities.transform_figure import fig_to_base64


def go_enrichment_bar_plot(
    input_df,
    top_terms,
    cutoff,
    value,
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
    :param value: Value to plot, either "p_value" or "fdr"
    :type value: str
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
    if "term" in input_df.columns:
        # df is a restring file
        restring_input = True
        input_df = input_df.rename(
            columns={"description": "Term", "p_value": "P-value"}
        )
        input_df["Overlap"] = "0/0"
    elif not "Term" in input_df.columns:
        msg = "Please choose an enrichment result dataframe to plot."
        return [dict(messages=[dict(level=messages.ERROR, msg=msg)])]

    if not isinstance(categories, list):
        categories = [categories]
    if not categories:
        msg = "Please select at least one category to plot."
        return [dict(messages=[dict(level=messages.ERROR, msg=msg)])]

    # remove all Gene_sets that are not in categories
    df = input_df[input_df["Gene_set"].isin(categories)]

    if value == "fdr":  # only available for restring result
        if restring_input:
            # manual cutoff because gseapy does not support cutoffs for fdr
            # and user expects the supplied cutoff to be applied
            df = df[df["fdr"] <= cutoff]
            if len(df) == 0:
                msg = f"No data to plot when applying cutoff {cutoff}. Check your input data or choose a different cutoff."
                return [dict(messages=[dict(level=messages.WARNING, msg=msg)])]

            column = "-log10(FDR)"
            df[column] = -1 * np.log10(df["fdr"])
            # prevent cutoff from being applied again by bar plot method
            cutoff = df[column].max()
        else:
            return [
                dict(
                    messages=[
                        dict(
                            level=messages.ERROR,
                            msg="FDR is not available for this enrichment result.",
                        )
                    ]
                )
            ]
    elif value == "p_value":
        column = "P-value" if restring_input else "Adjusted P-value"

    if colors == "" or colors is None or len(colors) == 0:
        colors = PROTZILLA_DISCRETE_COLOR_SEQUENCE
    size_y = top_terms * 0.5 * len(categories)
    try:
        ax = gseapy.barplot(
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


def go_enrichment_dot_plot(
    input_df,
    top_terms,
    cutoff,
    categories=[],
    x_axis_type="Gene Sets",
    title="",
    rotate_x_labels=False,
    show_ring=False,
    dot_size=5,
):
    """
    Creates a dot plot for the GO enrichment results. The plot is created using the gseapy library.
    Only the top_terms that meet the cutoff are shown. The x axis can be used to compare multiple
    Gene Set Libraries or to display the Combined Score of one of them.

    :param input_df: GO enrichment results (offline or Enrichr)
    :type input_df: pandas.DataFrame
    :param categories: Categories/Gene Set Libraries from enrichment to plot
    :type categories: list
    :param top_terms: Number of top enriched terms per category
    :type top_terms: int
    :param cutoff: Cutoff for the Adjusted p-value. Only terms with
        Adjusted P-value < cutoff will be shown.
    :type cutoff: float
    :param x_axis_type: What to display on the x-axis: "Gene Sets" or "Combined Score", defaults to "Gene Sets"
    :type x_axis_type: str
    :param title: Title of the plot, defaults to ""
    :type title: str, optional
    :param rotate_x_labels: Rotate the x-axis labels by 45 degrees if Gene Sets are on x_axis, defaults to True
    :type rotate_x_labels: bool
    :param show_ring: Show a ring around the dots, defaults to False
    :type show_ring: bool
    :param dot_size: Size of the dots, defaults to 5
    :type dot_size: int
    :return: Base64 encoded image of the plot
    :rtype: bytes
    """
    if not isinstance(input_df, pd.DataFrame) or not "Overlap" in input_df.columns:
        msg = "Please input a dataframe from offline GO enrichment analysis or GO enrichment analysis with Enrichr."
        return [dict(messages=[dict(level=messages.ERROR, msg=msg)])]

    if input_df is None or len(input_df) == 0 or input_df.empty:
        msg = "No data to plot. Please check your input data or run enrichment again."
        return [dict(messages=[dict(level=messages.ERROR, msg=msg)])]

    if not isinstance(categories, list):
        categories = [categories]
    if not categories:
        msg = "Please select at least one category to plot."
        return [dict(messages=[dict(level=messages.ERROR, msg=msg)])]

    if len(categories) > 1 and x_axis_type == "Combined Score":
        msg = "Combined Score is only available for one category. Choose only one category or Gene Sets as x-axis."
        return [dict(messages=[dict(level=messages.WARNING, msg=msg)])]

    # remove all Gene_sets that are not in categories
    df = input_df[input_df["Gene_set"].isin(categories)]

    size_y = top_terms * len(categories)
    xticklabels_rot = 45 if rotate_x_labels else 0

    if x_axis_type == "Gene Sets":
        try:
            ax = gseapy.dotplot(
                df,
                column="Adjusted P-value",
                x="Gene_set",
                size=dot_size,
                top_term=top_terms,
                figsize=(3, size_y),
                cutoff=cutoff,
                title=title,
                xticklabels_rot=xticklabels_rot,
                show_ring=show_ring,
            )
            return [
                dict(
                    plot_base64=fig_to_base64(ax.get_figure()),
                    key="go_enrichment_dot_plot_img",
                )
            ]
        except ValueError as e:
            msg = f"No data to plot when applying cutoff {cutoff}. Check your input data or choose a different cutoff."
            return [dict(messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))])]

    elif x_axis_type == "Combined Score":
        try:
            ax = gseapy.dotplot(
                df,
                size=10,
                top_term=top_terms,
                figsize=(3, size_y),
                cutoff=cutoff,
                title=title,
                xticklabels_rot=xticklabels_rot,
                show_ring=show_ring,
            )
            return [
                dict(
                    plot_base64=fig_to_base64(ax.get_figure()),
                    key="go_enrichment_dot_plot_img",
                )
            ]
        except ValueError as e:
            msg = f"No data to plot when applying cutoff {cutoff}. Check your input data or choose a different cutoff."
            return [dict(messages=[dict(level=messages.ERROR, msg=msg, trace=str(e))])]
    else:
        msg = "Invalid x_axis_type value"
        return [dict(messages=[dict(level=messages.ERROR, msg=msg)])]
