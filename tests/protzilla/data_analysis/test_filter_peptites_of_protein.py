import pytest

from protzilla.data_analysis.ptm_analysis import select_peptides_of_protein


def test_filter_peptides_of_protein(peptides_df):
    filtered_peptides_df = select_peptides_of_protein(peptides_df, ["Protein2"])["peptide_df"]

    assert len(filtered_peptides_df) == 6
    assert filtered_peptides_df["Sequence"].tolist() == [
        "SEQB", "SEQC", "SEQD", "SEQK", "SEQP", "SEQU"
    ]
    assert (filtered_peptides_df["Protein ID"] == "Protein2").all()