import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LearningCurveDisplay
from sklearn.svm import SVC

from protzilla.data_analysis.classification_helper import (
    perform_cross_validation,
    encode_labels,
    perform_nested_cross_validation,
)
from protzilla.utilities import fig_to_base64
from protzilla.utilities.transform_dfs import is_long_format, long_to_wide
from protzilla.constants.colors import (
    PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE as COLORS,
)

estimator_mapping = {
    "Random Forest": RandomForestClassifier(),
    "Support Vector Machine": SVC(),
}


def learning_curve_plot(train_sizes, train_scores, test_scores, score_name):
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
    # set line colors
    for line, fill, color in zip(display.lines_, display.fill_between_, COLORS):
        line.set_color(color)
        fill.set_color(color)
    # set legend names for each curve
    legend = plt.legend()
    legend_labels = ["Training Score", "Test Score"]
    for text, label in zip(legend.get_texts(), legend_labels):
        text.set_text(label)

    return [fig_to_base64(display.figure_)]
