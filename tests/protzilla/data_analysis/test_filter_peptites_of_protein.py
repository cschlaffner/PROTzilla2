import pytest

from protzilla.data_analysis.filter_peptieds_of_protein import by_select_protein
from tests.protzilla.data_preprocessing.test_peptide_preprocessing import peptides_df


def test_filter_peptides_of_protein(peptides_df):
    filtered_peptides_df = by_select_protein(peptides_df, ["Protein2"])["peptide_df"]

    assert len(filtered_peptides_df) == 6
    assert filtered_peptides_df["Sequence"].tolist() == [
        "SEQB", "SEQC", "SEQD", "SEQK", "SEQP", "SEQU"
    ]
    assert (filtered_peptides_df["Protein ID"] == "Protein2").all()