from collections import defaultdict

import numpy as np
import pandas as pd
from django.contrib import messages
from joblib import Parallel, delayed
from kneed import KneeLocator
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import learning_curve, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

from protzilla.data_analysis.classification_helper import (
    encode_labels,
    perform_cross_validation,
    perform_nested_cross_validation,
)
from protzilla.data_analysis.model_selection_plots import elbow_method_n_clusters
from protzilla.utilities import replace_spaces_with_underscores_and_lowercase
from protzilla.utilities.transform_dfs import is_long_format, long_to_wide

estimator_mapping = {
    "Random Forest": RandomForestClassifier(),
    "Support Vector Machine": SVC(),
    "Naive Bayes": GaussianNB(),
}


def compute_learning_curve(
    clf_str,
    input_df,
    metadata_df: pd.DataFrame,
    labels_column: str,
    positive_label: str,
    train_sizes,
    cross_validation_strategy,
    scoring,
    random_state,
    shuffle="yes",
    nested_cv_params=None,
    n_jobs=1,
    **cv_params,
):
    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    input_df_wide.sort_values(by="Sample", inplace=True)
    labels_df = (
        metadata_df[["Sample", labels_column]]
        .set_index("Sample")
        .sort_values(by="Sample")
    )
    common_indices = input_df_wide.index.intersection(labels_df.index)
    labels_df = labels_df.loc[common_indices]
    encoding_mapping, labels_df = encode_labels(
        labels_df, labels_column, positive_label
    )
    clf = estimator_mapping[clf_str]

    if "Nested" in cross_validation_strategy:
        X_subsets, y_subsets = generate_stratified_subsets(
            input_df_wide, labels_df["Encoded Label"], train_sizes, random_state
        )

        results = Parallel(n_jobs=n_jobs, verbose=1)(
            delayed(perform_nested_cross_validation)(
                input_df=X_subsets[i],
                labels_df=y_subsets[i],
                clf=clf,
                scoring=scoring,
                random_state=random_state,
                **cv_params,
            )
            for i in range(len(X_subsets))
        )
        test_scores, train_scores = zip(*results)
        test_scores = np.array(test_scores)
        train_scores = np.array(train_scores)

    else:
        cv_callable = perform_cross_validation(
            cross_validation_strategy, random_state_cv=random_state, **cv_params
        )
        _, train_scores, test_scores = learning_curve(
            clf,
            input_df_wide,
            labels_df["Encoded Label"],
            train_sizes=train_sizes,
            scoring=scoring,
            cv=cv_callable,
            random_state=random_state,
        )

    # create df train_sizes, train_scores, test_scores
    kneedle = KneeLocator(
        train_sizes,
        test_scores.mean(axis=1),
        S=1.0,
        curve="concave",
        direction="increasing",
    )
    minimum_viable_sample_size = round(kneedle.elbow)

    return dict(
        train_sizes=train_sizes,
        test_scores=test_scores.tolist(),
        train_scores=train_scores.tolist(),
        minimum_viable_sample_size=minimum_viable_sample_size,
    )


def generate_stratified_subsets(input_df, labels_df, train_sizes, random_state):
    X_subsets = []
    y_subsets = []
    if len(input_df) in train_sizes:
        train_sizes.remove(len(input_df))
        X_subsets.append(input_df)
        y_subsets.append(labels_df)
    for size in train_sizes:
        X_train, X_remaining, y_train, y_remaining = train_test_split(
            input_df,
            labels_df,
            stratify=labels_df,
            train_size=size,
            random_state=random_state,
        )
        X_subsets.append(X_train)
        y_subsets.append(y_train)
    return X_subsets, y_subsets


# adapt for samples without labels
def random_sampling(input_df, metadata_df, labels_column, n_samples, random_state=6):
    # prepare X and y dataframes for classification
    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    input_df_wide.sort_values(by="Sample", inplace=True)
    labels_df = (
        metadata_df[["Sample", labels_column]]
        .set_index("Sample")
        .sort_values(by="Sample")
    )
    common_indices = input_df_wide.index.intersection(labels_df.index)
    labels_df = labels_df.loc[common_indices]

    if len(input_df) < n_samples:
        msg = f"The number of samples should be less than {len(input_df)}"
        return dict(
            input_df=None,
            labels_df=None,
            messages=[dict(level=messages.ERROR, msg=msg)],
        )
    input_df_n_samples, _, labels_df_n_samples, _ = train_test_split(
        input_df_wide,
        labels_df,
        train_size=n_samples,
        random_state=random_state,
        stratify=labels_df,
    )
    return dict(input_df=input_df_n_samples, labels_df=labels_df_n_samples)


def cluster_multiple_sample_sizes_and_k(
    input_df,
    metadata_df: pd.DataFrame,
    labels_column: str,
    clustering_method,
    sample_sizes: list[int],
    n_clusters,
    scoring,
    model_selection_scoring,
    random_state,
):
    from protzilla.constants.location_mapping import method_map

    input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    input_df_wide.sort_values(by="Sample", inplace=True)
    # necessary for ba as subsets need to be stratified
    labels_df = (
        metadata_df[["Sample", labels_column]]
        .set_index("Sample")
        .sort_values(by="Sample")
    )
    common_indices = input_df_wide.index.intersection(labels_df.index)
    labels_df = labels_df.loc[common_indices]

    clustering_method_key = replace_spaces_with_underscores_and_lowercase(
        clustering_method
    )

    model_evaluation_dict = defaultdict()
    merged_df = pd.concat([input_df_wide, labels_df], axis=1)
    stratified_subsets = []
    for i, size in enumerate(sample_sizes):
        if i == 0:
            # For the first sample size, use train_test_split
            samples, _ = train_test_split(
                merged_df,
                train_size=size,
                stratify=labels_df,
                random_state=random_state,
            )
        else:
            # For subsequent sample sizes, take a subset of the previous sample
            previous_samples = stratified_subsets[i - 1]
            previous_indices = previous_samples.index.tolist()
            remaining_samples = merged_df.loc[~merged_df.index.isin(previous_indices)]
            train_size = size - sample_sizes[i - 1]
            if train_size == len(remaining_samples):
                additional_samples = remaining_samples
            else:
                additional_samples, _ = train_test_split(
                    remaining_samples,
                    train_size=train_size,
                    stratify=labels_df.loc[~merged_df.index.isin(previous_indices)],
                    random_state=random_state,
                )
            samples = pd.concat([previous_samples, additional_samples])
        # Remove the samples from merged_df
        stratified_subsets.append(samples.drop(labels_column, axis=1))

    # Extract X for each sample size
    for subset in stratified_subsets:
        clustering_method_key_callable = method_map[
            ("data_analysis", "clustering", clustering_method_key)
        ]
        results = clustering_method_key_callable(
            input_df=subset,
            n_clusters=n_clusters,
            n_components=n_clusters,
            scoring=scoring,
            model_selection_scoring=model_selection_scoring,
            random_state=random_state,
        )
        model_evaluation_dict[f"sample_size_{len(subset)}"] = results[
            "model_evaluation_df"
        ]
    stratified_subsets_dict = dict(
        zip([str(s) for s in sample_sizes], stratified_subsets)
    )
    return {**model_evaluation_dict, **stratified_subsets_dict}


def elbow_plot_multiple_sample_sizes(df, result_df, current_out, plot_title):
    current_out = {
        key: value
        for key, value in current_out.items()
        if key.startswith("sample_size")
    }

    plots = elbow_method_n_clusters(
        model_evaluation_dfs=list(current_out.values()),
        sample_sizes=list(current_out.keys()),
        find_elbow="no",
        plot_title=plot_title,
    )
    return plots
