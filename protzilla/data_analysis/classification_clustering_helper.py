from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    KFold,
    RepeatedKFold,
    LeaveOneOut,
    LeavePOut,
    StratifiedKFold,
    train_test_split,
    ParameterGrid,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder


def encode_labels(input_df_wide, labels_df):
    input_df_wide.sort_values(by="Sample", inplace=True)
    samples_input_df = input_df_wide.reset_index(names="Sample")["Sample"]
    y = pd.merge(samples_input_df, labels_df, on="Sample", how="inner")
    y.sort_values(by="Sample", inplace=True)
    y = y["Group"]
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    return y_encoded


def perform_grid_search_cv(
    grid_search_model, model, param_grid: dict, scoring, cv=None
):
    if grid_search_model == "Grid search" or grid_search_model == "Manual":
        return GridSearchCV(
            model, param_grid=param_grid, scoring=scoring, cv=cv, error_score="raise"
        )
    elif grid_search_model == "Randomized search":
        return RandomizedSearchCV(
            model,
            param_distributions=param_grid,
            scoring=scoring,
            cv=cv,
            error_score="raise",
        )


def perform_grid_search_manual(
    grid_search_model,
    model,
    param_grid: dict,
    scoring,
):
    if grid_search_model == "Grid search":
        return GridSearchManual(model=model, param_grid=param_grid)
    elif grid_search_model == "Randomized search":
        pass


def perform_cross_validation(
    cross_validation_estimator,
    n_splits=5,
    n_repeats=10,
    shuffle=True,
    random_state=42,
    p=None,
    **parameters,
):
    if cross_validation_estimator == "K-Fold":
        return KFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)
    elif cross_validation_estimator == "Repeated K-Fold":
        return RepeatedKFold(
            n_splits=n_splits, n_repeats=n_repeats, random_state=random_state
        )
    elif cross_validation_estimator == "Stratified K-Fold":
        return StratifiedKFold(
            n_splits=n_splits, shuffle=shuffle, random_state=random_state
        )
    elif cross_validation_estimator == "Leave one out":
        return LeaveOneOut()
    elif cross_validation_estimator == "Leave p out":
        return LeavePOut(p)


def update_raw_evaluation_data(results, params, train_scores, val_scores):
    for param_name, param_value in params.items():
        results |= {f"param_{param_name}": param_value}
    results["mean_train_score"].append(np.mean(train_scores))
    results["std_train_score"].append(np.std(train_scores))
    results["mean_test_score"].append(np.mean(val_scores))
    results["std_test_score"].append(np.std(val_scores))
    return results


@dataclass
class GridSearchManual:
    model: Pipeline
    param_grid: dict
    train_val_split: tuple = None
    results: dict = field(
        default_factory=lambda: {
            "mean_train_score": [],
            "mean_test_score": [],
            "std_train_score": [],
            "std_test_score": [],
        }
    )

    def fit(self, train_val_split):
        self.train_val_split = train_val_split
        X_train, X_val, y_train, y_val = self.train_val_split
        # Iterate over the parameter grid
        for params in ParameterGrid(self.param_grid):
            model = self.model.set_params(**params)
            model.fit(X_train, y_train)
            train_scores = model.score(X_train, y_train)
            val_scores = model.score(X_val, y_val)

            # Store the results for the current parameter combination
            self.results = update_raw_evaluation_data(
                self.results, params, train_scores, val_scores
            )

        return self.model


# maybe add option to hide or show certain columns
def create_model_evaluation_df(raw_evaluation_df, clf_parameters):
    # create model evaluation dataframe
    columns_names = ["param_" + key for key in clf_parameters.keys()]
    columns_names.append("mean_test_score")
    # for multimetrics evaluation
    # columns_names.append([["mean_test_" + score] for score in scoring])
    return raw_evaluation_df[columns_names]


def create_dict_with_lists_as_values(d):
    return {
        key: value if isinstance(value, list) else [value] for key, value in d.items()
    }


def perform_train_test_split(
    input_df, labels_df, test_size=None, random_state=None, shuffle=True, stratify=None
):
    return train_test_split(
        input_df,
        labels_df,
        test_size=test_size,
        random_state=random_state,
        shuffle=shuffle,
        stratify=stratify,
    )
