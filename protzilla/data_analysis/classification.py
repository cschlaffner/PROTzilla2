import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate
from sklearn.svm import SVC

from protzilla.data_analysis.classification_helper import (
    create_dict_with_lists_as_values,
    create_model_evaluation_df_grid_search,
    create_model_evaluation_df_grid_search_manual,
    decode_labels,
    encode_labels,
    evaluate_with_scoring,
    perform_cross_validation,
    perform_grid_search_cv,
    perform_train_test_split,
)
from protzilla.utilities.transform_dfs import is_long_format, long_to_wide


def perform_classification(
    input_df,
    labels_df,
    validation_strategy,
    grid_search_method,
    clf,
    clf_parameters,
    scoring,
    model_selection_scoring="accuracy",
    test_validate_split=None,
    **parameters,
):
    if validation_strategy == "Manual" and grid_search_method == "Manual":
        X_train, X_val, y_train, y_val = perform_train_test_split(
            input_df, labels_df, test_size=test_validate_split
        )
        model = clf.set_params(**clf_parameters)
        model.fit(X_train, y_train)

        y_pred_train = model.predict(X_train)
        train_scores = evaluate_with_scoring(scoring, y_train, y_pred_train)
        y_pred_val = model.predict(X_val)
        val_scores = evaluate_with_scoring(scoring, y_val, y_pred_val)

        # create model evaluation dataframe
        train_scores = {"train_" + key: value for key, value in train_scores.items()}
        val_scores = {"test_" + key: value for key, value in val_scores.items()}
        scores = {**train_scores, **val_scores}
        model_evaluation_df = create_model_evaluation_df_grid_search_manual(
            clf_parameters,
            scores,
        )
        return model, model_evaluation_df
    elif validation_strategy == "Manual" and grid_search_method != "Manual":
        return "Please select a cross validation strategy"
    elif validation_strategy != "Manual" and grid_search_method == "Manual":
        model = clf.set_params(**clf_parameters)
        cv = perform_cross_validation(validation_strategy, **parameters)
        scores = cross_validate(
            model, input_df, labels_df, scoring=scoring, cv=cv, return_train_score=True
        )

        # create model evaluation dataframe
        model_evaluation_df = create_model_evaluation_df_grid_search_manual(
            clf_parameters, scores
        )
        return model, model_evaluation_df
    elif validation_strategy != "Manual" and grid_search_method != "Manual":
        clf_parameters = create_dict_with_lists_as_values(clf_parameters)
        cv = perform_cross_validation(validation_strategy, **parameters)
        model = perform_grid_search_cv(
            grid_search_method,
            clf,
            clf_parameters,
            scoring,
            model_selection_scoring,
            cv=cv,
        )
        model.fit(input_df, labels_df)

        # create model evaluation dataframe
        model_evaluation_df = create_model_evaluation_df_grid_search(
            pd.DataFrame(model.cv_results_), clf_parameters, scoring
        )
        return model.best_estimator_, model_evaluation_df


def random_forest(
    input_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    labels_column: str,
    positive_label: str = None,
    n_estimators=100,
    criterion="gini",
    max_depth=None,
    bootstrap=True,
    random_state=42,
    model_selection: str = "Grid search",
    validation_strategy: str = "Cross Validation",
    scoring: list[str] = ["accuracy"],
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

    # prepare X and y dataframes for classification
    input_df_wide.sort_values(by="Sample", inplace=True)
    labels_df = (
        metadata_df[["Sample", labels_column]]
        .set_index("Sample")
        .sort_values(by="Sample")
    )
    encoding_mapping, labels_df = encode_labels(
        labels_df, labels_column, positive_label
    )

    X_train, X_test, y_train, y_test = perform_train_test_split(
        input_df_wide,
        labels_df["Encoded Label"],
        **kwargs,
    )

    clf = RandomForestClassifier()

    clf_parameters = dict(
        n_estimators=n_estimators,
        criterion=criterion,
        max_depth=max_depth,
        bootstrap=bootstrap,
        random_state=random_state,
    )
    # Transform scoring to list if scoring is a string
    # (multiselect returns a string when only one value is selected)
    scoring = [scoring] if isinstance(scoring, str) else scoring

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
    y_test = decode_labels(encoding_mapping, y_test)
    y_train = decode_labels(encoding_mapping, y_train)
    return dict(
        model=model,
        model_evaluation_df=model_evaluation_df,
        X_train_df=X_train,
        X_test_df=X_test,
        y_train_df=y_train,
        y_test_df=y_test,
    )


def svm(
    input_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    labels_column: str,
    positive_label: str = None,
    C=1.0,
    kernel="rbf",
    gamma="scale",  # only relevant ‘rbf’, ‘poly’ and ‘sigmoid’.
    coef0=0.0,  # relevant for "poly" and "sigmoid"
    probability=True,
    tol=0.001,
    class_weight=None,
    max_iter=-1,
    random_state=42,
    model_selection: str = "Grid search",
    validation_strategy: str = "Cross Validation",
    scoring: list[str] = ["accuracy"],
    **kwargs,
):
    # TODO 216 add warning to user that data should be to shuffled, give that is being sorted at the beginning!

    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df

    # prepare X and y dataframes for classification
    input_df_wide.sort_values(by="Sample", inplace=True)
    labels_df = (
        metadata_df[["Sample", labels_column]]
        .set_index("Sample")
        .sort_values(by="Sample")
    )
    encoding_mapping, labels_df = encode_labels(
        labels_df, labels_column, positive_label
    )

    X_train, X_test, y_train, y_test = perform_train_test_split(
        input_df_wide,
        labels_df["Encoded Label"],
        **kwargs,
    )

    clf = SVC()

    clf_parameters = dict(
        C=C,
        kernel=kernel,
        gamma=gamma,
        coef0=coef0,
        probability=probability,
        tol=tol,
        class_weight=class_weight,
        max_iter=max_iter,
        random_state=random_state,
    )
    # multiselect returns a string when only one value is selected
    scoring = [scoring] if isinstance(scoring, str) else scoring

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
    y_test = decode_labels(encoding_mapping, y_test)
    y_train = decode_labels(encoding_mapping, y_train)
    return dict(
        model=model,
        model_evaluation_df=model_evaluation_df,
        X_train_df=X_train,
        X_test_df=X_test,
        y_train_df=y_train,
        y_test_df=y_test,
    )
