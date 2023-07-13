import numpy as np
from kneed import KneeLocator
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from sklearn.model_selection import LearningCurveDisplay

from protzilla.utilities import fig_to_base64, remove_underscore_and_capitalize


def learning_curve_plot(
    train_sizes, train_scores, test_scores, score_name, initial_coef_sigmoid
):
    # learning curve with training and validation score
    display = LearningCurveDisplay(
        train_sizes=train_sizes,
        train_scores=np.array(train_scores),
        test_scores=np.array(test_scores),
        score_name=score_name,
    )
    display.plot(
        score_type="both",
        line_kw={"marker": "o"},
    )
    # set legend names for each curve
    legend = plt.legend()
    legend_labels = [f"Training {score_name}", f"Test {score_name}"]
    for text, label in zip(legend.get_texts(), legend_labels):
        text.set_text(label)

    # find flattening point in learning curve
    def sigmoid(x, a, b, c):
        return a / (1 + np.exp(-b * (x - c)))

    test_scores_mean = np.array(test_scores).mean(axis=1)
    params, _ = curve_fit(
        sigmoid, train_sizes, test_scores_mean, p0=initial_coef_sigmoid
    )
    x_fit = np.linspace(min(train_sizes), max(train_sizes), 100)
    curve_values = sigmoid(x_fit, *params)
    diff = np.diff(curve_values)
    flattening_point_idx = np.argmax(diff < np.mean(diff))
    flattening_point = x_fit[flattening_point_idx]

    plt.figure()
    plt.plot(train_sizes, test_scores_mean, "o-", label=f"Test {score_name}")
    plt.plot(x_fit, curve_values, "r-", label="Fitted Curve")
    plt.axvline(
        flattening_point,
        ls="--",
        color="gray",
        label="Minimum Viable Sample Size",
    )
    plt.xlabel("Training Set Size")
    plt.ylabel(score_name)
    plt.ylim(0.4, 1.0)
    plt.legend()
    display_flat = plt.gcf()

    return [fig_to_base64(display.figure_), fig_to_base64(display_flat)]


def elbow_method_n_clusters(
    model_evaluation_dfs, estimator_str, find_elbow, sample_sizes=None
):
    model_evaluation_dfs = (
        model_evaluation_dfs
        if isinstance(model_evaluation_dfs, list)
        else [model_evaluation_dfs]
    )
    # get the key of the n_clusters parameter
    n_clusters_label = (
        "param_n_clusters"
        if "param_n_clusters" in model_evaluation_dfs[0].columns
        else "param_n_components"
    )

    # get column name of scoring metrics
    score_names = model_evaluation_dfs[0].columns[
        ~model_evaluation_dfs[0].columns.str.startswith("param_")
    ]

    # sort sample size keys
    sorted_data = sorted(
        zip(sample_sizes, model_evaluation_dfs),
        key=lambda x: (int(x[0][len("sample_size_") :]), x[1]),
    )
    sample_sizes, model_evaluation_dfs = zip(*sorted_data)

    plots = []
    for score_name in score_names:
        score_name_plt = remove_underscore_and_capitalize(score_name)
        plt.figure()
        for sample_size, model_evaluation_df in zip(sample_sizes, model_evaluation_dfs):
            n_clusters = list(model_evaluation_df[n_clusters_label])
            score_values = list(model_evaluation_df[score_name])
            sample_size = (
                remove_underscore_and_capitalize(sample_size) if sample_size else None
            )
            plt.plot(n_clusters, score_values, marker="o", label=sample_size)
            plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
            if find_elbow == "yes":
                kn = KneeLocator(
                    n_clusters,
                    score_values,
                    curve="convex",
                    direction="decreasing",
                )
                elbow_point = kn.knee
                plt.axvline(
                    x=elbow_point, color="r", linestyle="--", label="Elbow Point"
                )
                plt.legend()

        plt.xlabel("Number of Clusters")
        plt.ylabel(score_name_plt)
        plt.title(
            f"{estimator_str}:Evaluation of Optimal Number of Clusters with {score_name_plt}"
        )
        plots.append(fig_to_base64(plt.gcf()))
        plt.clf()

    return plots
