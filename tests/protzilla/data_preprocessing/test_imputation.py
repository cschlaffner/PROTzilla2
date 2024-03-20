import pytest

from protzilla.data_preprocessing.imputation import (
    by_knn,
    by_knn_plot,
    by_min_per_dataset,
    by_min_per_dataset_plot,
    by_min_per_protein,
    by_min_per_protein_plot,
    by_min_per_sample,
    by_min_per_sample_plot,
    by_normal_distribution_sampling,
    by_normal_distribution_sampling_plot,
    by_simple_imputer,
    by_simple_imputer_plot,
    np,
    number_of_imputed_values,
    pd,
)
from tests.protzilla.data_preprocessing import test_plots_data_preprocessing


def protein_group_intensities(dataframe, protein_group_name):
    # small helper function for tests
    return dataframe[dataframe["Protein ID"] == protein_group_name]["Intensity"]


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

    input_imputation_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return input_imputation_df


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


@pytest.fixture
def assertion_df_min_value_per_sample():
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


@pytest.fixture
def assertion_df_min_value_per_protein():
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


@pytest.fixture
def assertion_df_mean_per_protein():
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


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_build_box_hist_plot"])
def test_imputation_min_value_per_df(
    show_figures, input_imputation_df, assertion_df_min_value_per_df
):
    assertion_df = assertion_df_min_value_per_df

    # perform imputation on test data frame
    result_df = by_min_per_dataset(input_imputation_df, shrinking_value=0.1)[0]

    fig1, fig2 = by_min_per_dataset_plot(
        input_imputation_df,
        result_df,
        {},
        "Boxplot",
        "Bar chart",
        "Sample",
        ["Protein1", "Protein2"],
        "linear",
    )
    if show_figures:
        fig1.show()
        fig2.show()

    # test whether dataframes match
    assert result_df.equals(
        assertion_df
    ), f"Imputation by min value per df does not match!\
             Imputation should be \
            {assertion_df} but is {result_df}"


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_build_box_hist_plot"])
def test_imputation_min_value_per_sample(
    show_figures, input_imputation_df, assertion_df_min_value_per_sample
):
    assertion_df = assertion_df_min_value_per_sample

    # perform imputation on test data frame
    result_df = by_min_per_sample(input_imputation_df, shrinking_value=0.2)[0]

    fig1, fig2 = by_min_per_sample_plot(
        input_imputation_df,
        result_df,
        {},
        "Boxplot",
        "Bar chart",
        "Sample",
        ["Protein1", "Protein2"],
        "linear",
    )
    if show_figures:
        fig1.show()
        fig2.show()

    # test whether dataframes match
    assert result_df.equals(
        assertion_df
    ), f"Imputation by min value per sample does not match!\
             Imputation should be \
            {assertion_df} but is {result_df}"


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_build_box_hist_plot"])
def test_imputation_min_value_per_protein(
    show_figures, input_imputation_df, assertion_df_min_value_per_protein
):
    assertion_df = assertion_df_min_value_per_protein

    # perform imputation on test data frame
    result_df = by_min_per_protein(input_imputation_df, shrinking_value=1.0)[0]

    fig1, fig2 = by_min_per_protein_plot(
        input_imputation_df,
        result_df,
        {},
        "Boxplot",
        "Bar chart",
        "Sample",
        ["Protein1", "Protein2"],
        "linear",
    )
    if show_figures:
        fig1.show()
        fig2.show()

    # test whether dataframes match
    assert result_df.equals(
        assertion_df
    ), f"Imputation by min value per protein does not match!\
             Imputation should be \
            {assertion_df} but is {result_df}"


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_build_box_hist_plot"])
def test_imputation_mean_per_protein(
    show_figures, input_imputation_df, assertion_df_mean_per_protein
):
    assertion_df = assertion_df_mean_per_protein

    # perform imputation on test data frame
    result_df = by_simple_imputer(
        input_imputation_df,
        strategy="mean",
    )[0]

    fig1, fig2 = by_simple_imputer_plot(
        input_imputation_df,
        result_df,
        {},
        "Boxplot",
        "Bar chart",
        "Sample",
        ["Protein1", "Protein2"],
        "linear",
    )
    if show_figures:
        fig1.show()
        fig2.show()

    # test whether dataframes match
    assert result_df.equals(
        assertion_df
    ), f"Imputation by simple median imputation per protein does not match!\
             Imputation should be \
            {assertion_df} but is {result_df}"


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_build_box_hist_plot"])
def test_imputation_knn(show_figures, input_imputation_df, assertion_df_knn):
    assertion_df = assertion_df_knn

    # perform imputation on test data frame
    result_df = by_knn(
        input_imputation_df,
        number_of_neighbours=2,
    )[0]

    fig1, fig2 = by_knn_plot(
        input_imputation_df,
        result_df,
        {},
        "Boxplot",
        "Bar chart",
        "Sample",
        ["Protein1", "Protein2"],
        "linear",
    )
    if show_figures:
        fig1.show()
        fig2.show()

    # test whether dataframes match
    assert result_df.equals(
        assertion_df
    ), f"Imputation by simple median imputation per protein does not match!\n\
             Imputation should be \n\
            {assertion_df} but is\n {result_df}"


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_build_box_hist_plot"])
def test_imputation_normal_distribution_sampling(show_figures, input_imputation_df):
    # perform imputation on test data frame
    result_df_perProtein = by_normal_distribution_sampling(
        input_imputation_df, strategy="perProtein", down_shift=-10
    )[0]
    result_df_perDataset = by_normal_distribution_sampling(
        input_imputation_df, strategy="perDataset", down_shift=-10
    )[0]

    fig1, fig2 = by_normal_distribution_sampling_plot(
        input_imputation_df,
        result_df_perProtein,
        {},
        "Boxplot",
        "Bar chart",
        "Sample",
        ["Protein1", "Protein2"],
        "linear",
    )
    if show_figures:
        fig1.show()
        fig2.show()

    assert (
        result_df_perProtein["Intensity"].min() >= 0
    ), f"Imputation by normal distribution sampling should not have negative values!"
    assert (
        result_df_perDataset["Intensity"].min() >= 0
    ), f"Imputation by normal distribution sampling should not have negative values!"

    assert (
        False == protein_group_intensities(result_df_perProtein, "Protein1").hasnans
    ) and (
        False == protein_group_intensities(result_df_perProtein, "Protein3").hasnans
    ), f"Imputation by normal distribution sampling should not have NaN values!"
    assert protein_group_intensities(
        result_df_perProtein, "Protein2"
    ).hasnans, f"This protein group should have NaN values! Not enough data points to sample from!"
    assert (
        False == result_df_perDataset["Intensity"].hasnans
    ), f"Imputation by normal distribution sampling per Dataset should not have NaN values!"


def test_number_of_imputed_values(input_imputation_df, assertion_df_knn):
    count = number_of_imputed_values(input_imputation_df, assertion_df_knn)
    assert (
        count == 3
    ), f"Wrong number of imputed samples\
               3 but is {count}"


@pytest.mark.order(1)
@pytest.mark.dependency()
def test_build_box_hist_plot(
    show_figures, input_imputation_df, assertion_df_knn, assertion_df_min_value_per_df
):
    test_plots_data_preprocessing.test_build_box_hist_plot(
        show_figures,
        input_imputation_df,
        assertion_df_knn,
        assertion_df_min_value_per_df,
    )
