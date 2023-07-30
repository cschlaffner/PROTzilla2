import pandas as pd
from sklearn.model_selection import permutation_test_score

from protzilla.data_analysis.classification_helper import (
    evaluate_with_scoring,
    perform_cross_validation,
)


def evaluate_classification_model(model, input_test_df, labels_test_df, scoring):
    """
    Function that asseses an already trained classification model on separate testing
    data using widely used scoring metrics

    :param model: The trained classification model instance to be evaluated.
    :type model: BaseEstimator
    :param input_test_df: The input features of the testing data as a DataFrame.
    :type input_test_df: pd.DataFrame
    :param labels_test_df: The true labels of the testing data as a DataFrame.
    :type labels_test_df: pd.DataFrame
    :param scoring: The scoring metric to be used for evaluation. It can be a string
     representing a predefined metric e.g. accuracy, precision, recall, matthews_corrcoef
    :type scoring: str or callable
    :return: A dataframe with the metric name and its corresponding score.
    :rtype: dict
    """
    input_test_df = input_test_df.set_index("Sample")

    y_pred = model.predict(input_test_df)
    labels_test_df["Predicted Label"] = pd.Series(y_pred)

    scores = evaluate_with_scoring(scoring, labels_test_df["Encoded Label"], y_pred)
    scores_df = pd.DataFrame.from_dict(scores, orient="index", columns=["Score"])
    scores_df = scores_df.reset_index().rename(columns={"index": "Metric"})
    return dict(scores_df=scores_df, labels_test_df=labels_test_df)


def permutation_testing(
    model,
    input_df,
    labels_df,
    cross_validation_strategy,
    scoring,
    n_permutations,
    n_jobs,
    random_state,
    **cv_params,
):
    input_df = input_df.set_index("Sample")

    cv_callable = perform_cross_validation(cross_validation_strategy, **cv_params)
    score, permutation_scores, pvalue = permutation_test_score(
        model,
        input_df,
        labels_df["Encoded Label"],
        scoring=scoring,
        cv=cv_callable,
        n_permutations=n_permutations,
        n_jobs=n_jobs,
        random_state=random_state,
        verbose=True,
    )
    return dict(
        score=score, permutation_scores=permutation_scores.tolist(), pvalue=pvalue
    )
