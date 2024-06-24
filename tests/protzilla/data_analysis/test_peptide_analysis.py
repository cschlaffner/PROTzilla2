import pytest

from protzilla.data_analysis.ptm_analysis import filter_peptides_of_protein, ptms_per_sample, \
    ptms_per_protein_and_sample


@pytest.mark.parametrize("df_num", [0, 1])
def test_filter_peptides_of_protein(peptides_df, evidence_peptide_df, df_num):
    peptide_df = [peptides_df, evidence_peptide_df][df_num]

    filtered_peptides_df = filter_peptides_of_protein(peptide_df, ["Protein2"])["peptide_df"]

    assert len(filtered_peptides_df) == 6
    assert filtered_peptides_df["Sequence"].tolist() == [
        'SEQB', 'SEQC', 'SEQD', 'SEQK', 'SEQP', 'SEQU'
    ]
    assert (filtered_peptides_df["Protein ID"] == "Protein2").all()


def test_ptms_per_sampel(evidence_peptide_df):
    ptm_df = ptms_per_sample(evidence_peptide_df)["ptm_df"]

    assert ptm_df.columns.tolist() == ["Sample", "Acetyl (Protein N-term)", "Oxidation (M)", "Unmodified"]
    assert ptm_df["Sample"].tolist() == ["Sample1", "Sample2", "Sample3", "Sample4"]
    assert ptm_df["Unmodified"].tolist() == [7, 4, 5, 4]
    assert ptm_df["Acetyl (Protein N-term)"].tolist() == [2, 1, 0, 0]
    assert ptm_df["Oxidation (M)"].tolist() == [1, 0, 0, 0]


def test_ptms_per_protein_and_sample(evidence_peptide_df):
    ptm_df = ptms_per_protein_and_sample(evidence_peptide_df)["ptm_df"]

    assert ptm_df.columns.tolist() == ["Sample", "Protein1", "Protein2", "Protein3", "Protein4", "Protein5"]
    assert ptm_df["Sample"].tolist() == ["Sample1", "Sample2", "Sample3", "Sample4"]
    assert (ptm_df["Protein1"].tolist() ==
            ["(1) Unmodified, ", "(1) Acetyl (Protein N-term), ", "(1) Unmodified, ", "(1) Unmodified, "])
    assert (ptm_df["Protein2"].tolist() ==
            ["(2) Acetyl (Protein N-term), (1) Oxidation (M), (1) Unmodified, ", "(1) Unmodified, ", "(1) Unmodified, ", "(1) Unmodified, "])
    assert (ptm_df["Protein3"].tolist() ==
            ["(3) Unmodified, ", "(1) Unmodified, ", "(1) Unmodified, ", "(1) Unmodified, "])
    assert (ptm_df["Protein4"].tolist() ==
            ["(1) Unmodified, ", "(1) Unmodified, ", "(1) Unmodified, ", "(1) Unmodified, "])
    assert (ptm_df["Protein5"].tolist() ==
            ["(1) Unmodified, ", "(1) Unmodified, ", "(1) Unmodified, ", ""])