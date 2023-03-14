import pytest

from protzilla.data_preprocessing import imputation
from protzilla.data_preprocessing.plots import *

# this tests will build some Figures and display them if show_figures==True
# it tests only for occurring errors

# for reviewers: all these tests are  new
@pytest.mark.dependency(depends=["test_create_pie_plot","test_create_box_plots"])
def test_build_box_hist_plot(show_figures, input_imputation_df, assertion_df_knn, assertion_df_min_value_per_df):

    fig1, fig2 = imputation._build_box_hist_plot(input_imputation_df, assertion_df_knn, ["Boxplot", "Bar chart"],
                                                 "Sample")
    fig3, fig4 = imputation._build_box_hist_plot(input_imputation_df, assertion_df_min_value_per_df,
                                                 ["Histogram", "Pie chart"],
                                                 "Protein ID")

    if show_figures:
        fig1.show()
        fig2.show()
        fig3.show()
        fig4.show()
    return


def test_create_pie_plot(show_figures):
    fig = create_pie_plot(
        names_of_sectors=["Non-imputed values", "Imputed values"],
        values_of_sectors=values_of_sectors, #TODO
        heading="Number of Imputed Values",
    )

def test_create_bar_plot()


def test_create_box_plots(show_figures, input_imputation_df, assertion_df_knn, assertion_df_min_value_per_df):
    # only tests for no error
    fig = create_box_plots(
        dataframe_a=input_imputation_df,
        dataframe_b=assertion_df_knn,
        name_a="Before Transformation",
        name_b="After Transformation",
        heading="Distribution of Protein Intensities",
        group_by="None",
    )
    if show_figures:
        fig.show()
    # should throw Value Error
    with pytest.raises(ValueError):
        create_box_plots(
            dataframe_a=input_imputation_df,
            dataframe_b=assertion_df_knn,
            group_by="wrong_group_by")
    return

def test_create_histograms(show_figures, input_imputation_df, assertion_df_knn, assertion_df_min_value_per_df):
    fig = create_histograms(
        dataframe_a=df,
        dataframe_b=result_df,
        name_a="Before Imputation",
        name_b="After Imputation",
        heading="Distribution of Protein Intensities",
    )

def test_create_anomaly_score_bar_plot()

def test_create_pca_2d_scatter_plot(

def test_create_pca_3d_scatter_plot