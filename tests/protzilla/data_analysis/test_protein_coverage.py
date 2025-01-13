import pytest
from protzilla.data_analysis.protein_coverage import (
    distribute_to_rows,
    get_max_coverage,
    PeptideMatch,
)

import pytest
import pandas as pd
from protzilla.data_analysis.protein_coverage import (
    extract_peptide_from_slice,
    AggregationMethod,
)

import pytest
from protzilla.data_analysis.protein_coverage import increment_coverage, ProteinHit

import pytest
from protzilla.data_analysis.protein_coverage import (
    match_peptide_to_protein_ids,
    ProteinHit,
)


def test_match_peptide_to_protein_ids_empty_peptide():
    with pytest.raises(ValueError, match="Peptide sequence is empty."):
        match_peptide_to_protein_ids("", {}, {})


def test_match_peptide_to_protein_ids_no_matches():
    peptide_sequence = "ABCDE"
    protein_kmer_dictionary = {"ABCDE": [("protein1", 0)]}
    protein_dictionary = {"protein1": "XYZ"}
    result = match_peptide_to_protein_ids(
        peptide_sequence, protein_kmer_dictionary, protein_dictionary
    )
    assert result == []


def test_match_peptide_to_protein_ids_single_match():
    peptide_sequence = "ABCDE"
    protein_kmer_dictionary = {"ABCDE": [("protein1", 0)]}
    protein_dictionary = {"protein1": "ABCDE"}
    result = match_peptide_to_protein_ids(
        peptide_sequence, protein_kmer_dictionary, protein_dictionary
    )
    expected = [
        ProteinHit(
            protein_id="protein1",
            start_location_on_protein=0,
            end_location_on_protein=5,
        )
    ]
    assert result == expected


def test_match_peptide_to_protein_ids_multiple_matches():
    peptide_sequence = "ABCDE"
    protein_kmer_dictionary = {"ABCDE": [("protein1", 0), ("protein2", 0)]}
    protein_dictionary = {"protein1": "ABCDE", "protein2": "ABCDE"}
    result = match_peptide_to_protein_ids(
        peptide_sequence, protein_kmer_dictionary, protein_dictionary
    )
    expected = list(
        set(
            [
                ProteinHit(
                    protein_id="protein1",
                    start_location_on_protein=0,
                    end_location_on_protein=5,
                ),
                ProteinHit(
                    protein_id="protein2",
                    start_location_on_protein=0,
                    end_location_on_protein=5,
                ),
            ]
        )
    )
    assert result == expected


def test_match_peptide_to_protein_ids_partial_match():
    peptide_sequence = "ABCDE"
    protein_kmer_dictionary = {"ABCDE": [("protein1", 0)]}
    protein_dictionary = {"protein1": "ABCDEXYZ"}
    result = match_peptide_to_protein_ids(
        peptide_sequence, protein_kmer_dictionary, protein_dictionary
    )
    expected = [
        ProteinHit(
            protein_id="protein1",
            start_location_on_protein=0,
            end_location_on_protein=5,
        )
    ]
    assert result == expected


def test_increment_coverage():
    coverage = [0, 0, 0, 0, 0]
    protein_hit = ProteinHit(
        protein_id="P12345", start_location_on_protein=1, end_location_on_protein=4
    )
    increment_coverage(coverage, protein_hit)
    assert coverage == [0, 1, 1, 1, 0]


def test_increment_coverage_multiple_hits():
    coverage = [0, 0, 0, 0, 0]
    protein_hit1 = ProteinHit(
        protein_id="P12345", start_location_on_protein=1, end_location_on_protein=3
    )
    protein_hit2 = ProteinHit(
        protein_id="P12345", start_location_on_protein=2, end_location_on_protein=4
    )
    increment_coverage(coverage, protein_hit1)
    increment_coverage(coverage, protein_hit2)
    assert coverage == [0, 1, 2, 1, 0]


def test_increment_coverage_no_overlap():
    coverage = [0, 0, 0, 0, 0]
    protein_hit1 = ProteinHit(
        protein_id="P12345", start_location_on_protein=0, end_location_on_protein=2
    )
    protein_hit2 = ProteinHit(
        protein_id="P12345", start_location_on_protein=3, end_location_on_protein=5
    )
    increment_coverage(coverage, protein_hit1)
    increment_coverage(coverage, protein_hit2)
    assert coverage == [1, 1, 0, 1, 1]


def test_extract_peptide_from_slice_single_entry():
    data = {"Sequence": ["PEPTIDE"], "Intensity": [100]}
    df = pd.DataFrame(data)
    result = extract_peptide_from_slice(df)
    assert result.equals(df)


def test_extract_peptide_from_slice_multiple_entries():
    data = {"Sequence": ["PEPTIDE", "PEPTIDE", "PEPTIDE"], "Intensity": [100, 130, 200]}
    df = pd.DataFrame(data)
    result = extract_peptide_from_slice(df)
    expected = pd.DataFrame({"Sequence": "PEPTIDE", "Intensity": [130.0]})
    expected.set_index("Sequence", inplace=True)
    assert result.equals(expected)


def test_extract_peptide_from_slice_median():
    data = {"Sequence": ["PEPTIDE", "PEPTIDE"], "Intensity": [100, 200]}
    df = pd.DataFrame(data)
    result = extract_peptide_from_slice(df, AggregationMethod.median)
    expected = pd.DataFrame({"Sequence": "PEPTIDE", "Intensity": [150.0]})
    expected.set_index("Sequence", inplace=True)
    assert result.equals(expected)


def test_extract_peptide_from_slice_mean():
    data = {"Sequence": ["PEPTIDE", "PEPTIDE"], "Intensity": [100, 200]}
    df = pd.DataFrame(data)
    result = extract_peptide_from_slice(df, AggregationMethod.mean)
    expected = pd.DataFrame({"Sequence": "PEPTIDE", "Intensity": [150.0]})
    expected.set_index("Sequence", inplace=True)
    assert result.equals(expected)


def test_extract_peptide_from_slice_unknown_strategy():
    data = {"Sequence": ["PEPTIDE", "PEPTIDE"], "Intensity": [100, 200]}
    df = pd.DataFrame(data)
    with pytest.raises(ValueError, match="Unknown strategy: unknown"):
        extract_peptide_from_slice(df, "unknown")


import pytest
from protzilla.data_analysis.protein_coverage import distribute_to_rows, PeptideMatch


def test_distribute_to_rows_empty():
    with pytest.raises(
        ValueError,
        match="Attempted to distribute empty list of peptide matches to rows in plot.",
    ):
        distribute_to_rows([])


def test_distribute_to_rows_single_peptide():
    peptide_matches = [
        PeptideMatch(
            peptide_sequence="AAA",
            start_location_on_protein=0,
            end_location_on_protein=3,
            metadata_group="group1",
        )
    ]
    expected = {"group1": [[peptide_matches[0]]]}
    assert distribute_to_rows(peptide_matches) == expected


def test_distribute_to_rows_non_overlapping():
    peptide_matches = [
        PeptideMatch(
            peptide_sequence="AAA",
            start_location_on_protein=0,
            end_location_on_protein=3,
            metadata_group="group1",
        ),
        PeptideMatch(
            peptide_sequence="BBB",
            start_location_on_protein=4,
            end_location_on_protein=7,
            metadata_group="group1",
        ),
    ]
    expected = {"group1": [[peptide_matches[0], peptide_matches[1]]]}
    assert distribute_to_rows(peptide_matches) == expected


def test_distribute_to_rows_overlapping():
    peptide_matches = [
        PeptideMatch(
            peptide_sequence="AAA",
            start_location_on_protein=0,
            end_location_on_protein=3,
            metadata_group="group1",
        ),
        PeptideMatch(
            peptide_sequence="BBB",
            start_location_on_protein=2,
            end_location_on_protein=5,
            metadata_group="group1",
        ),
    ]
    expected = {"group1": [[peptide_matches[0]], [peptide_matches[1]]]}
    assert distribute_to_rows(peptide_matches) == expected


def test_distribute_to_rows_multiple_groups():
    peptide_matches = [
        PeptideMatch(
            peptide_sequence="AAA",
            start_location_on_protein=0,
            end_location_on_protein=3,
            metadata_group="group1",
        ),
        PeptideMatch(
            peptide_sequence="BBB",
            start_location_on_protein=4,
            end_location_on_protein=7,
            metadata_group="group2",
        ),
    ]
    expected = {"group1": [[peptide_matches[0]]], "group2": [[peptide_matches[1]]]}
    assert distribute_to_rows(peptide_matches) == expected


def test_distribute_to_rows():
    peptide_matches = [
        PeptideMatch("PEPTIDE1", 0, 7, 1.0, "group1"),
        PeptideMatch("PEPTIDE2", 8, 15, 1.0, "group1"),
        PeptideMatch("PEPTIDE3", 16, 23, 1.0, "group1"),
        PeptideMatch("PEPTIDE4", 0, 7, 1.0, "group2"),
        PeptideMatch("PEPTIDE5", 8, 15, 1.0, "group2"),
    ]
    rows = distribute_to_rows(peptide_matches)
    assert len(rows["group1"]) == 1
    assert len(rows["group2"]) == 1


def test_get_max_coverage():
    coverage = {
        "group1": [1, 2, 3, 4, 5],
        "group2": [2, 3, 4, 5, 6],
    }
    max_coverage = get_max_coverage(coverage)
    assert max_coverage == 6


def test_get_max_coverage_empty():
    with pytest.raises(
        ValueError,
        match="Cannot calculate maximum coverage value: No coverage data provided.",
    ):
        get_max_coverage({})
