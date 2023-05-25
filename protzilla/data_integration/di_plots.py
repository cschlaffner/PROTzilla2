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
    pd.set_option('display.width', get_terminal_size()[0])

    if input_df is None or len(input_df) == 0 or input_df.empty:
        msg = "No data to plot. Please check your input data or run enrichment again."
        return [dict(messages=[dict(level=messages.ERROR, msg=msg)])]
    
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
        print(df.columns)
        fdr_column = df.columns[2]

    if restring_input:
        # manual cutoff because gseapy does not support cutoffs for restring files
        df = df[df[fdr_column] <= cutoff]
        if len(df) == 0:
            msg = f"No data to plot when applying cutoff {cutoff}. Check your input data or choose a different cutoff."
            return [dict(messages=[dict(level=messages.WARNING, msg=msg)])]
        
        column = "-log10(FDR)"
        df[column] = -1 * np.log10(df[fdr_column])
        cutoff = df[column].max()
        df["Overlap"] = "0/0"
    else:
        column = "Adjusted P-value"

    size_y = top_terms * 0.5 * len(categories)
    # ValueError: Warning: No enrich terms when cutoff = 0
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
    return [fig_to_base64(ax.get_figure())]


def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    return base64.b64encode(img.getvalue())
