import pandas as pd
import gseapy as gp

import matplotlib.pyplot as plt
import plotly.tools as tls
import numpy as np
import plotly.graph_objects as go
from django.contrib import messages

from ..constants.colors import PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE

def go_enrichment_bar_plot(input_df, categories, top_terms, cutoff, title, colors):
    if input_df is None or len(input_df) == 0 or input_df.empty:
        msg = "No data to plot. Please check your input data or run enrichment again."
        [dict(messages=[dict(level=messages.ERROR, msg=msg)])]

    # remove all Gene_sets that are not in categories
    df = input_df[input_df["Gene_set"].isin(categories)]

    if colors =="" or colors is None or len(colors) == 0:
        colors = PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE

    size_y = top_terms * 0.5 * len(categories)
    if title != "" and title is not None:
        bar = gp.barplot(df=df,
                        column="Adjusted P-value",
                        cutoff=cutoff,
                        group="Gene_set",
                        figsize=(10, size_y),
                        top_term=top_terms,
                        color=colors,
                        title=title,
                    )
    else:
        bar = gp.barplot(df=df,
                        column="Adjusted P-value",
                        cutoff=cutoff,
                        group=top_terms,
                        figsize=(10, size_y),
                        top_term=top_terms,
                        color=colors,
                    )

    return [bar]