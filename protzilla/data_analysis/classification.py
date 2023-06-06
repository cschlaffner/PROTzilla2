import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from protzilla.utilities.transform_dfs import is_long_format, long_to_wide
from protzilla.data_analysis.classification_clustering_helper import (
    perform_grid_search,
    perform_cross_validation,
    update_raw_evaluation_data,
    create_model_evaluation_df,
    create_dict_with_lists_as_values,
    perform_train_test_split,
)


def perform_classification(
    input_df,
    labels_df,
    validation_strategy,
    grid_search_method,
    clf,
    clf_parameters,
    scoring,
    cross_validation_estimator=None,
    test_validate_split=None,
    **parameters,
):
    # work with function set_params or create param_grid depending on the case
    # check returns, what to return clf, scores, already fit and predict here? Take
    # into account that scores are not always called using score() function
    if validation_strategy == "Manual" and grid_search_method == "Manual":
        X_train, X_val, y_train, y_val = perform_train_test_split(
            input_df, labels_df, test_size=test_validate_split
        )
        model = clf.set_params(**clf_parameters)
        model.fit(X_train, y_train)
        train_scores = model.score(X_train, y_train)
        val_scores = model.score(X_val, y_val)

        results = update_raw_evaluation_data(
            {
                "mean_train_score": [],
                "mean_test_score": [],
                "std_train_score": [],
                "std_test_score": [],
            },
            clf_parameters,
            train_scores,
            val_scores,
        )
        raw_evaluation_df = pd.DataFrame(results)
        model_evaluation_df = create_model_evaluation_df(
            raw_evaluation_df, clf_parameters
        )
        return model, model_evaluation_df
    elif validation_strategy == "Manual" and grid_search_method != "Manual":
        train_val_split = perform_train_test_split(
            input_df, labels_df, test_size=test_validate_split
        )
        clf_parameters = create_dict_with_lists_as_values(clf_parameters)
        model = perform_grid_search(
            grid_search_method,
            clf,
            clf_parameters,
            scoring,
        )
        model.fit(train_val_split)
        model_evaluation_df = create_model_evaluation_df(
            pd.DataFrame(model.results), clf_parameters
        )
        return model, model_evaluation_df
    elif validation_strategy != "Manual":
        clf_parameters = create_dict_with_lists_as_values(clf_parameters)
        cv = perform_cross_validation(cross_validation_estimator, **parameters)
        model = perform_grid_search(
            grid_search_method, clf, clf_parameters, scoring, cv=cv
        )
        model.fit(input_df, labels_df)

        # create model evaluation dataframe
        model_evaluation_df = create_model_evaluation_df(
            pd.DataFrame(model.cv_results_), clf_parameters
        )
        return model, model_evaluation_df


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
    validation_strategy: str = "Cross Validation",
    scoring: list[str] = "accuracy",
    **kwargs,
):
    # TODO select right column from labels_df ot try to predict
    # TODO add warning to user that data should be to shuffled, give that is being sorted at the beginning!
    # TODO add user is able to choose group from metadata
    # TODO add parameters for gridsearch and cross validation
    # TODO be able to select multiple scoring methods,this might also change how evaluation tables are created
    # TODO how to refit
    # TODO save object model with Pickle

    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    input_df_wide.sort_values(by="Sample", inplace=True)
    samples_input_df = input_df_wide.reset_index(names="Sample")["Sample"]
    y = pd.merge(samples_input_df, labels_df, on="Sample", how="inner")
    y.sort_values(by="Sample", inplace=True)
    y = y["Group"]
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

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
    model, model_evaluation_df = perform_classification(
        input_df_wide,
        y_encoded,
        validation_strategy,
        model_selection,
        clf,
        clf_parameters,
        scoring,
        **kwargs,
    )
    return dict(model=model, model_evaluation_df=model_evaluation_df)
