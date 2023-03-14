import numpy as np
import pandas as pd
import pytest

from protzilla.data_preprocessing.imputation import *


@pytest.fixture
def input_imputation_df():
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", np.nan],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1],
        ["Sample2", "Protein2", "Gene2", np.nan],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", np.nan],
        ["Sample3", "Protein3", "Gene3", 80],
    )

    test_intensity_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return test_intensity_df


@pytest.fixture
def assertion_df_knn():
    assertion_list = (
        ["Sample1", "Protein1", "Gene1", 50.5],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1.0],
        ["Sample2", "Protein2", "Gene2", 20],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 20],
        ["Sample3", "Protein3", "Gene3", 80],
    )
    assertion_df = pd.DataFrame(
        data=assertion_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    return assertion_df

@pytest.fixture
def assertion_df_min_value_per_df():
    # create data frame with correct answers
    assertion_list = (
        ["Sample1", "Protein1", "Gene1", 0.1],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1],
        ["Sample2", "Protein2", "Gene2", 0.1],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 0.1],
        ["Sample3", "Protein3", "Gene3", 80],
    )
    assertion_df = pd.DataFrame(
        data=assertion_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    return assertion_df

def test_imputation_min_value_per_df(show_figures, input_imputation_df, assertion_df_min_value_per_df):
    assertion_df = assertion_df_min_value_per_df

    # perform imputation on test data frame
    test_intensity_df_imputed = by_min_per_dataset(input_imputation_df, shrinking_value=0.1)[0]

    if show_figures:
        fig1, fig2 = by_min_per_dataset_plot(df=input_imputation_df)
        fig1.show()
        fig2.show()

    # test whether dataframes match
    assert test_intensity_df_imputed.equals(
        assertion_df
    ), f"Imputation by min value per df does not match!\
             Imputation should be \
            {assertion_df} but is {test_intensity_df_imputed}"

@pytest.fixture
def assertion_df_min_value_per_sample():
    # create data frame with correct answers
    assertion_list = (
        ["Sample1", "Protein1", "Gene1", 2],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1.0],
        ["Sample2", "Protein2", "Gene2", 0.2],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 16],
        ["Sample3", "Protein3", "Gene3", 80],
    )
    return pd.DataFrame(
        data=assertion_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

def test_imputation_min_value_per_sample(show_figures, input_imputation_df, assertion_df_min_value_per_sample):
    test_intensity_df = input_imputation_df
    assertion_df = assertion_df_min_value_per_sample

    # perform imputation on test data frame
    test_intensity_df_imputed = by_min_per_sample(test_intensity_df, shrinking_value=0.2)[0]

    if show_figures:
        fig1, fig2 = by_min_per_sample_plot(df=input_imputation_df)
        fig1.show()
        fig2.show()


    # test whether dataframes match
    assert test_intensity_df_imputed.equals(
        assertion_df
    ), f"Imputation by min value per sample does not match!\
             Imputation should be \
            {assertion_df} but is {test_intensity_df_imputed}"


@pytest.fixture
def assertion_df_min_value_per_protein():
    # create data frame with correct answers
    assertion_list = (
        ["Sample1", "Protein1", "Gene1", 1],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1.0],
        ["Sample2", "Protein2", "Gene2", 20],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 20],
        ["Sample3", "Protein3", "Gene3", 80],
    )
    return pd.DataFrame(
        data=assertion_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

def test_imputation_min_value_per_protein(show_figures, input_imputation_df, assertion_df_min_value_per_protein):
    # generate dummy data
    test_intensity_df = input_imputation_df
    assertion_df = assertion_df_min_value_per_protein
    # perform imputation on test data frame
    test_intensity_df_imputed = by_min_per_protein(test_intensity_df, shrinking_value=1.0)[0]

    if show_figures:
        fig1, fig2 = by_min_per_protein_plot(df=input_imputation_df)
        fig1.show()
        fig2.show()



    # test whether dataframes match
    assert test_intensity_df_imputed.equals(
        assertion_df
    ), f"Imputation by min value per protein does not match!\
             Imputation should be \
            {assertion_df} but is {test_intensity_df_imputed}"

@pytest.fixture
def assertion_df_mean_per_protein():
    # create data frame with correct answers
    assertion_list = (
        ["Sample1", "Protein1", "Gene1", 50.5],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1.0],
        ["Sample2", "Protein2", "Gene2", 20],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 20],
        ["Sample3", "Protein3", "Gene3", 80],
    )
    return pd.DataFrame(
        data=assertion_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

def test_imputation_mean_per_protein(show_figures, input_imputation_df, assertion_df_mean_per_protein):
    # generate dummy data
    test_intensity_df = input_imputation_df
    assertion_df = assertion_df_mean_per_protein
    # perform imputation on test data frame
    test_intensity_df_imputed = by_simple_imputer(
        test_intensity_df,
        strategy="mean",
    )[0]

    if show_figures:
        fig1, fig2 = by_simple_imputer_plot(df=input_imputation_df)
        fig1.show()
        fig2.show()



    # test whether dataframes match
    assert test_intensity_df_imputed.equals(
        assertion_df
    ), f"Imputation by simple median imputation per protein does not match!\
             Imputation should be \
            {assertion_df} but is {test_intensity_df_imputed}"

def test_number_of_imputed_values(input_imputation_df, assertion_df_knn):
    count = number_of_imputed_values(input_imputation_df, assertion_df_knn)
    assert (
            count == 3
    ), f"Wrong number of imputed samples\
               3 but is {count}"


def test_imputation_knn(show_figures, input_imputation_df, assertion_df_knn):
    # perform imputation on test data frame
    imputed_df = by_knn(
        input_imputation_df,
        n_neighbors=2,
    )[0]

    if show_figures:
        fig1, fig2 = by_knn_plot(df=input_imputation_df)
        fig1.show()
        fig2.show()

    # test whether dataframes match
    assert imputed_df.equals(
        assertion_df_knn
    ), f"Imputation by simple median imputation per protein does not match!\n\
             Imputation should be \n\
            {assertion_df_knn} but is\n {imputed_df}"
