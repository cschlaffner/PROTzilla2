import pytest

from protzilla.data_analysis.differential_expression_helper import normalize_ptm_df
from protzilla.data_analysis.ptm_analysis import ptms_per_sample


def test_normalize_ptm_df(evidence_peptide_df):
    ptm_df = ptms_per_sample(evidence_peptide_df)["ptm_df"]
    normalized_ptm_df = normalize_ptm_df(ptm_df)

    assert normalized_ptm_df.columns.tolist() == ["Sample", "Acetyl (Protein N-term)", "Oxidation (M)", "Unmodified"]
    assert normalized_ptm_df["Sample"].tolist() == ["Sample1", "Sample2", "Sample3", "Sample4"]
    assert normalized_ptm_df["Unmodified"].tolist() == [0.8, 0.8, 1.0, 1.0]
    assert normalized_ptm_df["Acetyl (Protein N-term)"].tolist() == [0.2, 0.2, 0.0,  0.0]
    assert normalized_ptm_df["Oxidation (M)"].tolist() == [0.1, 0.0, 0.0, 0.0]