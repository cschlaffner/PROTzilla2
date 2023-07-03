import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LearningCurveDisplay
from sklearn.svm import SVC

from protzilla.utilities import fig_to_base64

estimator_mapping = {
    "Random Forest": RandomForestClassifier(),
    "Support Vector Machine": SVC(),
}


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
