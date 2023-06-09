import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate

from protzilla.utilities.transform_dfs import is_long_format, long_to_wide
from protzilla.data_analysis.classification_helper import (
    perform_grid_search_cv,
    perform_grid_search_manual,
    perform_cross_validation,
    create_dict_with_lists_as_values,
    perform_train_test_split,
    encode_labels,
    decode_labels,
    create_model_evaluation_df_grid_search_manual,
    create_model_evaluation_df_grid_search,
)


def perform_classification(
    input_df,
    labels_df,
    validation_strategy,
    grid_search_method,
    clf,
    clf_parameters,
    scoring,
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

        model_evaluation_df = create_model_evaluation_df_grid_search_manual(
            clf_parameters,
            train_scores,
            val_scores,
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
        model_evaluation_df = create_model_evaluation_df_grid_search(
            pd.DataFrame(model.results), clf_parameters
        )
        return model, model_evaluation_df
    elif validation_strategy != "Manual" and grid_search_method == "Manual":
        model = clf.set_params(**clf_parameters)
        cv = perform_cross_validation(validation_strategy, n_splits=2, **parameters)
        scores = cross_validate(
            model, input_df, labels_df, scoring=scoring, cv=cv, return_train_score=True
        )
        model_evaluation_df = create_model_evaluation_df_grid_search_manual(
            clf_parameters,
            scores["train_score"],
            scores["test_score"],
        )
        return model, model_evaluation_df
    elif validation_strategy != "Manual" and grid_search_method != "Manual":
        clf_parameters = create_dict_with_lists_as_values(clf_parameters)
        cv = perform_cross_validation(validation_strategy, **parameters)
        model = perform_grid_search_cv(
            grid_search_method, clf, clf_parameters, scoring, cv=cv
        )
        model.fit(input_df, labels_df)

        # create model evaluation dataframe
        model_evaluation_df = create_model_evaluation_df_grid_search(
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
    """
    Perform classification using a random forest classifier from sklearn.

    :param input_df: The dataframe that should be classified in wide or long format
    :type input_df: pd.DataFrame
    :param metadata_df: A separate dataframe containing additional metadata information.
    :type metadata_df: pd.DataFrame
    :param labels_column: The column name in the `metadata_df` dataframe that contains
     the target variable (labels) for classification.
    :type labels_column: str
    :param train_test_split: The proportion of data to be used for testing. Default is
     0.2 (80-20 train-test split).
    :type train_test_split: int, optional
    :param n_estimators: The number of decision trees to be used in the random forest.
    :type n_estimators: int, optional
    :param criterion: The impurity measure used for tree construction.
    :type criterion: str, optional
    :param max_depth: The maximum depth of the decision trees. If not specified (None),
     the trees will expand until all leaves are pure or contain minimum samples per leaf.
    :type max_depth: int or None, optional
    :param bootstrap: Whether bootstrap samples should be used when building trees.
    :type bootstrap: bool, optional
    :param random_state: The random seed for reproducibility.
    :type random_state: int, optional
    :param model_selection: The model selection method for hyperparameter tuning.
    :type model_selection: str, optional
    :param validation_strategy: The strategy for model validation.
    :type validation_strategy: str, optional
    :param scoring: The scoring metric(s) used to evaluate the model's performance
    during validation.
    :type scoring: list[str], optional
    :param **kwargs: Additional keyword arguments to be passed to the function.
    :return: A RandomForestClassifier instance, a dataframe consisting of the model's
     training parameters and the validation score, along with four dataframes containing
     the respective test and training samples and labels.
    :rtype: dict

    """
    # TODO 216 add warning to user that data should be to shuffled, give that is being sorted at the beginning!

    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df

    labels_df = metadata_df[["Sample", labels_column]]
    label_encoder, y_encoded = encode_labels(input_df_wide, labels_df)

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

    X_test.reset_index(inplace=True)
    X_train.reset_index(inplace=True)
    y_test = decode_labels(label_encoder, X_test, y_test)
    y_train = decode_labels(label_encoder, X_train, y_train)
    return dict(
        model=model,
        model_evaluation_df=model_evaluation_df,
        X_test_df=X_test,
        y_test_df=y_test,
        X_train_df=X_test,
        y_train_df=y_train,
    )
