import io
import base64
import gseapy as gp
from django.contrib import messages

from ..constants.colors import PROTZILLA_DISCRETE_COLOR_SEQUENCE


def go_enrichment_bar_plot(
    input_df, categories, top_terms, cutoff, title="", colors=None
):
    if input_df is None or len(input_df) == 0 or input_df.empty:
        msg = "No data to plot. Please check your input data or run enrichment again."
        return [dict(messages=[dict(level=messages.ERROR, msg=msg)])]

    # remove all Gene_sets that are not in categories
    df = input_df[input_df["Gene_set"].isin(categories)]

    if colors == "" or colors is None or len(colors) == 0:
        colors = PROTZILLA_DISCRETE_COLOR_SEQUENCE

    size_y = top_terms * 0.5 * len(categories)
    ax = gp.barplot(
        df=df,
        column="Adjusted P-value",
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
