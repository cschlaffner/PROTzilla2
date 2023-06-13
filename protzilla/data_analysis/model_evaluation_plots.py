import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay

from protzilla.data_analysis.classification_helper import encode_labels
from protzilla.utilities.transform_figure import fig_to_base64


def precision_recall_curve(model, input_test_df, labels_test_df, plot_title=None):
    input_test_df = input_test_df.set_index("Sample")
    label_encoder, y_test_encoded = encode_labels(
        input_test_df, labels_test_df, "Label"
    )

    display = PrecisionRecallDisplay.from_estimator(
        model, input_test_df, y_test_encoded
    )
    display.plot()
    plt.title(plot_title)
    return [
        dict(
            plot_base64=fig_to_base64(display.figure_),
            key="precision_recall_curve_img",
        )
    ]


def roc_curve(model, input_test_df, labels_test_df, plot_title=None):
    input_test_df = input_test_df.set_index("Sample")
    label_encoder, y_test_encoded = encode_labels(
        input_test_df, labels_test_df, "Label"
    )

    display = RocCurveDisplay.from_estimator(model, input_test_df, y_test_encoded)
    display.plot()
    plt.title(plot_title)
    return [
        dict(
            plot_base64=fig_to_base64(display.figure_),
            key="roc_curve_img",
        )
    ]
