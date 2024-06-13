import pytest

from protzilla.data_analysis.ptm_analysis import filter_peptides_of_protein
from tests.conftest import peptides_df


def test_filter_peptides_of_protein(peptides_df):
    filtered_peptides_df = filter_peptides_of_protein(peptides_df, ["Protein2"])["peptide_df"]

    assert len(filtered_peptides_df) == 6
    assert filtered_peptides_df["Sequence"].tolist() == [
        "SEQB", "SEQC", "SEQD", "SEQK", "SEQP", "SEQU"
    ]
    assert (filtered_peptides_df["Protein ID"] == "Protein2").all()