from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    matthews_corrcoef,
)
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    KFold,
    RepeatedKFold,
    LeaveOneOut,
    LeavePOut,
    StratifiedKFold,
    train_test_split,
)


def encode_labels(labels_df, labels_column, positive_label=None):
    labels_list = labels_df[labels_column].unique().tolist()
    if len(labels_list) < 2 and positive_label is not None:
        return "the data must contain at least 2 different classes"
    elif len(labels_list) == 2 and positive_label is not None:
        # if labels are binary let user determine which is the positive label
        negative_label = (
            labels_list[0] if labels_list[0] != positive_label else labels_list[1]
        )
        encoding_mapping = {1: positive_label, 0: negative_label}
        labels_df["Encoded Label"] = labels_df[labels_column].map(
            {positive_label: 1, negative_label: 0}
        )
    else:
        encoded_labels, labels = pd.factorize(labels_df[labels_column])
        labels_df["Encoded Label"] = encoded_labels
        encoding_mapping = {index: labels for index, labels in enumerate(labels)}
    return encoding_mapping, labels_df


def decode_labels(encoding_mapping, labels):
    labels_df = pd.DataFrame(labels, columns=["Encoded Label"])
    labels_df["Label"] = labels_df["Encoded Label"].map(encoding_mapping)
    labels_df.reset_index(inplace=True)
    return labels_df


def perform_grid_search_cv(
    grid_search_model,
    model,
    param_grid: dict,
    scoring,
    model_selection_scoring,
    cv=None,
):
    if grid_search_model == "Grid search":
        return GridSearchCV(
            model,
            param_grid=param_grid,
            scoring=scoring,
            cv=cv,
            refit=model_selection_scoring,
        )
    elif grid_search_model == "Randomized search":
        return RandomizedSearchCV(
            model,
            param_distributions=param_grid,
            scoring=scoring,
            cv=cv,
            refit=model_selection_scoring,
        )


def perform_cross_validation(
    cross_validation_estimator,
    n_splits=5,
    n_repeats=10,
    shuffle=True,
    random_state_cv=42,
    p_samples=None,
    **parameters,
):
    if cross_validation_estimator == "K-Fold":
        return KFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state_cv)
    elif cross_validation_estimator == "Repeated K-Fold":
        return RepeatedKFold(
            n_splits=n_splits, n_repeats=n_repeats, random_state=random_state_cv
        )
    elif cross_validation_estimator == "Stratified K-Fold":
        return StratifiedKFold(
            n_splits=n_splits, shuffle=shuffle, random_state=random_state_cv
        )
    elif cross_validation_estimator == "Leave one out":
        return LeaveOneOut()
    elif cross_validation_estimator == "Leave p out":
        return LeavePOut(p_samples)


def evaluate_with_scoring(scoring, y_true, y_pred):
    scores = defaultdict(list)
    for score in scoring:
        if score == "accuracy":
            s = accuracy_score(y_true=y_true, y_pred=y_pred)
        elif score == "precision":
            s = precision_score(y_true=y_true, y_pred=y_pred)
        elif score == "recall":
            s = recall_score(y_true=y_true, y_pred=y_pred)
        elif score == "matthews_corrcoef":
            s = matthews_corrcoef(y_true=y_true, y_pred=y_pred)
        else:
            s = "Score not known"
        scores[score] = s
    return scores


# maybe add option to hide or show certain columns
def create_model_evaluation_df_grid_search(raw_evaluation_df, clf_parameters, scoring):
    # The function transforms the cv_results_ dictionary obtained from a grid search cv
    # methods into a model_evaluation_df, where each column represents an estimator
    # parameter and its corresponding validation score.
    columns_names = ["param_" + key for key in clf_parameters.keys()]
    columns_names.extend([f"mean_test_{score}" for score in scoring])
    return raw_evaluation_df[columns_names]


def create_model_evaluation_df_grid_search_manual(clf_parameters, scores):
    # The function mimics the cv_results_ output from the grid search cv methods, but
    # for grid search manual methods. Then transforms it to the  model_evaluation_df
    # format, where each column represents an estimator parameter and its corresponding
    # validation score.
    scores.pop("fit_time", None)
    scores.pop("score_time", None)
    results = defaultdict(list)
    for param_name, param_value in clf_parameters.items():
        results[f"param_{param_name}"].append(param_value)
    for score_name, score_value in scores.items():
        results[f"mean_{score_name}"].append(np.mean(score_value))

    results_df = pd.DataFrame(results)
    return results_df


def create_dict_with_lists_as_values(d):
    return {
        key: value if isinstance(value, list) else [value] for key, value in d.items()
    }


def perform_train_test_split(
    input_df,
    labels_df,
    test_size=0.2,
    random_state=42,
    shuffle=True,
    split_stratify="yes",
    **kwargs,
):
    split_stratify = labels_df if split_stratify == "yes" else None
    return train_test_split(
        input_df,
        labels_df,
        test_size=test_size,
        random_state=random_state,
        shuffle=shuffle,
        stratify=split_stratify,
    )
