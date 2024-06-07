import pytest

from protzilla.data_analysis.ptm_analysis import filter_peptides_of_protein, ptms_per_sampel
from tests.protzilla.data_preprocessing.test_peptide_preprocessing import peptides_df, evidence_peptide_df


@pytest.mark.parametrize("df_num", [0, 1])
def test_filter_peptides_of_protein(peptides_df, evidence_peptide_df, df_num):
    peptide_df = [peptides_df, evidence_peptide_df][df_num]

    filtered_peptides_df = filter_peptides_of_protein(peptide_df, "Protein2")["peptide_df"]

    assert len(filtered_peptides_df) == 6
    assert filtered_peptides_df["Sequence"].tolist() == [
        'SEQB', 'SEQC', 'SEQD', 'SEQK', 'SEQP', 'SEQU'
    ]
    assert (filtered_peptides_df["Protein ID"] == "Protein2").all()


def test_ptms_per_sampel(evidence_peptide_df):
    ptm_df = ptms_per_sampel(evidence_peptide_df)["ptm_df"]

    assert ptm_df.columns.tolist() == ["Sample", "Unmodified", "Acetyl (Protein N-term)", "Oxidation (M)"]
    assert ptm_df["Sample"].tolist() == ["Sample1", "Sample2", "Sample3", "Sample4"]
    assert ptm_df["Unmodified"].tolist() == [7, 4, 5, 4]
    assert ptm_df["Acetyl (Protein N-term)"].tolist() == [2, 1, 0, 0]
    assert ptm_df["Oxidation (M)"].tolist() == [1, 0, 0, 0]