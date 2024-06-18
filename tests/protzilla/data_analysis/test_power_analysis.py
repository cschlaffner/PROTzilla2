import numpy as np
import pandas as pd
import pytest

from protzilla.data_analysis.power_analysis import variance_protein_group_calculation, sample_size_calculation
from tests.protzilla.data_analysis.test_differential_expression import diff_expr_test_data

def test_variance_protein_group_calculation(
        diff_expr_test_data
):
    intensity_df, metadata_df = diff_expr_test_data

    protein_id = "Protein1"
    group1 = "Group1"
    group2 = "Group2"

    variance = variance_protein_group_calculation(
        intensity_df, metadata_df, protein_id, group1, group2
    )

    assert variance == 4.0
    print(variance)




