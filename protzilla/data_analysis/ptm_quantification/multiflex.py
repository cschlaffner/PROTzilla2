import logging
import time
from collections import Counter
from copy import copy
from math import sqrt

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import Normalize
from numpy import arange, array, flip, nan, ones
from plotly.figure_factory import create_dendrogram
from plotly.graph_objects import Heatmap
from plotly.subplots import make_subplots
from pydeseq2.preprocessing import deseq2_norm
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import cdist
from seaborn import color_palette, histplot

from protzilla.data_analysis.ptm_quantification.flexiquant import flexiquant_lf
from protzilla.utilities.utilities import fig_to_base64


def multiflex_lf(
    peptide_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    reference_group: str,
    num_init: int = 30,
    mod_cutoff: float = 0.5,
    imputation_cosine_similarity: float = 0.98,
    deseq2_normalization: bool = True,
    colormap: int = 1,
):
    """
    Quantifies the extent of protein modifications in proteomics data by using robust linear regression to compare modified and unmodified peptide precursors
    and facilitates the analysis of modification dynamics and coregulated modifications across large datasets without the need for preselecting specific proteins.

    Parts of the implementation have been adapted from https://gitlab.com/SteenOmicsLab/multiflex-lf.
    """

    # get current system time to track the runtime
    start = time.time()

    # create dataframe input for multiflex-lf
    df_intens_matrix_all_proteins = pd.DataFrame(
        {
            "ProteinID": peptide_df["Protein ID"],
            "PeptideID": peptide_df["Sequence"],
            "Sample": peptide_df["Sample"],
            "Intensity": peptide_df["Intensity"],
        }
    )

    # add Group column to input
    df_intens_matrix_all_proteins = pd.merge(
        df_intens_matrix_all_proteins, metadata_df[["Sample", "Group"]], on="Sample"
    )

    # check if reference identifier exists in Group column
    if str(reference_group) not in set(
        df_intens_matrix_all_proteins["Group"].astype(str)
    ):
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg=f"Reference group {reference_group} not found in metadata.",
                )
            ],
        )

    df_intens_matrix_all_proteins = (
        df_intens_matrix_all_proteins.dropna(subset=["Intensity"])
        .groupby(["ProteinID", "PeptideID", "Group", "Sample"])["Intensity"]
        .apply(max)
        .unstack(level=["Group", "Sample"])
        .T
    )
    df_intens_matrix_all_proteins = df_intens_matrix_all_proteins.set_index(
        [
            df_intens_matrix_all_proteins.index.get_level_values("Group"),
            df_intens_matrix_all_proteins.index.get_level_values("Sample"),
        ]
    )
    df_intens_matrix_all_proteins = df_intens_matrix_all_proteins.sort_index(
        axis=0
    ).sort_index(axis=1)

    # create a list of all proteins in the dataset
    list_proteins = (
        df_intens_matrix_all_proteins.columns.get_level_values("ProteinID")
        .unique()
        .sort_values()
    )

    df_diff_modified = pd.DataFrame()
    df_raw_scores = pd.DataFrame()
    df_removed_peptides = pd.DataFrame()
    df_RM_scores = pd.DataFrame()

    skipped_proteins = []

    for protein in list_proteins:
        flexi_result = flexiquant_lf(
            peptide_df, metadata_df, reference_group, protein, num_init, mod_cutoff
        )

        if any(
            [
                message
                for message in flexi_result["messages"]
                if message["level"] == logging.ERROR
            ]
        ):
            skipped_proteins.append(protein)
            continue

        protein_raw_scores = flexi_result["raw_scores"]
        protein_raw_scores = protein_raw_scores.T
        protein_raw_scores.columns = protein_raw_scores.loc["Sample"]
        protein_raw_scores["ProteinID"] = protein
        protein_raw_scores.drop(
            index=[
                "Sample",
                "Slope",
                "R2 model",
                "R2 data",
                "Reproducibility factor",
                "Group",
            ],
            inplace=True,
        )
        protein_raw_scores = (
            protein_raw_scores.reset_index()
            .rename(columns={"index": "PeptideID"})
            .set_index(["ProteinID", "PeptideID"])
        )
        df_raw_scores = pd.concat([df_raw_scores, protein_raw_scores])

        protein_diff_modified = flexi_result["diff_modified"]
        protein_diff_modified.drop(columns=["Group"], inplace=True)
        protein_diff_modified = protein_diff_modified.T
        protein_diff_modified.columns = protein_diff_modified.loc["Sample"]
        protein_diff_modified["ProteinID"] = protein
        protein_diff_modified.drop(index="Sample", inplace=True)
        protein_diff_modified = (
            protein_diff_modified.reset_index()
            .rename(columns={"index": "PeptideID"})
            .set_index(["ProteinID", "PeptideID"])
        )
        df_diff_modified = pd.concat([df_diff_modified, protein_diff_modified])

        protein_removed_peptides = flexi_result["removed_peptides"]
        protein_removed_peptides.remove("Sample")
        protein_removed_peptides_df = pd.DataFrame(
            {"ProteinID": protein, "PeptideID": protein_removed_peptides}
        )
        df_removed_peptides = pd.concat(
            [df_removed_peptides, protein_removed_peptides_df]
        )

        protein_RM_scores = flexi_result["RM_scores"]
        protein_RM_scores = protein_RM_scores.T
        protein_RM_scores.columns = pd.MultiIndex.from_arrays(
            [protein_RM_scores.loc["Group"], protein_RM_scores.loc["Sample"]],
            names=["Group", "Sample"],
        )
        protein_RM_scores["ProteinID"] = protein
        protein_RM_scores.drop(
            index=[
                "Sample",
                "Slope",
                "R2 model",
                "R2 data",
                "Reproducibility factor",
                "Group",
            ],
            inplace=True,
        )
        protein_RM_scores = (
            protein_RM_scores.reset_index()
            .rename(columns={"index": "PeptideID"})
            .set_index(["ProteinID", "PeptideID"])
        )
        df_RM_scores = pd.concat([df_RM_scores, protein_RM_scores])

    if df_RM_scores.empty:
        return dict(
            messages=[
                dict(
                    level=logging.WARNING,
                    msg="RM scores were not computed! Intensities of at least 5 peptides per protein have to be given!",
                )
            ],
        )

    # list of all groups for creation the distribution plots and protein-wise heatmaps
    list_groups = list(set(df_RM_scores.columns.get_level_values("Group")))
    list_groups.sort()

    rm_score_dist_plots = fig_to_base64(
        create_RM_score_distribution_plots(df_RM_scores, list_groups)
    )

    # define the colormap for the heatmap as specified by the user
    if colormap == 1:
        color_map = "RdBu"
    elif colormap == 2:
        color_map = "PiYG"
    elif colormap == 3:
        color_map = "PRGn"
    elif colormap == 3:
        color_map = "BrBG"
    elif colormap == 4:
        color_map = "PuOr"
    elif colormap == 5:
        color_map = "RdGy"
    elif colormap == 6:
        color_map = "RdYlGn"
    elif colormap == 7:
        color_map = "RdYlBu"

    # check if colormap is valid
    try:
        custom_cmap = copy(plt.get_cmap(color_map))
    except ValueError:
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg="Invalid color map!\n Please choose a valid color map. See: https://matplotlib.org/stable/tutorials/colors/colormaps.html",
                )
            ],
        )

    # create title page
    fig = plt.figure(figsize=(1, 1))
    plt.title("Heatmaps of RM scores of multiFLEX-LF", fontsize=20)
    plt.axis("off")
    plt.close()

    # define color map for the heatmaps
    custom_cmap = copy(plt.get_cmap(color_map))
    # missing values are set to black
    custom_cmap.set_bad("black", 1.0)
    custom_norm = Normalize(vmin=0, vmax=mod_cutoff * 2)

    # sort the proteins descending by number of peptides and samples with a RM scores below the modification cutoff
    sorted_proteins = list(
        df_RM_scores[df_RM_scores < mod_cutoff]
        .count(axis=1)
        .groupby("ProteinID")
        .sum()
        .sort_values(ascending=False)
        .index
    )

    heatmap_plots = []
    # go through all protein in the sorted order
    for protein_id in sorted_proteins:
        # dataframe of the RM scores of the current protein
        df_RM_scores_protein = df_RM_scores.loc[protein_id]

        # skip the protein, if dataframe empty
        if df_RM_scores_protein.empty:
            continue

        # ignore nan-slice warnings
        # with warnings.catch_warnings():
        #     warnings.filterwarnings("ignore", r"All-NaN (slice|axis) encountered")

        # create heatmap of the current protein
        heatmap_plots.append(
            create_heatmap(df_RM_scores_protein, protein_id, color_map, mod_cutoff)
        )

    # keep only peptides that have RM scores in at least two groups
    to_remove = df_RM_scores.loc[
        df_RM_scores.groupby("Group", axis=1).count().replace(0, nan).count(axis=1) < 2
    ].index
    df_RM_scores_all_proteins_reduced = df_RM_scores.drop(to_remove, axis=0)
    removed_peptides = pd.DataFrame(list(to_remove))
    to_remove = pd.DataFrame()

    # impute missing values for clustering
    (
        df_RM_scores_all_proteins_reduced,
        df_RM_scores_all_proteins_imputed,
        removed,
    ) = missing_value_imputation(
        df_RM_scores_all_proteins_reduced, round(1 - imputation_cosine_similarity, 3)
    )
    removed_peptides = pd.concat([removed_peptides, removed])
    removed = pd.DataFrame()

    # check if RM scores dataframe is empty, if true return error and finish analysis
    if df_RM_scores_all_proteins_imputed.empty:
        # add removed peptides to csv file
        if len(removed_peptides) > 0:
            removed_peptides.columns = ["ProteinID", "PeptideID"]
            removed_peptides = removed_peptides.set_index(["ProteinID"])

        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg="Imputation of RM scores for clustering was unsuccessful! Too many missing values in the data!",
                )
            ],
            removed_peptides=removed_peptides,
        )

    if deseq2_normalization:
        groups = pd.DataFrame(list(df_RM_scores.columns))
        groups.columns = ["Group", "Sample"]
        df_normalization = df_RM_scores_all_proteins_imputed.copy()

        # one column per peptide, one row per sample
        df_normalization = df_normalization.T
        df_normalization = df_normalization.astype(float)

        # apply normalization
        df_normalization = deseq2_norm(df_normalization)[0]

        # transpose back
        df_normalization = df_normalization.T

        # keep only normalized RM scores which were not missing before the previous imputation
        # then reimpute the missing values
        df_RM_scores_all_proteins_reduced = df_normalization[
            df_RM_scores_all_proteins_reduced.isna() == False
        ]
        df_RM_scores_all_proteins_reduced = round(df_RM_scores_all_proteins_reduced, 5)

        # impute missing values again
        (
            df_RM_scores_all_proteins_reduced,
            df_RM_scores_all_proteins_imputed,
            removed,
        ) = missing_value_imputation(
            df_RM_scores_all_proteins_reduced,
            round(1 - imputation_cosine_similarity, 5),
        )
        # dataframe of peptides that were removed during imputation
        removed_peptides = removed_peptides.append(removed)
        removed = pd.DataFrame()

        rm_score_dist_plots = fig_to_base64(
            create_RM_score_distribution_plots(
                df_RM_scores_all_proteins_reduced, list_groups
            )
        )

    if len(removed_peptides) > 0:
        removed_peptides.columns = ["ProteinID", "PeptideID"]
        removed_peptides = removed_peptides.set_index(["ProteinID"])

    linkage_matrix = linkage(
        df_RM_scores_all_proteins_imputed,
        metric=lambda u, v: RM_score_distance(u, v, mod_cutoff),
        method="average",
    )

    # create plotly figure
    (
        peptide_clustering_fig,
        array_RM_scores_all_proteins_reduced,
        ordered_peptides,
    ) = peptide_clustering(
        df_RM_scores_all_proteins_reduced,
        linkage_matrix,
        mod_cutoff,
        color_map,
        ["black"] * 8,
        None,
        [],
    )

    # create output of the RM scores in same order as in the heatmap
    output_df = pd.DataFrame(flip(array_RM_scores_all_proteins_reduced, axis=0))
    output_df.columns = df_RM_scores_all_proteins_reduced.columns.get_level_values(
        "Sample"
    )
    # add the ID column
    output_df.index = pd.MultiIndex.from_tuples(
        flip(array(df_RM_scores_all_proteins_reduced.index)[ordered_peptides]),
        names=("ProteinID", "PeptideID"),
    )
    output_df = output_df.reset_index()
    output_df.index.names = ["ID"]

    end = time.time()
    message = dict(
        level=logging.INFO,
        msg=f"Finished with MultiFLEX-LF analysis in ~{end-start:.1f} seconds.",
    )

    return dict(
        RM_scores_clustered=output_df,
        diff_modified=df_diff_modified,
        raw_scores=df_raw_scores,
        removed_peptides=removed_peptides,
        RM_scores=df_RM_scores,
        plots=[rm_score_dist_plots, peptide_clustering_fig] + heatmap_plots,
        messages=[message],
    )


def create_RM_score_distribution_plots(df_RM_scores, list_groups):
    """
    Constructs a figure of distribution plots of the RM scores. For every group a seperate plot is created
    with the different samples in different colors.
    """

    # initialize the figure with a size that accounts for 7ptx7pt plots of every sample group
    fig_size = sqrt(len(list_groups))

    if fig_size % 1 != 0:
        fig_size = int(int(fig_size) + 1)
    else:
        fig_size = int(fig_size)

    fig = plt.figure(figsize=(7 * fig_size, 7 * fig_size))

    # list of colors for the color coding of the different samples in one group
    colors_list = color_palette(
        "husl",
        Counter(df_RM_scores.columns.get_level_values("Group")).most_common(1)[0][1],
    )  # int(df_group_all_prots.shape[1]/2)

    # create the distribution plots for every group and apply kernel density estimation if possible
    i = 1
    for group in list_groups:
        df_group = df_RM_scores[group]

        ax = fig.add_subplot(fig_size, fig_size, i)

        try:
            histplot(
                df_group,
                ax=ax,
                kde=True,
                stat="count",
                bins=30,
                palette=colors_list[: df_group.shape[1]],
                edgecolor=None,
            )
        except:
            histplot(
                df_group,
                ax=ax,
                kde=False,
                stat="count",
                bins=30,
                palette=colors_list[: df_group.shape[1]],
                edgecolor=None,
            )

        plt.xticks(fontsize=8)
        plt.yticks(fontsize=8)
        plt.xlim(0, 3)
        plt.title("Group: " + group, fontsize=16)
        plt.xlabel("RM score")

        # show sample legend if group contains 10 samples or less
        if df_group.shape[1] > 10:
            plt.legend([], [], frameon=False)

        plt.tight_layout(h_pad=2)

        i += 1

    fig.suptitle("Distribution of RM scores of FLEXIQuant-LF ", fontsize=20)
    plt.subplots_adjust(top=0.90)

    plt.close()

    return fig


def create_heatmap(
    df_RM_scores: pd.DataFrame, protein_id: str, color_scale: str, mod_cutoff: float
):
    """
    Constructs a heatmap of the RM scores for a protein
    """

    # Create Plotly subplots figure
    fig = make_subplots(
        rows=1,
        cols=1,  # +1 for colorbar
        shared_yaxes=True,
        horizontal_spacing=0.01,
    )

    df_RM_scores = df_RM_scores.astype(float)
    fig.add_trace(
        Heatmap(
            z=df_RM_scores.values,
            x=df_RM_scores.columns.get_level_values("Sample"),
            y=df_RM_scores.index.get_level_values("PeptideID"),
            zmin=0,
            zmax=mod_cutoff * 2,
            hovertemplate="Sample: %{x}<br />Peptide: %{y}<br />RM score: %{z}",
            colorscale=color_scale,
            showscale=True,
            colorbar=dict(
                title="RM score",
                titleside="top",
                tickmode="array",
                thicknessmode="pixels",
                thickness=25,
                len=1,
                x=1.05,
                ticks="outside",
                dtick=5,
            ),
        ),
    )

    # Update layout
    fig.update_layout(
        title_text=f"Protein: {protein_id}",
        title_x=0.5,
        height=20 * df_RM_scores.shape[0] + 200,  # Adjust height to fit
        autosize=True,
        xaxis_title="",
        yaxis_title="Peptides",
        yaxis_nticks=df_RM_scores.shape[0],  # Adjust number of ticks
    )

    return fig


def missing_value_imputation(df_RM_scores: pd.DataFrame, max_cos_dist: float):
    """
    Impute missing values by calculating the median of the RM scores of all peptides
    with a cosine distance (i.e. 1 - cosine similarity) of at most max_cos_dist from
    the current peptide. If not all missing values of a peptide were imputed, it is
    removed from further analysis.
    """

    # copy df
    df_RM_scores_imputed = df_RM_scores.copy()

    for peptide in df_RM_scores.index:
        # get RM scores of the current peptide
        df_RM_scores_pep = df_RM_scores.loc[peptide]

        # skip if no missing value for peptide
        if not df_RM_scores_pep.isna().any():
            continue

        # remove NaN values
        df_RM_scores_pep = pd.DataFrame(df_RM_scores_pep.dropna())

        # get all other peptides and keep only samples that have a RM scores for the current peptides
        df_RM_scores_other_peps = df_RM_scores[df_RM_scores_pep.index].drop(
            peptide, axis=0
        )

        # calculate all pairwise cosine distances between the current peptide and all other
        cos_dist_other_peps = cdist(
            df_RM_scores_pep.T, df_RM_scores_other_peps, "cosine"
        )[0]

        # get the index of the closest peptides
        index_impute = df_RM_scores_other_peps[
            cos_dist_other_peps <= max_cos_dist
        ].index

        # skip peptide if less than 2 close peptides were found
        if len(index_impute) < 2:
            continue

        # calculate the median RM scores of the closest peptides
        df_imputation_values = (
            df_RM_scores.loc[index_impute].median().drop(df_RM_scores_pep.index)
        )

        # replace the missing values with the calculated values
        df_RM_scores_imputed.loc[
            peptide, df_imputation_values.index
        ] = df_imputation_values

    # remove all peptides that still have missing values
    remove_nans = df_RM_scores_imputed[df_RM_scores_imputed.isna().any(axis=1)].index
    df_RM_scores_imputed = df_RM_scores_imputed.drop(remove_nans, axis=0)
    df_RM_scores = df_RM_scores.drop(remove_nans, axis=0)

    return df_RM_scores, df_RM_scores_imputed, pd.DataFrame(list(remove_nans))


def RM_score_distance(u: float, v: float, mod_cutoff: float):
    """
    Calculation of the customized Manhattan distance between the arrays of RM scores u and v
    """
    # initialize distance vector
    if len(u) == len(v):
        dist = ones(len(u))
    else:
        return

    # calculate absolute differences between the elements of u and v
    for i in range(len(dist)):
        x = u[i]
        y = v[i]

        # penalize jumps from below to above the modification cutoff
        if (x < mod_cutoff and y >= mod_cutoff) or (x >= mod_cutoff and y < mod_cutoff):
            dist[i] = abs(x - y) + 1
        else:
            dist[i] = abs(x - y)

    # return sum of the penalized absolute differences
    return dist.sum()


def peptide_clustering(
    df_RM_scores: pd.DataFrame,
    linkage_matrix: pd.DataFrame,
    mod_cutoff: float,
    cmap: str,
    colors: list[str],
    clust_threshold: float,
    clust_ids: list,
):
    """
    Clustering results are saved as interactive HTML file with the dendrogram and the heatmap.
    """
    # initialize plotly figure and create the dendrogram based on the linkage matrix
    plotly_figure = create_dendrogram(
        df_RM_scores.astype(float),
        orientation="right",
        linkagefun=lambda x: linkage_matrix,
        colorscale=colors,
        color_threshold=clust_threshold,
    )

    # set x-axis of the dendrogram to x2 (axis nr. 2)
    for i in range(len(plotly_figure["data"])):
        plotly_figure["data"][i]["xaxis"] = "x2"

    # get order of the peptides in the dendrogram
    clust_leaves = plotly_figure["layout"]["yaxis"]["ticktext"]
    clust_leaves = list(map(int, clust_leaves))

    # create numpy array from the RM scores dataframe
    # and sort the peptides by the order in the dendrogram
    heat_data = df_RM_scores.to_numpy()
    heat_data = heat_data[clust_leaves, :]

    # define row and column labels for the heatmap
    row_names = [str(i[0]) + "<br />Peptide: " + str(i[1]) for i in df_RM_scores.index]
    row_names = list(array(row_names)[clust_leaves])
    col_names = list(df_RM_scores.columns.get_level_values(1))

    if len(clust_ids) == 0:
        # define the row IDs shown upon hovering over the cells of the heatmap
        clust_id = array(
            [[i] * df_RM_scores.shape[1] for i in range(len(clust_leaves) - 1, -1, -1)]
        )
    else:
        ## if cluster ids given add the cluster id to the hover information
        clust_id = array(
            [
                [str(i) + "<br />Cluster: " + str(clust_ids[i])] * df_RM_scores.shape[1]
                for i in range(len(clust_leaves) - 1, -1, -1)
            ]
        )

    # create heatmap
    heatmap = Heatmap(
        z=heat_data,
        colorscale=cmap,
        zmin=0,
        zmax=mod_cutoff * 2,
        customdata=clust_id,
        hovertemplate="Sample: %{x}<br />Protein: %{y}<br />RM score: %{z}<br />ID: %{customdata}",
        colorbar=dict(
            title="RM score",
            titleside="top",
            tickmode="array",
            thicknessmode="pixels",
            thickness=25,
            lenmode="pixels",
            len=250,
            yanchor="top",
            y=1,
            x=1.05,
            ticks="outside",
            dtick=5,
        ),
    )

    # align y-axis of heatmap to dendrogram
    heatmap["y"] = plotly_figure["layout"]["yaxis"]["tickvals"]

    # add the heatmap to plotly figure plotly_figure
    plotly_figure.add_trace(heatmap)

    # edit layout of plotly_figure
    figure_width = min(max(df_RM_scores.shape[1] * 50 + 100, 500), 1500)
    plotly_figure.update_layout(autosize=True, height=900, font={"size": 11})

    # amount of the figure size used for the dendrogram
    dendrogram_width = 100 / figure_width

    # update x-axis of the heatmap
    plotly_figure.update_layout(
        xaxis={
            "domain": [dendrogram_width, 1],
            "mirror": False,
            "showgrid": False,
            "showline": False,
            "zeroline": False,
            "showticklabels": True,
            "ticks": "outside",
            "ticktext": col_names,  # list of sample names
            "tickvals": arange(0, len(col_names)),
        }
    )

    # update x-axis (xaxis2) of the dendrogram
    plotly_figure.update_layout(
        xaxis2={
            "domain": [0, dendrogram_width],
            "mirror": False,
            "showgrid": False,
            "showline": False,
            "zeroline": False,
            "showticklabels": True,
            "ticks": "",
        }
    )

    # update y-axis of the heatmap
    plotly_figure.update_layout(
        yaxis={
            "domain": [0, 1],
            "mirror": False,
            "showgrid": False,
            "showline": False,
            "zeroline": False,
            "showticklabels": False,
            "ticks": "",
            "side": "right",
            "ticktext": row_names,  # list of the peptides
        }
    )

    # set plot title and axes lables
    plotly_figure.update_layout(
        title="Clustered Heatmap of RM scores",
        xaxis_title="Sample",
        yaxis_title="Peptides",
        xaxis2_title="",
        template="plotly_white",
    )

    # return the figure, the matrix of the RM scores in clustering order and the clustering order of the peptides
    return plotly_figure, heat_data, clust_leaves
