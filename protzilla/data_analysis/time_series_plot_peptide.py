import pandas as pd
import plotly.graph_objects as go
from scipy import stats
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

from protzilla.utilities.transform_dfs import is_long_format, long_to_wide_time

# Define color constants
PROTZILLA_DISCRETE_COLOR_SEQUENCE = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#19D3F3", "#E763FA", "#FECB52", "#FFA15A", "#FF6692", "#B6E880"]
colors = {
    "plot_bgcolor": "white",
    "gridcolor": "#F1F1F1",
    "linecolor": "#F1F1F1",
    "annotation_text_color": "#ffffff",
    "annotation_proteins_of_interest": "#4A536A",
}

def time_series_plot_peptide(
    input_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    protein_group: str,
    similarity: float = 1.0,
    similarity_measure: str = "euclidean distance",
) -> dict:
    """
    A function to create a graph visualising protein quantifications across all samples
    as a line diagram using time. It's possible to select one proteingroup
    that will be displayed in orange and choose a similarity measurement with a similarity score
    to get all proteingroups that are similar displayed in another color in this line diagram.
    All other proteingroups are displayed in the background as a grey polygon.

    :param input_df: A dataframe in protzilla wide format, where each row
        represents a sample and each column represents a feature.
    :param metadata_df: A dataframe containing the metadata of the samples.
    :param protein_group: Protein IDs as the columnheader of the dataframe
    :param similarity_measure: method to compare the chosen proteingroup with all others. The two
        methods are "cosine similarity" and "euclidean distance".
    :param similarity: similarity score of the chosen similarity measurement method.

    :return: returns a dictionary containing a list with a plotly figure and/or a list of messages
    """

    input_df = pd.merge(
        left=input_df,
        right=metadata_df[["Sample", "Time"]],
        on="Sample",
        copy=False,
    )

    wide_df = input_df.interpolate(method='linear', axis=0)
    wide_df = long_to_wide_time(wide_df) if is_long_format(wide_df) else  wide_df


    if protein_group not in wide_df.columns:
        raise ValueError("Please select a valid protein group.")
    elif similarity_measure == "euclidean distance" and similarity < 0:
        raise ValueError(
            "Similarity for euclidean distance should be greater than or equal to 0."
        )
    elif similarity_measure == "cosine similarity" and (
            similarity < -1 or similarity > 1
    ):
        raise ValueError("Similarity for cosine similarity should be between -1 and 1")

    fig = go.Figure()

    color_mapping = {
        "A": PROTZILLA_DISCRETE_COLOR_SEQUENCE[0],
        "C": PROTZILLA_DISCRETE_COLOR_SEQUENCE[1],
    }

    lower_upper_x = []
    lower_upper_y = []

    lower_upper_x.append(wide_df.index[0])
    lower_upper_y.append(wide_df.iloc[0].min())

    for index, row in wide_df.iterrows():
        lower_upper_x.append(index)
        lower_upper_y.append(row.max())

    for index, row in reversed(list(wide_df.iterrows())):
        lower_upper_x.append(index)
        lower_upper_y.append(row.min())

    fig.add_trace(
        go.Scatter(
            x=lower_upper_x,
            y=lower_upper_y,
            fill="toself",
            name="Intensity Range",
            line=dict(color="silver"),
        )
    )

    similar_groups = []
    for group_to_compare in wide_df.columns:
        if group_to_compare != protein_group:
            if similarity_measure == "euclidean distance":
                distance = euclidean_distances(
                    stats.zscore(wide_df[protein_group]).values.reshape(1, -1),
                    stats.zscore(wide_df[group_to_compare]).values.reshape(1, -1),
                )[0][0]
            else:
                distance = cosine_similarity(
                    stats.zscore(wide_df[protein_group]).values.reshape(1, -1),
                    stats.zscore(wide_df[group_to_compare]).values.reshape(1, -1),
                )[0][0]
            if similarity_measure == "euclidean distance":
                if distance <= similarity:
                    similar_groups.append(group_to_compare)
            else:
                if distance >= similarity:
                    similar_groups.append(group_to_compare)

    for group in similar_groups:
        fig.add_trace(
            go.Scatter(
                x=wide_df.index,
                y=wide_df[group],
                mode="lines",
                name=group[:15] + "..." if len(group) > 15 else group,
                line=dict(color=PROTZILLA_DISCRETE_COLOR_SEQUENCE[1]),
                showlegend=len(similar_groups) <= 7,
            )
        )

    if len(similar_groups) > 7:
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                line=dict(color=PROTZILLA_DISCRETE_COLOR_SEQUENCE[1]),
                name="Similar Protein Groups",
            )
        )

    formatted_protein_name = (
        protein_group[:15] + "..." if len(protein_group) > 15 else protein_group
    )
    fig.add_trace(
        go.Scatter(
            x=wide_df.index,
            y=wide_df[protein_group],
            mode="lines",
            name=formatted_protein_name,
            line=dict(color=PROTZILLA_DISCRETE_COLOR_SEQUENCE[2]),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color=color_mapping.get("A")),
            name="Intensity",
        )
    )
    fig.update_layout(
        title=f"Time Series of {formatted_protein_name} in all samples",
        plot_bgcolor=colors["plot_bgcolor"],
        xaxis_gridcolor=colors["gridcolor"],
        yaxis_gridcolor=colors["gridcolor"],
        xaxis_linecolor=colors["linecolor"],
        yaxis_linecolor=colors["linecolor"],
        xaxis_title="Time",
        yaxis_title="Intensity",
        legend_title="Legend",
        xaxis=dict(
            tickmode="array",
            tickangle=0,
            tickvals=wide_df.index,
            ticktext=[wide_df["Time"].unique() for wide_df["Time"] in wide_df.index],
        ),
        autosize=True,
        margin=dict(l=100, r=300, t=100, b=100),
        legend=dict(
            x=1.05,
            y=1,
            bgcolor="rgba(255, 255, 255, 0.5)",
            orientation="v",
        ),
    )

    return dict(plots=[fig])