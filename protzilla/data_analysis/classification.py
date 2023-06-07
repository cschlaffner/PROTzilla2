import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from protzilla.utilities.transform_dfs import is_long_format, long_to_wide
from protzilla.data_analysis.classification_clustering_helper import (
    perform_grid_search_cv,
    perform_grid_search_manual,
    perform_cross_validation,
    update_raw_evaluation_data,
    create_model_evaluation_df,
    create_dict_with_lists_as_values,
    perform_train_test_split,
    encode_labels,
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
        model = perform_grid_search_manual(
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
        model = perform_grid_search_cv(
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
    metadata_df: pd.DataFrame,
    labels_column: str,
    train_test_split: int = 0.2,
    n_estimators=100,
    criterion="gini",
    max_depth=None,
    bootstrap=True,
    random_state=42,
    model_selection: str = "Grid search",
    validation_strategy: str = "Cross Validation",
    scoring: list[str] = "accuracy",
    **kwargs,
):
    # TODO add warning to user that data should be to shuffled, give that is being sorted at the beginning!
    # TODO add parameters for gridsearch and cross validation
    # TODO be able to select multiple scoring methods,this might also change how evaluation tables are created
    # TODO how to refit
    # TODO save object model with Pickle
    # TODO add parameters for grid search and cross validation,in general to sub steps
    # TODO add scoring to workflow meta and also in backend

    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df

    # "Sample" column should not always have header Sample, modify accordingly
    labels_df = metadata_df[["Sample", labels_column]]
    y_encoded = encode_labels(input_df_wide, labels_df)

    X_train, X_test, y_train, y_test = perform_train_test_split(
        input_df_wide,
        y_encoded,
        test_size=train_test_split,
        random_state=random_state,
        shuffle=True,
    )

    clf = RandomForestClassifier()

    clf_parameters = dict(
        n_estimators=n_estimators,
        criterion=criterion,
        max_depth=max_depth,
        bootstrap=bootstrap,
        random_state=random_state,
    )
    model, model_evaluation_df = perform_classification(
        X_train,
        y_train,
        validation_strategy,
        model_selection,
        clf,
        clf_parameters,
        scoring,
        **kwargs,
    )
    return dict(
        model=model,
        model_evaluation_df=model_evaluation_df,
        X_test_df=pd.DataFrame(X_test),
        y_test_df=pd.DataFrame(y_test),
        X_train_df=pd.DataFrame(X_train),
        y_train_df=pd.DataFrame(y_train),
    )
