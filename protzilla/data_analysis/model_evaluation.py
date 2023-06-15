import pandas as pd

from protzilla.data_analysis.classification_helper import (
    evaluate_with_scoring,
    encode_labels,
)


def evaluate_classification_model(model, input_test_df, labels_test_df, scoring):
    """Function that asseses an already trained classification model on separate testing
    data using widely used scoring metrics

    :param model: The trained classification model instance to be evaluated.
    :type model: BaseEstimator
    :param input_test_df: The input features of the testing data as a DataFrame.
    :type input_test_df: pd.DataFrame
    :param labels_test_df: The true labels of the testing data as a DataFrame.
    :type labels_test_df: pd.DataFrame
    :param scoring: The scoring metric to be used for evaluation. It can be a string
     representing a predefined metric.
    :type scoring: str or callable
    :return: A dataframe with the metric name and its corresponding score.
    :rtype: dict
    """
    input_test_df = input_test_df.set_index("Sample")
    _, labels_test_df = encode_labels(labels_test_df, "Label")

    y_pred = model.predict(input_test_df)
    scores = evaluate_with_scoring(scoring, labels_test_df["Encoded Label"], y_pred)

    scores_df = pd.DataFrame.from_dict(scores, orient="index", columns=["Score"])
    scores_df = scores_df.reset_index().rename(columns={"index": "Metric"})
    return dict(scores_df=scores_df)
