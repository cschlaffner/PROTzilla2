import logging

import matplotlib
import pandas as pd
from numpy import array, nan, sqrt, square
from scipy.stats import f, median_abs_deviation
from sklearn import linear_model

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import gridspec
from seaborn import distplot, diverging_palette, lineplot, scatterplot

from protzilla.utilities.utilities import fig_to_base64

CONFIDENCE_BAND_ALPHA = 0.3


def flexiquant_lf(
    peptide_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    reference_group: str,
    protein_id: str,
    grouping_column: str,
    num_init: int = 50,
    mod_cutoff: float = 0.5,
) -> dict:
    """
    FLEXIQuant-LF is a method to quantify protein modification extent in label-free proteomics data.

    Parts of the implementation have been adapted from https://github.com/SteenOmicsLab/FLEXIQuantLF.

    :param peptide_df: DataFrame containing peptide intensities.
    :param metadata_df: DataFrame containing metadata.
    :param reference_group: Name of the reference group.
    :param protein_id: Protein ID that should be analysed.
    :param num_init: Number of initializations for RANSAC regression.
    :param mod_cutoff: RM score cutoff value for modified peptides.
    """

    df = peptide_df[peptide_df["Protein ID"] == protein_id].pivot_table(
        index="Sample", columns="Sequence", values="Intensity", aggfunc="first"
    )
    df.reset_index(inplace=True)

    df = pd.merge(
        left=df,
        right=metadata_df[["Sample", grouping_column]],
        on="Sample",
        copy=False,
    )

    if not grouping_column in df:
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg=f"No {grouping_column} column found in provided dataframe.",
                )
            ]
        )

    # delete columns where all entries are nan
    df.dropna(how="all", axis=1, inplace=True)

    if reference_group not in df[grouping_column].unique():
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg=f"Reference sample '{reference_group}' not found in provided data.",
                )
            ]
        )
    else:
        # filter dataframe for controls
        df_control = df[df[grouping_column] == reference_group]

    # get modified peptides
    modified = []
    for elm in df_control.columns:
        if "ph" in elm or "ac" in elm or "gly" in elm:
            modified.append(elm)

    # delete modified peptides
    df_control: pd.DataFrame = df_control.drop(modified, axis=1)
    df.drop(modified, inplace=True, axis=1)

    # delete Group column
    group_column = df[grouping_column]
    df_control.drop(grouping_column, axis=1, inplace=True)
    df.drop(grouping_column, axis=1, inplace=True)

    sample_column = df["Sample"]

    # calculate median intensities for unmodified peptides of control
    median_intensities = df_control.median(axis=0)

    # initiate empty lists to save results of linear regressions
    slope_list = []
    r2_score_list_model = []
    r2_score_list_data = []
    reproducibility_list = []

    df_distance_RL = df.copy()

    regression_plots = []

    plot_dict = {}

    for idx, row in df.iterrows():
        df_train = pd.DataFrame(
            {"Sample intensity": row, "Reference intensity": median_intensities}
        )

        df_train.dropna(inplace=True)

        df_train.sort_index(inplace=True, axis=0)

        # if number of peptides is smaller than 5, skip sample and continue with next interation
        if len(df_train) < 5:
            # set all metrices to nan
            df_distance_RL.loc[idx] = nan
            df_train["CB low"] = nan
            df_train["CB high"] = nan
            slope_list.append(nan)
            r2_score_list_model.append(nan)
            r2_score_list_data.append(nan)
            reproducibility_list.append(nan)

            continue

        # initiate empty list to save results of linear regression
        list_model_slopes = []
        list_r2_model = []
        list_r2_data = []
        all_iter_slopes = []
        all_iter_r2_data = []
        all_iter_r2_model = []

        # set training data
        X = array(df_train["Reference intensity"]).reshape(-1, 1)
        y = df_train["Sample intensity"]

        sq_mad = square(median_abs_deviation(df_train["Sample intensity"]))

        for i in range(num_init):
            ransac_model = linear_model.RANSACRegressor(
                estimator=linear_model.LinearRegression(fit_intercept=False, n_jobs=-2),
                max_trials=1000,
                stop_probability=1,
                min_samples=0.5,
                residual_threshold=sq_mad,
            )

            ransac_model.fit(X, y)

            slope = float(ransac_model.estimator_.coef_)

            inlier_mask = ransac_model.inlier_mask_

            df_train["Outlier"] = ~inlier_mask.astype(bool)

            # calculate R2 score based on inliers
            df_train_inlier = df_train[~df_train["Outlier"]]
            X_inlier = array(df_train_inlier["Reference intensity"]).reshape(-1, 1)
            y_inlier = df_train_inlier["Sample intensity"]
            r2_score_model = round(ransac_model.score(X_inlier, y_inlier), 4)
            r2_score_data = round(ransac_model.score(X, y), 4)

            list_model_slopes.append(slope)
            list_r2_model.append(r2_score_model)
            list_r2_data.append(r2_score_data)

        all_iter_slopes.append(list_model_slopes)
        all_iter_r2_model.append(list_r2_model)
        all_iter_r2_data.append(list_r2_data)

        # determine best model based on r2 scores
        best_model = list_r2_model.index(max(list_r2_model))

        # save slope of best model to slope_list
        slope_list.append(list_model_slopes[best_model])
        slope = list_model_slopes[best_model]

        # calculate reproducibility factor and save to list
        series_slopes = pd.Series(list_model_slopes)
        reproducibility_factor = max(series_slopes.value_counts()) / num_init
        reproducibility_list.append(reproducibility_factor)

        # get r2 scores of best model
        r2_score_model = list_r2_model[best_model]
        r2_score_data = list_r2_data[best_model]

        # save best r2 score to lists
        r2_score_list_model.append(r2_score_model)
        r2_score_list_data.append(r2_score_data)

        # calculate confidence band
        alpha = 0.3
        df_distance_RL, df_train = calculate_confidence_band(
            slope,
            median_intensities,
            df_train,
            X,
            y,
            row,
            idx,
            df_distance_RL,
            CONFIDENCE_BAND_ALPHA,
        )

        # plot scatter plot with regression line

        plot_dict[sample_column[idx]] = [
            df_train,
            idx,
            r2_score_model,
            r2_score_data,
            slope,
            alpha,
        ]

    df_distance_RL["Slope"] = slope_list
    df_raw_scores = calc_raw_scores(df_distance_RL, median_intensities)

    # Assume df_raw_scores is your input DataFrame
    # calculate MAD per sample
    df_raw_scores.drop("Slope", axis=1, inplace=True)
    df_raw_scores_T = df_raw_scores.T
    df_raw_scores_T = df_raw_scores_T.apply(pd.to_numeric, errors="coerce")
    mad = df_raw_scores_T.mad(axis=0)
    median = df_raw_scores_T.median(axis=0)

    # calculate cutoff value for each time point (> 3*MAD)
    cutoff = median + 3 * mad

    # remove peptides with raw scores > cutoff for each sample
    df_raw_scores_T_cutoff = df_raw_scores_T[
        round(df_raw_scores_T, 5) <= round(cutoff, 5)
    ]
    removed = pd.Series(
        df_raw_scores_T_cutoff.index[df_raw_scores_T_cutoff.isna().all(axis=1)]
    )
    df_raw_scores_T_cutoff.dropna(axis=0, how="all", inplace=True)
    df_raw_scores_cutoff = df_raw_scores_T_cutoff.T

    # apply t3median normalization to calculate RM scores
    df_RM = normalize_t3median(df_raw_scores_cutoff)

    # check if peptides are modified (RM score below modification cutoff)
    df_RM_mod = df_RM < mod_cutoff

    df_raw_scores["Slope"] = slope_list
    df_raw_scores["R2 model"] = r2_score_list_model
    df_raw_scores["R2 data"] = r2_score_list_data
    df_raw_scores["Reproducibility factor"] = reproducibility_list

    df_RM["Slope"] = slope_list
    df_RM["R2 model"] = r2_score_list_model
    df_RM["R2 data"] = r2_score_list_data
    df_RM["Reproducibility factor"] = reproducibility_list

    # add Group column again
    df_raw_scores[grouping_column] = group_column
    df_RM[grouping_column] = group_column
    df_RM_mod[grouping_column] = group_column

    # add Sample column again
    df_raw_scores["Sample"] = sample_column
    df_RM["Sample"] = sample_column
    df_RM_mod["Sample"] = sample_column

    for sample in sample_column:
        if sample in plot_dict:
            regression_plots.append(
                fig_to_base64(
                    create_regression_plots(
                        *plot_dict[sample],
                        sample_column,
                        df_RM[df_RM["Sample"] == sample].iloc[0],
                        mod_cutoff=mod_cutoff,
                        grouping_column=grouping_column,
                    )
                )
            )

    messages = []
    if len(regression_plots) == 0:
        messages.append(
            dict(
                level=logging.WARNING,
                msg="No samples were processed. This is probably due to the fact that there are not enough valid peptides in the samples.",
            )
        )
    else:
        if len(regression_plots) == len(sample_column):
            messages.append(
                dict(
                    level=logging.INFO,
                    msg=f"All {len(sample_column)} samples have been processed successfully. {len(removed)} peptides have been removed.",
                )
            )
        else:
            messages.append(
                dict(
                    level=logging.INFO,
                    msg=f"{len(regression_plots)}/{len(sample_column)} samples have been processed successfully. "
                    f"The remaining samples have been skipped due to insufficient valid peptides. {len(removed)} peptides have been removed.",
                )
            )

    return dict(
        raw_scores=df_raw_scores,
        RM_scores=df_RM[df_RM.columns[::-1]],
        diff_modified=df_RM_mod[df_RM_mod.columns[::-1]],
        removed_peptides=removed.to_list(),
        plots=regression_plots,
        messages=messages,
    )


def calculate_confidence_band(
    slope: float,
    median_int: float,
    dataframe_train: pd.DataFrame,
    X: array,
    y: pd.Series,
    row: pd.Series,
    idx: int,
    matrix_distance_RL: pd.DataFrame,
    alpha: float,
):
    """
    Calculates confidence bands arround the regression line.

    :param slope: Slope of the regression line.
    :param median_int: Median intensity of the reference group.
    :param dataframe_train: DataFrame containing the training data.
    :param X: Array containing the reference intensities.
    :param y: Series containing the sample intensities.
    :param row: Series containing the sample intensities.
    :param idx: Index of the sample.
    :param matrix_distance_RL: DataFrame containing the distances to the regression line.
    :param alpha: Alpha value for the confidence band.
    """

    # calculate predicted intensity with Reference intensity of a peptide and slope of the sample (Y hat)
    Y_pred = slope * median_int

    # calculate W
    N = len(dataframe_train)
    F = f.ppf(q=1 - alpha, dfn=2, dfd=N - 1)
    W = sqrt(2 * F)

    # calculate standard deviation (s(Y hat))
    # calculate prediction error
    error = y - Y_pred
    error.dropna(inplace=True)

    # calculate mean squared error
    MSE = sum(error.apply(square)) / (N - 1)

    # calculate mean X intensity
    X_bar = dataframe_train["Reference intensity"].mean()

    # iterate over all peptides of the sample
    CB_low = []
    CB_high = []

    # iterate through median peptide intensities
    for idx_2, elm in dataframe_train["Reference intensity"].items():
        # calculate squared distance to mean X (numerator)
        dist_X_bar = square(elm - X_bar)

        # calculate sum of squared distances to mean X(denominator)
        sum_dist_X_bar = sum(square(X - X_bar))

        # calculate standard deviation
        s = float(sqrt(MSE * ((1 / N) + (dist_X_bar / sum_dist_X_bar))))

        # calculate predicted intensity for given X
        Y_hat = slope * elm

        # calculate high and low CB values and append to list
        cb_low = Y_hat - W * s
        cb_high = Y_hat + W * s

        CB_low.append(cb_low)
        CB_high.append(cb_high)

    # calculate predicted intensities
    pred_ints = median_int * slope

    # calculate distance to regression line
    distance_RL = pred_ints - row

    # save distances in matrix_distance
    matrix_distance_RL.loc[idx] = distance_RL

    # add CBs as columns to dataframe_train
    dataframe_train["CB low"] = CB_low
    dataframe_train["CB high"] = CB_high

    return matrix_distance_RL, dataframe_train


def create_regression_plots(
    dataframe_train: pd.DataFrame,
    idx: int,
    r2_score_model: float,
    r2_score_data: float,
    slope: float,
    alpha: float,
    sample_column: pd.Series,
    rm_scores: pd.DataFrame,
    mod_cutoff: float,
    grouping_column: str,
):
    """
    Creates a scatter plot with regression line and confidence bands.

    :param dataframe_train: DataFrame containing the training data.
    :param idx: Index of the sample.
    :param r2_score_model: R2 score of the model.
    :param r2_score_data: R2 score of the data.
    :param slope: Slope of the regression line.
    :param alpha: Alpha value for the confidence band.
    :param sample_column: Series containing the sample names.
    :param rm_scores: DataFrame containing the RM scores.
    :param mod_cutoff: RM score cutoff value for modified peptides.
    :param grouping_column: Name of the grouping column.
    """

    # create new figure with two subplots
    fig = plt.figure(figsize=(16, 9))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 6])
    ax1 = plt.subplot(gs[1])
    ax0 = plt.subplot(gs[0], sharex=ax1)

    # set space between subplots
    gs.update(hspace=0.05)

    # plot histogram in upper subplot
    plt.sca(ax0)

    # add title
    plt.title("RANSAC Linear Regression of Sample " + str(sample_column[idx]))

    # plot histogram
    distplot(a=dataframe_train["Reference intensity"], bins=150, kde=False)

    # remove axis and tick labels
    plt.xlabel("")
    plt.tick_params(
        axis="x",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=True,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off

    # plot scatter plot
    plt.sca(ax1)

    rm_scores = rm_scores.drop(
        [
            "Slope",
            "R2 model",
            "R2 data",
            "Reproducibility factor",
            grouping_column,
            "Sample",
        ]
    )
    # rm_scores.dropna(inplace=True)
    rm_scores.clip(0, 1, inplace=True)

    rm_scores = rm_scores.to_frame(name="RM score")
    # outliers in dataframe_train don't have an RM score
    rm_scores = dataframe_train.merge(
        rm_scores, left_index=True, right_index=True, how="left"
    )
    rm_scores.fillna(-1, inplace=True)

    palette = diverging_palette(h_neg=0, h_pos=120, as_cmap=True, center="dark")

    def cmap(values: list[float]):
        nanIdx = set([i for i, x in enumerate(values) if x == -1])
        return [
            color if i not in nanIdx else [0.75, 0.75, 0.75, 1.0]
            for i, color in enumerate(palette(values))
        ]

    scatterplot(
        x="Reference intensity",
        y="Sample intensity",
        data=dataframe_train,
        hue=list(rm_scores.index),
        palette=cmap(scale_to_mod_cutoff(list(rm_scores["RM score"]), mod_cutoff)),
    )

    # draw regression line
    line_label = "R2 model: " + str(r2_score_model) + "\nR2 data: " + str(r2_score_data)
    max_int = dataframe_train["Reference intensity"].max()
    min_int = min(
        dataframe_train["Reference intensity"].min(),
        dataframe_train["Sample intensity"].min(),
    )
    X = [min_int - 2, max_int]
    y = [min_int - 2, slope * max_int]
    plt.plot(X, y, color="darkblue", linestyle="-", label=line_label)

    # draw confidence band
    lineplot(
        x="Reference intensity",
        y="CB low",
        data=dataframe_train,
        color="darkgreen",
        label="CB, alpha=" + str(alpha),
    )
    lineplot(
        x="Reference intensity", y="CB high", data=dataframe_train, color="darkgreen"
    )

    # set line style of CB lines to dashed
    for i in [len(ax1.lines) - 1, len(ax1.lines) - 2]:
        ax1.lines[i].set_linestyle("--")

    # create legend if sample has 20 peptides or less otherwise don't create a legend
    if len(dataframe_train) <= 20:
        # set right x axis limit
        plt.gca().set_xlim(right=1.4 * max_int)
        plt.legend()
    else:
        plt.gca().get_legend().remove()

    # set y axis label
    plt.ylabel("Intensity sample " + str(sample_column[idx]))
    plt.xlabel("Reference intensity")

    return fig


def calc_raw_scores(df_distance: pd.DataFrame, median_int: pd.Series):
    """
    Calculates raw scores for each sample based on the distance to the regression line.

    :param df_distance: DataFrame containing the distances to the regression line.
    :param median_int: Median intensity of the reference group
    """
    # copy df_distance
    df_rs = df_distance.copy()

    # iterate through rows of df_distance (samples)
    for idx, row in df_distance.iterrows():
        # extract slope
        slope = row["Slope"]

        # delete slope from row
        row.drop("Slope", inplace=True)

        # calculate raw scores
        raw_scores = 1 - row / (slope * median_int)

        # add slope to raw scores
        raw_scores["Slope"] = slope

        # replace idx row in df_RM_score with calculated raw scores
        df_rs.loc[idx] = raw_scores

    return df_rs


def normalize_t3median(dataframe: pd.DataFrame):
    """
    Applies Top3 median normalization to dataframe.
    Determines the median of the three highest values in each row and divides every value in the row by it.

    :param dataframe: DataFrame containing the data to be normalized.
    """
    # copy dataframe
    dataframe_t3med = dataframe.copy()

    # for each row, normalize values by dividing each value by the median
    # of the three highest values of the row
    # iterate over rows of dataframe
    for idx, row in dataframe.iterrows():
        # calculate the median of the three highest values
        median_top3 = row.nlargest(3).median()

        # normalize each value of row by dividing by median_top3
        row_norm = row / median_top3

        # update row in dataframe_norm with row_norm
        dataframe_t3med.loc[idx] = row_norm

    return dataframe_t3med


def scale_to_mod_cutoff(values: list[float], cutoff: float) -> list[float]:
    """
    Scales values to a cutoff value.

    :param values: List of values to be scaled.
    :param cutoff: Cutoff value.
    """

    return [
        0.5 + (v - cutoff) * 0.5 / (1 - cutoff)
        if v >= 0.5
        else v * 0.5 / cutoff
        if v >= 0
        else v
        for v in values
    ]
