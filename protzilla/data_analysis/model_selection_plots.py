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


def learning_curve_plot(
    clf_str,
    input_df,
    metadata_df: pd.DataFrame,
    labels_column: str,
    positive_label: str,
    train_sizes,
    cross_validation_strategy,
    scoring,
    random_state,
    shuffle=True,
    **cv_params,
):
    # train_sizes = np.linspace(0.1, 1.0, 10)
    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    input_df_wide.sort_values(by="Sample", inplace=True)
    labels_df = (
        metadata_df[["Sample", labels_column]]
        .set_index("Sample")
        .sort_values(by="Sample")
    )
    common_indices = input_df_wide.index.intersection(labels_df.index)
    labels_df = labels_df.loc[common_indices]
    encoding_mapping, labels_df = encode_labels(
        labels_df, labels_column, positive_label
    )
    clf = estimator_mapping[clf_str]

    if "Nested" in cross_validation_strategy:
        if shuffle == "yes":
            random_indices = np.random.RandomState(random_state).permutation(
                input_df_wide.index
            )
            input_df_wide = input_df_wide.loc[random_indices]
            labels_df = labels_df.loc[random_indices]
        test_scores = list()
        train_scores = list()
        for size in train_sizes:
            test_score, train_score = perform_nested_cross_validation(
                input_df_wide.iloc[:size],
                labels_df["Encoded Label"].iloc[:size],
                clf,
                scoring,
                random_state=random_state,
                **cv_params,
            )
            test_scores.append(test_score)
            train_scores.append(train_score)
            print(f"train_size{size}")

        display = LearningCurveDisplay(
            train_sizes=np.array(train_sizes),
            train_scores=np.array(train_scores),
            test_scores=np.array(test_scores),
        )

    else:
        cv_callable = perform_cross_validation(
            cross_validation_strategy, random_state_cv=random_state, **cv_params
        )

        display = LearningCurveDisplay.from_estimator(
            clf,
            input_df_wide,
            labels_df["Encoded Label"],
            train_sizes=train_sizes,
            scoring=scoring,
            cv=cv_callable,
            random_state=random_state,
            score_type="both",
        )

    display.plot(
        score_type="both",
        score_name=scoring,
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
