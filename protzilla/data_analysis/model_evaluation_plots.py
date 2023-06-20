import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay
from sklearn.model_selection import permutation_test_score

from protzilla.data_analysis.classification_helper import (
    encode_labels,
    perform_cross_validation,
)
from protzilla.utilities.utilities import fig_to_base64
from protzilla.constants.colors import (
    PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE as COLORS,
)


def precision_recall_curve_plot(model, input_test_df, labels_test_df, title=None):
    """
    Calculate and plot the precision-recall curve for a classification model.
    :param model: The trained classification model instance to be evaluated.
    :type model: BaseEstimator
    :param input_test_df: The input features of the testing data as a DataFrame.
    :type input_test_df: pd.DataFrame
    :param labels_test_df: The true labels of the testing data as a DataFrame.
    :type labels_test_df: pd.DataFrame
    :param title: The title of the precision-recall curve plot. This is an optional
     parameter.
    :type title: str, optional
    :return: Base64 encoded image of the plot
    :rtype: bytes
    """
    input_test_df = input_test_df.set_index("Sample")
    _, labels_test_df = encode_labels(labels_test_df, "Label")

    display = PrecisionRecallDisplay.from_estimator(
        model, input_test_df, labels_test_df["Encoded Label"]
    )
    display.plot()
    plt.title(title)
    return [fig_to_base64(display.figure_)]


def roc_curve_plot(model, input_test_df, labels_test_df, title=None):
    """
    Calculate and plot the roc curve for a classification model.
    :param model: The trained classification model instance to be evaluated.
    :type model: BaseEstimator
    :param input_test_df: The input features of the testing data as a DataFrame.
    :type input_test_df: pd.DataFrame
    :param labels_test_df: The true labels of the testing data as a DataFrame.
    :type labels_test_df: pd.DataFrame
    :param title: The title of the precision-recall curve plot. This is an optional
     parameter.
    :type title: str, optional
    :return: Base64 encoded image of the plot
    :rtype: bytes
    """
    input_test_df = input_test_df.set_index("Sample")
    _, labels_test_df = encode_labels(labels_test_df, "Label")

    display = RocCurveDisplay.from_estimator(
        model, input_test_df, labels_test_df["Encoded Label"]
    )
    display.plot()
    plt.title(title)
    return [fig_to_base64(display.figure_)]


def permutation_testing_plot(
    model, input_df, labels_df, cv, scoring, n_permutations, random_state, **cv_params
):
    # add license https://scikit-learn.org/stable/auto_examples/model_selection/plot_permutation_tests_for_classification.html#sphx-glr-auto-examples-model-selection-plot-permutation-tests-for-classification-py
    input_df = input_df.set_index("Sample")
    _, labels_df = encode_labels(labels_df, "Label")

    cv_callable = perform_cross_validation(cv, **cv_params)
    score, permutation_scores, pvalue = permutation_test_score(
        model,
        input_df,
        labels_df["Encoded Label"],
        scoring=scoring,
        cv=cv_callable,
        n_permutations=n_permutations,
        random_state=random_state,
    )
    fig, ax = plt.subplots()

    ax.hist(permutation_scores, bins=20, density=True, color=COLORS[0])
    line = ax.axvline(score, ls="--", color=COLORS[1])
    ax.legend(
        [line],
        [f"Score on original\ndata: {score:.2f}\n(p-value: {pvalue:.3f})"],
        loc="upper right",
        bbox_to_anchor=(1.4, 1),
    )
    ax.set_xlabel(f"{scoring} score")
    _ = ax.set_ylabel("Probability")
    return [fig_to_base64(fig)]
