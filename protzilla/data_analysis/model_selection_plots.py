import numpy as np
from kneed import KneeLocator
from matplotlib import pyplot as plt
from sklearn.model_selection import LearningCurveDisplay

from protzilla.utilities import fig_to_base64, remove_underscore_and_capitalize


def learning_curve_plot(
    train_sizes, train_scores, test_scores, score_name, minimum_viable_sample_size
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

    # learning curve for test scores with elbow
    display_elbow = LearningCurveDisplay(
        train_sizes=train_sizes,
        train_scores=np.array(train_scores),
        test_scores=np.array(test_scores),
        score_name=score_name,
    )
    display_elbow.plot(
        score_type="test",
        std_display_style=None,
        line_kw={"marker": "o", "color": "#ff7f0a"},
    )
    display_elbow.ax_.axvline(
        minimum_viable_sample_size,
        ls="--",
        color="gray",
        label="Minimum Viable Sample Size",
    )

    plt.legend([f"Test {score_name}", "Minimum Viable Sample Size"])

    return [fig_to_base64(display.figure_), fig_to_base64(display_elbow.figure_)]


def elbow_method_n_clusters(model_evaluation_df, estimator_str, find_elbow):
    n_clusters_label = (
        "param_n_clusters"
        if "param_n_clusters" in model_evaluation_df.columns
        else "param_n_components"
    )
    n_clusters = list(model_evaluation_df[n_clusters_label])
    # create dataframe with only the score metrics
    filtered_columns = model_evaluation_df.columns[
        ~model_evaluation_df.columns.str.startswith("param_")
    ]
    scores_df = model_evaluation_df[filtered_columns]
    plots = []
    for score_name in scores_df.columns:
        score_values = list(scores_df[score_name])

        score_name_plt = remove_underscore_and_capitalize(score_name)
        plt.plot(n_clusters, score_values, marker="o")
        plt.xlabel("Number of Clusters")
        plt.ylabel(score_name_plt)
        plt.title(
            f"Evaluation of Optimal Number of Clusters with {score_name_plt} for {estimator_str}"
        )
        if find_elbow is "yes":
            kn = KneeLocator(
                n_clusters,
                score_values,
                curve="convex",
                direction="decreasing",
            )
            elbow_point = kn.knee
            plt.axvline(x=elbow_point, color="r", linestyle="--", label="Elbow Point")
            plt.legend()
        plots.append(fig_to_base64(plt.gcf()))
        plt.show()
    return plots
