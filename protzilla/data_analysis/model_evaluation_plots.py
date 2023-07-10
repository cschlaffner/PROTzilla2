import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
from sklearn.metrics import (
    PrecisionRecallDisplay,
    RocCurveDisplay,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import permutation_test_score

from protzilla.data_analysis.classification_helper import (
    encode_labels,
    perform_cross_validation,
)
from protzilla.utilities.utilities import fig_to_base64
from protzilla.constants.colors import (
    PROTZILLA_DISCRETE_COLOR_OUTLIER_SEQUENCE as COLORS,
)


def precision_recall_curve_plot(model, input_test_df, labels_test_df, plot_title=None):
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

    display = PrecisionRecallDisplay.from_estimator(
        model, input_test_df, labels_test_df["Encoded Label"]
    )
    display.plot()
    plt.title(plot_title)
    return [fig_to_base64(display.figure_)]


def roc_curve_plot(model, input_test_df, labels_test_df, plot_title=None):
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

    display = RocCurveDisplay.from_estimator(
        model, input_test_df, labels_test_df["Encoded Label"]
    )
    display.plot()
    plt.title(plot_title)
    return [fig_to_base64(display.figure_)]


def confusion_matrix_plot(model, input_test_df, labels_test_df, plot_title=None):
    input_test_df = input_test_df.set_index("Sample")
    unique_tuples = set(
        labels_test_df[["Label", "Encoded Label"]].itertuples(index=False)
    )
    encoded_labels, display_labels = zip(*unique_tuples)
    encoded_labels = list(encoded_labels)
    display_labels = list(display_labels)
    out = list()
    try:
        display = ConfusionMatrixDisplay.from_estimator(
            model,
            input_test_df,
            labels_test_df["Encoded Label"],
            labels=encoded_labels,
            display_labels=display_labels,
        )
    except Exception as e:
        display = ConfusionMatrixDisplay.from_estimator(
            model, input_test_df, labels_test_df["Encoded Label"]
        )
    display.plot(cmap=mpl.colormaps["Blues"])
    plt.title(plot_title)
    out.append(fig_to_base64(display.figure_))
    return out


def permutation_testing_plot(score, permutation_scores, pvalue, score_name):
    # add license https://scikit-learn.org/stable/auto_examples/model_selection/plot_permutation_tests_for_classification.html#sphx-glr-auto-examples-model-selection-plot-permutation-tests-for-classification-py
    fig, ax = plt.subplots()

    ax.hist(permutation_scores, bins=20, density=True, color=COLORS[0])
    line = ax.axvline(score, ls="--", color=COLORS[1])
    ax.legend(
        [line],
        [f"Score on original\ndata: {score:.2f}\n(p-value: {pvalue:.3f})"],
        loc="upper right",
        bbox_to_anchor=(1.4, 1),
    )
    ax.set_xlabel(f"{score_name} score")
    _ = ax.set_ylabel("Probability")
    return [fig_to_base64(fig)]
