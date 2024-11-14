from protzilla.data_analysis.protein_coverage import align_peptide_to_protein_sequence


def test_aligns_peptide_at_start():
    peptide = "MKT"
    protein_sequence = "MKTLLL"
    expected_indices = [0]
    assert (
        align_peptide_to_protein_sequence(peptide, protein_sequence) == expected_indices
    )


def test_aligns_peptide_in_middle():
    peptide = "KTL"
    protein_sequence = "MKTLLL"
    expected_indices = [1]
    assert (
        align_peptide_to_protein_sequence(peptide, protein_sequence) == expected_indices
    )


def test_aligns_peptide_at_end():
    peptide = "LLL"
    protein_sequence = "MKTLLL"
    expected_indices = [3]
    assert (
        align_peptide_to_protein_sequence(peptide, protein_sequence) == expected_indices
    )


def test_aligns_multiple_occurrences():
    peptide = "LL"
    protein_sequence = "MKTLLLL"
    expected_indices = [3, 4, 5]
    assert (
        align_peptide_to_protein_sequence(peptide, protein_sequence) == expected_indices
    )


def aligns_no_occurrences():
    peptide = "XYZ"
    protein_sequence = "MKTLLL"
    expected_indices = []
    assert (
        align_peptide_to_protein_sequence(peptide, protein_sequence) == expected_indices
    )


def test_aligns_empty_peptide():
    peptide = ""
    protein_sequence = "MKTLLL"
    expected_indices = []
    assert (
        align_peptide_to_protein_sequence(peptide, protein_sequence) == expected_indices
    )


def test_aligns_empty_protein_sequence():
    peptide = "MKT"
    protein_sequence = ""
    expected_indices = []
    assert (
        align_peptide_to_protein_sequence(peptide, protein_sequence) == expected_indices
    )


def test_aligns_peptide_longer_than_protein_sequence():
    peptide = "MKTLLL"
    protein_sequence = "MKT"
    expected_indices = []
    assert (
        align_peptide_to_protein_sequence(peptide, protein_sequence) == expected_indices
    )
