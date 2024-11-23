import matplotlib.pyplot as plot
from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay

from protzilla.constants.colors import PLOT_PRIMARY_COLOR
from protzilla.data_analysis.classification_helper import encode_labels
from protzilla.utilities.utilities import fig_to_base64


def precision_recall_curve_plot(model, input_test_df, labels_test_df, plot_title=None):
    """
    Calculate and plot the precision-recall curve for a classification model.

    :param model: The trained classification model instance to be evaluated.
    :type model: BaseEstimator
    :param input_test_df: The input features of the testing data as a DataFrame.
    :type input_test_df: pd.DataFrame
    :param labels_test_df: The true labels of the testing data as a DataFrame.
    :type labels_test_df: pd.DataFrame
    :param plot_title: The title of the precision-recall curve plot. This is an optional
        parameter.
    :type plot_title: str, optional
    :return: Base64 encoded image of the plot
    :rtype: bytes
    """
    input_test_df = input_test_df.set_index("Sample")
    _, labels_test_df = encode_labels(labels_test_df, "Label")

    display = PrecisionRecallDisplay.from_estimator(
        model, input_test_df, labels_test_df["Encoded Label"]
    )
    display.plot(color=PLOT_PRIMARY_COLOR)
    plot.title(plot_title)
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
    :param plot_title: The title of the precision-recall curve plot. This is an optional
        parameter.
    :type plot_title: str, optional
    :return: Base64 encoded image of the plot
    :rtype: bytes
    """
    input_test_df = input_test_df.set_index("Sample")
    _, labels_test_df = encode_labels(labels_test_df, "Label")

    display = RocCurveDisplay.from_estimator(
        model, input_test_df, labels_test_df["Encoded Label"]
    )
    display.plot(color=PLOT_PRIMARY_COLOR)
    plot.title(plot_title)
    return [fig_to_base64(display.figure_)]
