"""import numpy as np
import pandas as pd
import pytest
import math
from scipy import stats

from protzilla.data_analysis.power_analysis import (
    power_calculation,
    sample_size_calculation,
    variance_protein_group_calculation_max,
)
from tests.protzilla.data_analysis.power_analysis_validation import (
    check_sample_size_calculation_with_libfunc,
    check_sample_size_calculation_protzilla,
    check_sample_size_calculation_protzilla_without_log,
)
from test_differential_expression import diff_expr_test_data


@pytest.fixture
def power_test_data():
    test_differentially_expressed_proteins_list = (
        ["Sample1", "Protein1", "Gene1", 18, "Group1"],
        ["Sample1", "Protein2", "Gene1", 16, "Group1"],
        ["Sample1", "Protein3", "Gene1", 1, "Group1"],
        ["Sample1", "Protein4", "Gene1", 14, "Group1"],
        ["Sample2", "Protein1", "Gene1", 19, "Group1"],
        ["Sample2", "Protein2", "Gene1", 15, "Group1"],
        ["Sample2", "Protein3", "Gene1", 2, "Group1"],
        ["Sample2", "Protein4", "Gene1", 15, "Group1"],
        ["Sample3", "Protein1", "Gene1", 22, "Group1"],
        ["Sample3", "Protein2", "Gene1", 14, "Group1"],
        ["Sample3", "Protein3", "Gene1", 3, "Group1"],
        ["Sample3", "Protein4", "Gene1", 16, "Group1"],
        ["Sample4", "Protein1", "Gene1", 16, "Group1"],
        ["Sample4", "Protein2", "Gene1", 14, "Group1"],
        ["Sample4", "Protein3", "Gene1", 3, "Group1"],
        ["Sample4", "Protein4", "Gene1", 16, "Group1"],
        ["Sample5", "Protein1", "Gene1", 24, "Group1"],
        ["Sample5", "Protein2", "Gene1", 14, "Group1"],
        ["Sample5", "Protein3", "Gene1", 3, "Group1"],
        ["Sample5", "Protein4", "Gene1", 16, "Group1"],
        ["Sample6", "Protein1", "Gene1", 21, "Group1"],
        ["Sample6", "Protein2", "Gene1", 14, "Group1"],
        ["Sample6", "Protein3", "Gene1", 3, "Group1"],
        ["Sample6", "Protein4", "Gene1", 16, "Group1"],
        ["Sample7", "Protein1", "Gene1", 8, "Group2"],
        ["Sample7", "Protein2", "Gene1", 15, "Group2"],
        ["Sample7", "Protein3", "Gene1", 1, "Group2"],
        ["Sample7", "Protein4", "Gene1", 9, "Group2"],
        ["Sample8", "Protein1", "Gene1", 9, "Group2"],
        ["Sample8", "Protein2", "Gene1", 14, "Group2"],
        ["Sample8", "Protein3", "Gene1", 2, "Group2"],
        ["Sample8", "Protein4", "Gene1", 10, "Group2"],
        ["Sample9", "Protein1", "Gene1", 12, "Group2"],
        ["Sample9", "Protein2", "Gene1", 13, "Group2"],
        ["Sample9", "Protein3", "Gene1", 3, "Group2"],
        ["Sample9", "Protein4", "Gene1", 11, "Group2"],
        ["Sample10", "Protein1", "Gene1", 6, "Group2"],
        ["Sample10", "Protein2", "Gene1", 13, "Group2"],
        ["Sample10", "Protein3", "Gene1", 3, "Group2"],
        ["Sample10", "Protein4", "Gene1", 11, "Group2"],
        ["Sample11", "Protein1", "Gene1", 14, "Group2"],
        ["Sample11", "Protein2", "Gene1", 13, "Group2"],
        ["Sample11", "Protein3", "Gene1", 3, "Group2"],
        ["Sample11", "Protein4", "Gene1", 11, "Group2"],
        ["Sample12", "Protein1", "Gene1", 11, "Group2"],
        ["Sample12", "Protein2", "Gene1", 13, "Group2"],
        ["Sample12", "Protein3", "Gene1", 3, "Group2"],
        ["Sample12", "Protein4", "Gene1", 11, "Group2"],
    )

    test_differentially_expressed_proteins_df = pd.DataFrame(
        data=test_differentially_expressed_proteins_list,
        columns=["Sample", "Protein ID", "Gene", "Normalised iBAQ", "Group"],
    )
    return test_differentially_expressed_proteins_df

@pytest.fixture
def power_test_data_intensity_values():
    test_differentially_expressed_proteins_list = (
        ["Sample1", "Protein1", "Gene1", -1.56714, "Group1"],
        ["Sample1", "Protein2", "Gene1", 16, "Group1"],
        ["Sample1", "Protein3", "Gene1", 1, "Group1"],
        ["Sample1", "Protein4", "Gene1", 14, "Group1"],
        ["Sample2", "Protein1", "Gene1", -0.37691, "Group1"],
        ["Sample2", "Protein2", "Gene1", 15, "Group1"],
        ["Sample2", "Protein3", "Gene1", 2, "Group1"],
        ["Sample2", "Protein4", "Gene1", 15, "Group1"],
        ["Sample3", "Protein1", "Gene1", 0.38817, "Group1"],
        ["Sample3", "Protein2", "Gene1", 14, "Group1"],
        ["Sample3", "Protein3", "Gene1", 3, "Group1"],
        ["Sample3", "Protein4", "Gene1", 16, "Group1"],
        ["Sample4", "Protein1", "Gene1", 1.6, "Group1"],
        ["Sample4", "Protein2", "Gene1", 14, "Group1"],
        ["Sample4", "Protein3", "Gene1", 3, "Group1"],
        ["Sample4", "Protein4", "Gene1", 16, "Group1"],
        ["Sample5", "Protein1", "Gene1", 1.9, "Group1"],
        ["Sample5", "Protein2", "Gene1", 14, "Group1"],
        ["Sample5", "Protein3", "Gene1", 3, "Group1"],
        ["Sample5", "Protein4", "Gene1", 16, "Group1"],
        ["Sample6", "Protein1", "Gene1", -0.07, "Group1"],
        ["Sample6", "Protein2", "Gene1", 14, "Group1"],
        ["Sample6", "Protein3", "Gene1", 3, "Group1"],
        ["Sample6", "Protein4", "Gene1", 16, "Group1"],
        ["Sample7", "Protein1", "Gene1", 0.9819, "Group2"],
        ["Sample7", "Protein2", "Gene1", 15, "Group2"],
        ["Sample7", "Protein3", "Gene1", 1, "Group2"],
        ["Sample7", "Protein4", "Gene1", 9, "Group2"],
        ["Sample8", "Protein1", "Gene1", -0.26, "Group2"],
        ["Sample8", "Protein2", "Gene1", 13, "Group2"],
        ["Sample8", "Protein3", "Gene1", 3, "Group2"],
        ["Sample8", "Protein4", "Gene1", 11, "Group2"],
        ["Sample9", "Protein1", "Gene1", 1.116, "Group2"],
        ["Sample9", "Protein2", "Gene1", 14, "Group2"],
        ["Sample9", "Protein3", "Gene1", 3, "Group2"],
        ["Sample9", "Protein4", "Gene1", 16, "Group2"],
        ["Sample10", "Protein1", "Gene1", 0.81, "Group2"],
        ["Sample10", "Protein2", "Gene1", 14, "Group2"],
        ["Sample10", "Protein3", "Gene1", 3, "Group2"],
        ["Sample10", "Protein4", "Gene1", 16, "Group2"],
        ["Sample11", "Protein1", "Gene1", 1.336, "Group2"],
        ["Sample11", "Protein2", "Gene1", 14, "Group2"],
        ["Sample11", "Protein3", "Gene1", 3, "Group2"],
        ["Sample11", "Protein4", "Gene1", 16, "Group2"],
        ["Sample12", "Protein1", "Gene1", 1.81, "Group2"],
        ["Sample12", "Protein2", "Gene1", 14, "Group2"],
        ["Sample12", "Protein3", "Gene1", 2, "Group2"],
        ["Sample12", "Protein4", "Gene1", 10, "Group2"],
    )

    test_differentially_expressed_proteins_df = pd.DataFrame(
        data=test_differentially_expressed_proteins_list,
        columns=["Sample", "Protein ID", "Gene", "Normalised iBAQ", "Group"],
    )
    return test_differentially_expressed_proteins_df


def test_variance_protein_group_calculation(power_test_data):
    intensity_df = power_test_data

    protein_id = "Protein1"
    group1 = "Group1"
    group2 = "Group2"

    variance = variance_protein_group_calculation_max(
        intensity_df, protein_id, group1, group2
    )
    print(variance)
    assert variance == 4.0


def test_sample_size_calculation(power_test_data, diff_expr_test_data):
    test_alpha = 0.05
    test_power = 0.8
    test_fc_threshold = 1
    test_selected_protein_group = "Protein1"
    test_individual_column = "None"
    test_differentially_expressed_proteins_df, test_metadata_df = diff_expr_test_data

    required_sample_size = sample_size_calculation(
        differentially_expressed_proteins_df=power_test_data,
        significant_proteins_df=power_test_data,
        metadata_df=test_metadata_df,
        fc_threshold=test_fc_threshold,
        power=test_power,
        alpha=test_alpha,
        group1="Group1",
        group2="Group2",
        selected_protein_group=test_selected_protein_group,
        individual_column=test_individual_column,
        intensity_name=None,
    )
    print(required_sample_size)
    required_sample_size_int = next(iter(required_sample_size.values()), None)
    assert required_sample_size_int == 63


def test_power_calculation(power_test_data, diff_expr_test_data):
    test_alpha = 0.05
    test_fc_threshold = 1
    test_selected_protein_group = "Protein1"
    test_individual_column = "None"
    test_differentially_expressed_proteins_df, test_metadata_df = diff_expr_test_data

    power = power_calculation(
        differentially_expressed_proteins_df=power_test_data,
        significant_proteins_df=power_test_data,
        metadata_df=test_metadata_df,
        fc_threshold=test_fc_threshold,
        alpha=test_alpha,
        group1="Group1",
        group2="Group2",
        selected_protein_group=test_selected_protein_group,
        individual_column=test_individual_column,
        intensity_name=None,
    )
    print(power)
    power_int = next(iter(power.values()), None)
    assert power_int == 0.09

#TODO: The following tests has been used for thesis calculations. Should not be merged to dev branch.

def test_check_sample_size_calculation_with_libfun_intensity_values(power_test_data_intensity_values):
    test_alpha = 0.05
    test_power = 0.8
    test_fc_threshold = 5
    test_selected_protein_group = "Protein1"

    required_sample_size = check_sample_size_calculation_with_libfunc(
        differentially_expressed_proteins_df=power_test_data_intensity_values,
        significant_proteins_df=power_test_data_intensity_values,
        fc_threshold=test_fc_threshold,
        power=test_power,
        alpha=test_alpha,
        group1="Group1",
        group2="Group2",
        selected_protein_group=test_selected_protein_group,
        intensity_name=None,
    )
    print(required_sample_size)
    required_sample_size_int = next(iter(required_sample_size.values()), None)
    assert required_sample_size_int == 63

def test_check_sample_size_calculation_protzilla_intensity_values(power_test_data_intensity_values):
    test_alpha = 0.05
    test_power = 0.8
    test_fc_threshold = 1
    test_selected_protein_group = "Protein1"

    required_sample_size = check_sample_size_calculation_protzilla(
        differentially_expressed_proteins_df=power_test_data_intensity_values,
        significant_proteins_df=power_test_data_intensity_values,
        fc_threshold=test_fc_threshold,
        power=test_power,
        alpha=test_alpha,
        group1="Group1",
        group2="Group2",
        selected_protein_group=test_selected_protein_group,
        intensity_name=None,
    )
    print(required_sample_size)
    required_sample_size_int = next(iter(required_sample_size.values()), None)
    assert required_sample_size_int == 1

def test_check_sample_size_calculation_with_libfun(power_test_data):
    test_alpha = 0.05
    test_power = 0.8
    test_fc_threshold = 5
    test_selected_protein_group = "Protein1"

    required_sample_size = check_sample_size_calculation_with_libfunc(
        differentially_expressed_proteins_df=power_test_data,
        significant_proteins_df=power_test_data,
        fc_threshold=test_fc_threshold,
        power=test_power,
        alpha=test_alpha,
        group1="Group1",
        group2="Group2",
        selected_protein_group=test_selected_protein_group,
        intensity_name=None,
    )
    print(required_sample_size)
    required_sample_size_int = next(iter(required_sample_size.values()), None)
    assert required_sample_size_int == 63

def test_check_sample_size_calculation_protzilla(power_test_data):
    test_alpha = 0.05
    test_power = 0.8
    power_test_data_log2 = power_test_data.copy()
    power_test_data_log2["Normalised iBAQ"] = np.log2(
        power_test_data_log2["Normalised iBAQ"]
    )
    fc_threshold = 1
    test_selected_protein_group = "Protein1"

    required_sample_size = check_sample_size_calculation_protzilla(
        differentially_expressed_proteins_df=power_test_data_log2,
        significant_proteins_df=power_test_data,
        fc_threshold=fc_threshold,
        power=test_power,
        alpha=test_alpha,
        group1="Group1",
        group2="Group2",
        selected_protein_group=test_selected_protein_group,
        intensity_name=None,
    )
    print(required_sample_size)
    required_sample_size_int = next(iter(required_sample_size.values()), None)
    assert required_sample_size_int == 1


def test_check_sample_size_calculation_protzilla_without_log(power_test_data):
    test_alpha = 0.05
    test_power = 0.8
    test_fc_threshold = 5
    test_selected_protein_group = "Protein1"

    required_sample_size = check_sample_size_calculation_protzilla_without_log(
        differentially_expressed_proteins_df=power_test_data,
        significant_proteins_df=power_test_data,
        fc_threshold=test_fc_threshold,
        power=test_power,
        alpha=test_alpha,
        group1="Group1",
        group2="Group2",
        selected_protein_group=test_selected_protein_group,
        intensity_name=None,
    )
    print(required_sample_size)
    required_sample_size_int = next(iter(required_sample_size.values()), None)
    assert required_sample_size_int == 63

def test_replicate_paper_sample_size_calculation(power_test_data):
    alpha = 0.001
    power = 0.95
    fc_threshold = math.log2(2)
    biological_variance = 0.233
    technical_variance = 2.298
    number_of_replicates = 2

    z_alpha = round(stats.norm.ppf(1 - alpha / 2), 3)
    z_beta = round(stats.norm.ppf(power), 3)

    required_sample_size = (
        2
        * ((z_alpha + z_beta) / fc_threshold) ** 2
        * ((technical_variance / number_of_replicates) + biological_variance)
    )  # Equation (1) in Cairns, David A., et al., 2008, Sample size determination in clinical proteomic profiling experiments using mass spectrometry for class comparison
    required_sample_size = math.ceil(required_sample_size)
    print(required_sample_size)

    data = {
        "Cairns": [44, 31, 62, 44, 14, 10, 19, 14, 5, 4, 7, 5],
        "Calculated": [65, 52, 92, 74, 20, 16, 28, 23, 7, 6, 10, 8],
    }
    df = pd.DataFrame(data)
    correlation = df["Cairns"].corr(df["Calculated"])
    print(correlation)
    correlationmatrix = df.corr()
    print(correlationmatrix)

    return dict(required_sample_size=required_sample_size)
"""