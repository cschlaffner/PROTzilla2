import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    KFold,
    RepeatedKFold,
    LeaveOneOut,
    LeavePOut,
    StratifiedKFold,
)
from protzilla.utilities.transform_dfs import is_long_format, long_to_wide


def perform_grid_search(grid_search_model, model, param_grid: dict, scoring, cv=None):
    if grid_search_model == "Grid search":
        clf = GridSearchCV(model, param_grid=param_grid, scoring=scoring)
    elif grid_search_model == "Randomized search":
        clf = RandomizedSearchCV(model, param_distributions=param_grid, scoring=scoring)
    return clf


def perform_cross_validation(
    cross_validation_strategy,
    n_splits=5,
    n_repeats=10,
    shuffle=False,
    random_state=42,
    p=None,
):
    if cross_validation_strategy == "K-Fold":
        return KFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)
    elif cross_validation_strategy == "Repeated K-Fold":
        return RepeatedKFold(
            n_splits=n_splits, n_repeats=n_repeats, random_state=random_state
        )
    elif cross_validation_strategy == "Stratified K-Fold":
        return StratifiedKFold(
            n_splits=n_splits, shuffle=shuffle, random_state=random_state
        )
    elif cross_validation_strategy == "Leave one out":
        return LeaveOneOut()
    elif cross_validation_strategy == "Leave p out":
        return LeavePOut(p)


def perform_classification(
    validation_strategy, grid_search_method, clf, clf_parameters, scoring, **parameters
):
    # work withfuntion set_params or create param_grid depending on the case
    # check returns, what to return clf, scores, already fit and predict here? Take
    # into account that scores are not always called using score function
    if grid_search_method == "Manual" and validation_strategy == "Manual":
        pass
        # call normal estimator function and validate with validation data
    elif grid_search_method == "Manual" and validation_strategy != "Manual":
        # call normal estimator function, perform_cross_validation and cross_validation_eval or somethign like that
        cv = perform_cross_validation(validation_strategy, **parameters)
        # return cross_val_score()
    elif grid_search_method != "Manual" and validation_strategy == "Manual":
        pass
        # call perform_grid_search using only param_grid
    elif grid_search_method != "Manual" and validation_strategy != "Manual":
        pass
        # call perform_grid_search with parameter cv set to theresult of perform_cross_validation
        cv = perform_cross_validation(validation_strategy, **parameters)
        return perform_grid_search(
            grid_search_method, clf, clf_parameters, scoring, cv=cv
        )


def random_forest(
    input_df: pd.DataFrame,
    labels_df: pd.DataFrame,
    n_estimators=100,
    criterion="gini",
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features="sqrt",
    max_leaf_nodes=None,
    bootstrap=True,
    random_state=42,
    model_selection: str = "Grid search",
    validation_strategy: str = "Kfold",
    **kwargs,
):
    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    clf = RandomForestClassifier()
    clf_parameters = dict(
        n_estimators=n_estimators,
        criterion=criterion,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        max_features=max_features,
        max_leaf_nodes=max_leaf_nodes,
        bootstrap=bootstrap,
        random_state=random_state,
    )
    scoring = "a score"
    clf = perform_classification(
        validation_strategy, model_selection, clf, clf_parameters, scoring, **kwargs
    )
    clf.fit(input_df_wide)
