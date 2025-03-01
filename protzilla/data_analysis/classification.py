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
    train_validate_split=None,
    n_splits: int = 5,
    n_repeats: int = 10,
    random_state_cv: int = 42,
    p_samples = None,
):
    if validation_strategy == "Manual" and grid_search_method == "Manual":
        X_train, X_val, y_train, y_val = perform_train_test_split(
            input_df, labels_df, test_size=train_validate_split
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
        cv = perform_cross_validation(validation_strategy, n_splits,n_repeats,random_state_cv=random_state_cv, p_samples=p_samples)
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
        cv = perform_cross_validation(validation_strategy, n_splits, n_repeats, random_state_cv=random_state_cv, p_samples=p_samples)
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
    n_estimators: int = 100,
    criterion: str = "gini",
    max_depth: int = None,
    bootstrap: bool = True,

    #test_split_parameters
    test_size: float = 0.2,
    split_stratify: str = "yes",
    shuffle: bool = True,
    random_state: int = 42,

    #classification_parameters
    model_selection: str = "Grid search",
    scoring: list[str] = ["accuracy"],
    model_selection_scoring: str = "accuracy",
    train_val_split: float = 0.25,
    validation_strategy: str = "Cross Validation",

    #cross_validation_parameters
    n_splits: int = 5,
    n_repeats: int = 10,
    random_state_cv: int = 42,
    p_samples = None,
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
    :param positive_label: The label that should be considered as the positive class.
    :type positive_label: str, optional
    :param n_estimators: The number of decision trees to be used in the random forest.
    :type n_estimators: int, optional
    :param criterion: The impurity measure used for tree construction.
    :type criterion: str, optional
    :param max_depth: The maximum depth of the decision trees. If not specified (None),
        the trees will expand until all leaves are pure or contain minimum samples per leaf.
    :type max_depth: int or None, optional
    :param bootstrap: Whether bootstrap samples should be used when building trees.
    :type bootstrap: bool, optional
    :param test_size: The proportion of data to be used for testing. Default is
        0.2 (80-20 train-test split).
    :type test_size: float, optional
    :param split_stratify: If not None, data is split in a stratified fashion, using this as
        the class labels.
    :type split_stratify: str, optional
    :param shuffle: Whether to shuffle the data before splitting.
    :type shuffle: bool, optional
    :param random_state: The random seed for reproducibility.
    :type random_state: int, optional
    :param model_selection: The model selection method for hyperparameter tuning.
    :type model_selection: str
    :param scoring: The scoring metric(s) used to evaluate the model's performance
        during validation.
    :type scoring: list[str]
    :param model_selection_scoring: The scoring metric used to select the best model.
    :type model_selection_scoring: str, optional
    :param train_val_split: The proportion of data to be used for validation from the train part of the train-test-split. Default is 0.25.
    :type train_val_split: float, optional
    :param validation_strategy: The strategy for model validation.
    :type validation_strategy: str
    :param n_splits: The number of folds in a KFold.
    :type n_splits: int, optional
    :param n_repeats: The number of times cross-validator needs to be repeated.
    :type n_repeats: int, optional
    :param random_state_cv: The random seed for reproducibility.
    :type random_state_cv: int, optional
    :param p_samples: The number of samples to be used in the cross-validation.
    :type p_samples: float, optional
    :return: A RandomForestClassifier instance, a dataframe consisting of the model's
        training parameters and the validation score, along with four dataframes
        containing the respective test and training samples and labels.
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
        test_size,
        shuffle=shuffle,
        split_stratify=split_stratify,
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
        model_selection_scoring,
        train_val_split,
        n_splits,
        n_repeats,
        random_state_cv,
        p_samples,
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
    tolerance=0.001,
    class_weight=None,
    max_iter=-1,
    random_state=42,

    #test_split_parameters
    test_size: float = 0.2,
    split_stratify: str = "yes",
    shuffle: bool = True,

    #classification_parameters
    model_selection: str = "Grid search",
    scoring: list[str] = ["accuracy"],
    model_selection_scoring = "accuracy",
    train_val_split: float | None = None,
    validation_strategy: str = "Cross Validation",

    #cross_validation_parameters
    n_splits: int = 5,
    n_repeats: int = 10,
    random_state_cv: int = 42,
    p_samples = None,
):
    """
    Perform classification using the support vector machine classifier from sklearn.

    :param input_df: The dataframe that should be classified in wide or long format
    :type input_df: pd.DataFrame
    :param metadata_df: A separate dataframe containing additional metadata information.
    :type metadata_df: pd.DataFrame
    :param labels_column: The column name in the `metadata_df` dataframe that contains
        the target variable (labels) for classification.
    :type labels_column: str
    :param positive_label: The label that should be considered as the positive class.
    :type positive_label: str, optional
    :param C: Regularization parameter
    :type C: float
    :param kernel: Specifies the kernel type.
    :type kernel: str, optional
    :param gamma: Kernel coefficient (default: 'scale', relevant for 'rbf', 'poly', and
        'sigmoid').
    :type gamma: str
    :param coef0: Independent term in the kernel function (relevant for 'poly' and
        'sigmoid').
    :type coef0: float
    :param probability: Whether to enable probability estimates
    :type probability: bool, optional
    :param tol: Tolerance for stopping criterion
    :type tol: float
    :param class_weight: Weights associated with classes
    :type class_weight: float
    :param max_iter: Maximum number of iterations (default: -1, indicating no limit).
    :type max_iter: int
    :param random_state: The random seed for reproducibility.
    :type random_state: int
    :param test_size: The proportion of data to be used for testing. Default is
        0.2 (80-20 train-test split).
    :type test_size: float, optional
    :param split_stratify: If not None, data is split in a stratified fashion, using this as
        the class labels.
    :type split_stratify: str, optional
    :param shuffle: Whether to shuffle the data before splitting.
    :type shuffle: bool, optional   

    :param model_selection: The model selection method for hyperparameter tuning.
    :type model_selection: str
    :param scoring: The scoring metric(s) used to evaluate the model's performance
        during validation.
    :type scoring: list[str]
    :param model_selection_scoring: The scoring metric used to select the best model.
    :type model_selection_scoring: str, optional
    :param train_val_split: The proportion of data to be used for validation from the train part of the train-test-split. Default is 0.25.
    :type train_val_split: float, optional
    :param validation_strategy: The strategy for model validation.
    :type validation_strategy: str
    :param n_splits: The number of folds in a KFold.
    :type n_splits: int, optional
    :param n_repeats: The number of times cross-validator needs to be repeated.
    :type n_repeats: int, optional
    :param random_state_cv: The random seed for reproducibility.
    :type random_state_cv: int, optional
    :param p_samples: The number of samples to be used in the cross-validation.
    :type p_samples: float, optional
    :return: A dict containing: a SVC instance, a dataframe consisting of the model's
        training parameters and the validation score, along with four dataframes
        containing the respective test and training samples and labels.
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
        test_size,
        shuffle=shuffle,
        split_stratify=split_stratify
    )

    clf = SVC()

    clf_parameters = dict(
        C=C,
        kernel=kernel,
        gamma=gamma,
        coef0=coef0,
        probability=probability,
        tol=tolerance,
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
        model_selection_scoring,
        train_val_split,
        n_splits,
        n_repeats,
        random_state_cv,
        p_samples,
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
