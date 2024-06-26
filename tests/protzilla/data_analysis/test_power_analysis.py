import numpy as np
import pandas as pd
import pytest


from protzilla.data_analysis.power_analysis import variance_protein_group_calculation, sample_size_calculation


@pytest.fixture
def power_test_data():
    test_differentially_expressed_proteins_list = (
        ["Sample1", "Protein1", "Gene1", 20, "Group1"],
        ["Sample1", "Protein2", "Gene1", 16, "Group1"],
        ["Sample1", "Protein3", "Gene1", 1, "Group1"],
        ["Sample1", "Protein4", "Gene1", 14, "Group1"],
        ["Sample2", "Protein1", "Gene1", 20, "Group1"],
        ["Sample2", "Protein2", "Gene1", 15, "Group1"],
        ["Sample2", "Protein3", "Gene1", 2, "Group1"],
        ["Sample2", "Protein4", "Gene1", 15, "Group1"],
        ["Sample3", "Protein1", "Gene1", 22, "Group1"],
        ["Sample3", "Protein2", "Gene1", 14, "Group1"],
        ["Sample3", "Protein3", "Gene1", 3, "Group1"],
        ["Sample3", "Protein4", "Gene1", 16, "Group1"],
        ["Sample4", "Protein1", "Gene1", 8, "Group2"],
        ["Sample4", "Protein2", "Gene1", 15, "Group2"],
        ["Sample4", "Protein3", "Gene1", 1, "Group2"],
        ["Sample4", "Protein4", "Gene1", 9, "Group2"],
        ["Sample5", "Protein1", "Gene1", 10, "Group2"],
        ["Sample5", "Protein2", "Gene1", 14, "Group2"],
        ["Sample5", "Protein3", "Gene1", 2, "Group2"],
        ["Sample5", "Protein4", "Gene1", 10, "Group2"],
        ["Sample6", "Protein1", "Gene1", 12, "Group2"],
        ["Sample6", "Protein2", "Gene1", 13, "Group2"],
        ["Sample6", "Protein3", "Gene1", 3, "Group2"],
        ["Sample6", "Protein4", "Gene1", 11, "Group2"],
    )

    test_differentially_expressed_proteins_df = pd.DataFrame(
        data=test_differentially_expressed_proteins_list,
        columns=["Sample", "Protein ID", "Gene", "Normalised iBAQ", "Group"],
    )
    return test_differentially_expressed_proteins_df


def test_variance_protein_group_calculation(
        power_test_data
):
    intensity_df = power_test_data

    protein_id = "Protein1"
    group1 = "Group1"
    group2 = "Group2"

    variance = variance_protein_group_calculation(
        intensity_df, protein_id, group1, group2
    )
    print(variance)
    assert variance == 4.0

def test_sample_size_calculation(
        power_test_data

):
    test_alpha = 0.05
    test_power = 0.8
    test_fc_threshold = 1
    test_selected_protein_group = "Protein1"


    required_sample_size = sample_size_calculation(
        differentially_expressed_proteins_df=power_test_data,
        significant_proteins_df=power_test_data,
        fc_threshold=test_fc_threshold,
        power=test_power,
        alpha=test_alpha,
        group1= "Group1",
        group2= "Group2",
        selected_protein_group=test_selected_protein_group,
        significant_proteins_only=False,
        intensity_name=None
    )
    print(required_sample_size)
    required_sample_size_int = next(iter(required_sample_size.values()),None)
    assert required_sample_size_int == 63






