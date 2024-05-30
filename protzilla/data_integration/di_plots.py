import logging

import gseapy
import numpy as np
import pandas as pd

from protzilla.constants.protzilla_logging import logger
from protzilla.utilities.utilities import fig_to_base64

from ..constants.colors import PROTZILLA_DISCRETE_COLOR_SEQUENCE


def GO_enrichment_bar_plot(
    input_df,
    top_terms,
    cutoff,
    value,
    gene_sets=[],
    title="",
    colors=PROTZILLA_DISCRETE_COLOR_SEQUENCE,
    figsize=None,
):
    """
    Create a bar plot for the GO enrichment results. The plot is created using the gseapy library.
    Groups the bars by the enrichment categories (e.g. KEGG, Reactome, etc.) and sorts the bars by
    the adjusted p-value or FDR, whichever is available in the input data. A cutoff can be applied
    to the data to only show significant results or results with a low FDR.

    :param input_df: GO enrichment results
    :type input_df: pandas.DataFrame
    :param gene_sets: Categories/Sets from enrichment to plot
    :type gene_sets: list
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
    :param figsize: Size of the plot, defaults to None and is calculated dynamically if not provided.
    :type figsize: tuple, optional

    :return: Base64 encoded image of the plot
    :rtype: bytes
    """

    if input_df is None or len(input_df) == 0 or input_df.empty:
        msg = "No data to plot. Please check your input data or run enrichment again."
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

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
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

    if not gene_sets:
        msg = "Please select at least one category to plot."
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])
    if not isinstance(gene_sets, list):
        gene_sets = [gene_sets]
    if value not in ["fdr", "p-value"]:
        msg = "Invalid value. Value must be either 'fdr' or 'p-value'."
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])

    # remove all Gene_sets that are not in categories
    df = input_df[input_df["Gene_set"].isin(gene_sets)]

    if value == "fdr":  # only available for restring result
        if restring_input:
            # manual cutoff because gseapy does not support cutoffs for fdr
            # and user expects the supplied cutoff to be applied
            df = df[df["fdr"] <= cutoff]
            if len(df) == 0:
                msg = f"No data to plot when applying cutoff {cutoff}. Check your input data or choose a different cutoff."
                return dict(messages=[dict(level=logging.WARNING, msg=msg)])

            column = "-log10(FDR)"
            df[column] = -1 * np.log10(df["fdr"])
            # prevent cutoff from being applied again by bar plot method
            cutoff = df[column].max()
        else:
            return dict(
                messages=[
                    dict(
                        level=logging.ERROR,
                        msg="FDR is not available for this enrichment result.",
                    )
                ]
            )

    elif value == "p-value":
        column = "P-value" if restring_input else "Adjusted P-value"


    if colors == "" or colors is None or len(colors) == 0:
        colors = PROTZILLA_DISCRETE_COLOR_SEQUENCE
    size_y = top_terms * 0.5 * len(gene_sets)
    try:
        ax = gseapy.barplot(
            df=df,
            column=column,
            cutoff=cutoff,
            group="Gene_set",
            figsize=figsize if figsize else (10, size_y),
            top_term=top_terms,
            color=colors,
            title=title,
        )
    except ValueError as e:
        msg = f"No data to plot when applying cutoff {cutoff}. Check your input data or choose a different cutoff."
        return dict(messages=[dict(level=logging.ERROR, msg=msg, trace=str(e))])
    return {"plots": [fig_to_base64(ax.get_figure())]}


def GO_enrichment_dot_plot(
    input_df,
    top_terms,
    cutoff,
    gene_sets=[],
    x_axis_type="Gene Sets",
    title="",
    rotate_x_labels=False,
    show_ring=False,
    dot_size=5,
    figsize=None,
):
    """
    Creates a dot plot for the GO enrichment results. The plot is created using the gseapy library.
    Only the top_terms that meet the cutoff are shown. The x axis can be used to compare multiple
    Gene Set Libraries or to display the Combined Score of one of them.

    :param input_df: GO enrichment results (offline or Enrichr)
    :type input_df: pandas.DataFrame
    :param gene_sets: Categories/Gene Set Libraries from enrichment to plot
    :type gene_sets: list
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
    :param figsize: Size of the plot, defaults to None and is calculated dynamically if not provided.
    :type figsize: tuple, optional

    :return: Base64 encoded image of the plot
    :rtype: bytes
    """
    if not isinstance(input_df, pd.DataFrame) or not "Overlap" in input_df.columns:
        msg = "Please input a dataframe from offline GO enrichment analysis or GO enrichment analysis with Enrichr."
        return [dict(messages=[dict(level=logging.ERROR, msg=msg)])]

    if input_df is None or len(input_df) == 0 or input_df.empty:
        msg = "No data to plot. Please check your input data or run enrichment again."
        return [dict(messages=[dict(level=logging.ERROR, msg=msg)])]

    if not gene_sets:
        msg = "Please select at least one category to plot."
        return [dict(messages=[dict(level=logging.ERROR, msg=msg)])]
    if not isinstance(gene_sets, list):
        gene_sets = [gene_sets]

    if len(gene_sets) > 1 and x_axis_type == "Combined Score":
        msg = "Combined Score is only available for one category. Choose only one category or Gene Sets as x-axis."
        return [dict(messages=[dict(level=logging.WARNING, msg=msg)])]

    # remove all Gene_sets that are not in categories
    df = input_df[input_df["Gene_set"].isin(gene_sets)]

    size_y = top_terms * len(gene_sets)
    xticklabels_rot = 45 if rotate_x_labels else 0

    if x_axis_type == "Gene Sets":
        try:
            ax = gseapy.dotplot(
                df,
                column="Adjusted P-value",
                x="Gene_set",
                size=dot_size,
                top_term=top_terms,
                figsize=figsize if figsize else (3, size_y),
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
            return [dict(messages=[dict(level=logging.ERROR, msg=msg, trace=str(e))])]

    elif x_axis_type == "Combined Score":
        try:
            ax = gseapy.dotplot(
                df,
                size=dot_size,
                top_term=top_terms,
                figsize=figsize if figsize else (3, size_y),
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
            return [dict(messages=[dict(level=logging.ERROR, msg=msg, trace=str(e))])]
    else:
        msg = "Invalid x_axis_type value"
        return [dict(messages=[dict(level=logging.ERROR, msg=msg)])]


def gsea_dot_plot(
    input_df,
    cutoff=0.05,
    gene_sets=[],
    dot_color_value="FDR q-val",
    x_axis_value="NES",
    title="",
    show_ring=False,
    dot_size=5,
    remove_library_names=False,
    figsize=None,
):
    """
    Creates a dot plot from GSEA and pre-ranked GSEA results. The plot is created using the gseapy library.
    Only the top_terms that meet the cutoff are shown.

    :param input_df: GSEA or pre-ranked GSEA results
    :type input_df: pandas.DataFrame
    :param cutoff: Cutoff for the dot_color_value. Only terms with
        dot_color_value < cutoff will be shown.
    :type cutoff: float
    :param gene_sets: Gene Set Libraries from enrichment to plot
    :type gene_sets: list
    :param dot_color_value: What to display as color of the dots: "FDR q-val" or "NOM p-val", defaults to "FDR q-val"
    :type dot_color_value: str
    :param x_axis_value: What to display on the x-axis: "ES"(Enrichment Score) or "NES"(Normalised ES), defaults to "NES"
    :type x_axis_value: str
    :param title: Title of the plot, defaults to ""
    :type title: str, optional
    :param show_ring: Show a ring around the dots, defaults to False
    :type show_ring: bool
    :param dot_size: Size of the dots, defaults to 5
    :type dot_size: int
    :param remove_library_names: Remove the library names from the displayed gene sets, defaults to False
    :type remove_library_names: bool
    :param figsize: Size of the plot, defaults to None and is calculated dynamically if not provided.
    :type figsize: tuple, optional

    :return: Base64 encoded image of the plot
    :rtype: bytes
    """
    if not isinstance(input_df, pd.DataFrame) or not "NES" in input_df.columns:
        msg = "Please input a dataframe from GSEA or preranked GSEA."
        return [dict(messages=[dict(level=logging.ERROR, msg=msg)])]

    if input_df is None or len(input_df) == 0 or input_df.empty:
        msg = "No data to plot. Please check your input data or run enrichment again."
        return [dict(messages=[dict(level=logging.ERROR, msg=msg)])]

    if cutoff is None or cutoff == "":
        msg = "Please enter a cutoff value."
        return [dict(messages=[dict(level=logging.ERROR, msg=msg)])]

    if not dot_size:
        dot_size = 5

    if not gene_sets or gene_sets == "all":
        logger.info("Plotting for all gene set libraries.")
    if not isinstance(gene_sets, list):
        gene_sets = [gene_sets]
    else:  # remove all Gene_sets that were not selected
        input_df = input_df[input_df["Term"].str.startswith(tuple(gene_sets))]

    if remove_library_names:
        input_df["Term"] = input_df["Term"].apply(lambda x: x.split("__")[1])

    size_y = max((input_df[dot_color_value] < cutoff).sum(), 5)
    try:
        ax = gseapy.dotplot(
            input_df,
            column=dot_color_value,
            x=x_axis_value,
            cutoff=cutoff,
            size=dot_size,
            figsize=figsize if figsize else (5, size_y),
            title=title,
            show_ring=show_ring,
        )
        return [
            dict(
                plot_base64=fig_to_base64(ax.get_figure()),
                key="gsea_dot_plot_img",
            )
        ]
    except ValueError as e:
        msg = f"No data to plot when applying cutoff {cutoff}. Check your input data or choose a different cutoff."
        return [dict(messages=[dict(level=logging.ERROR, msg=msg, trace=str(e))])]


def gsea_enrichment_plot(
    term_dict=None,
    term_name=None,
    ranking=None,
    pos_pheno_label="",
    neg_pheno_label="",
    figsize=None,
):
    """
    Creates a typical enrichment plot from GSEA or pre-ranked GSEA details. The plot is created using the gseapy library.

    :param term_dict: Enrichment details for a gene set from GSEA
    :type term_dict: dict
    :param term_name: Name of the gene set, used as a title for the plot
    :type term_name: str
    :param ranking: Ranking output dataframe from GSEA or pre-ranked GSEA
    :type ranking: pandas.DataFrame or pandas.Series
    :param pos_pheno_label: Label for the positively correlated phenotype, defaults to ""
    :type pos_pheno_label: str, optional
    :param neg_pheno_label: Label for the negatively correlated phenotype, defaults to ""
    :type neg_pheno_label: str, optional
    :param figsize: Size of the plot, defaults to None and is calculated dynamically if not provided.
    :type figsize: tuple, optional

    :return: Base64 encoded image of the plot
    :rtype: bytes
    """
    if not isinstance(term_dict, dict) or not "nes" in term_dict.keys():
        msg = "Please input a dictionary with enrichment details for a gene set from GSEA."
        return [dict(messages=[dict(level=logging.ERROR, msg=msg)])]
    if not term_name:
        msg = "Please input a term name."
        return [dict(messages=[dict(level=logging.ERROR, msg=msg)])]
    if not (
        isinstance(ranking, pd.DataFrame) or isinstance(ranking, pd.Series)
    ) or not (ranking.index.name == "Gene symbol" or ranking.index.name == "gene_name"):
        msg = "Please input a ranking output dataframe from GSEA or pre-ranked GSEA."
        return [dict(messages=[dict(level=logging.ERROR, msg=msg)])]
    if isinstance(ranking, pd.DataFrame):  # ensure that ranking is a series
        ranking = ranking.iloc[:, 0]

    try:
        enrichment_plot_axes = gseapy.gseaplot(
            rank_metric=ranking,
            term=term_name,
            pheno_pos=pos_pheno_label,
            pheno_neg=neg_pheno_label,
            **term_dict,
            figsize=figsize if figsize else (6, 5.5),
        )
        return [
            dict(
                plot_base64=fig_to_base64(enrichment_plot_axes[0].get_figure()),
                key="gsea_enrichment_plot_img",
            )
        ]
    except Exception as e:
        msg = f"Could not plot enrichment plot for term {term_name}."
        return [dict(messages=[dict(level=logging.ERROR, msg=msg, trace=str(e))])]
