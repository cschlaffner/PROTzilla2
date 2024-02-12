from unittest.mock import patch

import pandas as pd

from protzilla.data_integration.database_query import (
    uniprot_groups_to_genes,
    uniprot_to_genes,
)


@patch("protzilla.data_integration.database_query.uniprot_to_genes")
def test_uniprot_groups_to_genes(mock_uniprot_to_genes):
    mock_uniprot_to_genes.return_value = dict(a="ABS", b="HKL", c="NNF"), ["d"]
    gene_to_protein_groups, protein_group_to_genes, filtered = uniprot_groups_to_genes(
        ["a;b;c", "a-1;b-1_4", "c;d", "d-4;d-8"], ["db_name"], use_biomart=False
    )
    assert filtered == ["d-4;d-8"]
    expected_gene_map = {
        "ABS": ["a;b;c", "a-1;b-1_4"],
        "HKL": ["a;b;c", "a-1;b-1_4"],
        "NNF": ["a;b;c", "c;d"],
    }
    assert set(gene_to_protein_groups.keys()) == set(expected_gene_map.keys())
    for key in gene_to_protein_groups:
        assert set(gene_to_protein_groups[key]) == set(expected_gene_map[key])

    expected_group_map = {
        "a-1;b-1_4": ["ABS", "HKL"],
        "a;b;c": ["ABS", "NNF", "HKL"],
        "c;d": ["NNF"],
    }
    assert set(protein_group_to_genes.keys()) == set(expected_group_map.keys())
    for key in protein_group_to_genes:
        assert set(protein_group_to_genes[key]) == set(expected_group_map[key])


@patch("protzilla.data_integration.database_query.biomart_query")
def test_uniprot_to_genes_biomart(mock_biomart):
    # no databases found, only biomart will be used to map
    mock_biomart.return_value = [["a", "ABS"], ["b", "HKL"], ["c", "NNF"]]
    mapping, not_found = uniprot_to_genes(list("abcd"), [], use_biomart=True)
    assert mapping == dict(a="ABS", b="HKL", c="NNF")
    assert not_found == ["d"]


@patch("protzilla.data_integration.database_query.uniprot_query_dataframe")
@patch("protzilla.data_integration.database_query.uniprot_columns")
@patch("protzilla.data_integration.database_query.biomart_query")
def test_uniprot_to_genes_database(mock_biomart, mock_columns, mock_query):
    # database found, biomart will not find anything
    mock_query.return_value = pd.DataFrame(
        {"Gene Names": ["ABS", "HKL GST", "NNF"]}, index=["a", "b", "c"]
    )
    mock_columns.return_value = ["Gene Names"]
    mock_biomart.return_value = []
    mapping, not_found = uniprot_to_genes(list("abcd"), ["db_name"], use_biomart=False)
    assert mapping == dict(a="ABS", b="HKL", c="NNF")
    assert not_found == ["d"]


@patch("protzilla.data_integration.database_query.uniprot_query_dataframe")
@patch("protzilla.data_integration.database_query.uniprot_columns")
@patch("protzilla.data_integration.database_query.biomart_query")
def test_uniprot_to_genes_both(mock_biomart, mock_columns, mock_query):
    # both database and biomart used for mapping
    mock_query.return_value = pd.DataFrame(
        {"Gene Names": ["ABS", "HKL GST"]}, index=["a", "b"]
    )
    mock_columns.return_value = ["Gene Names"]
    mock_biomart.return_value = [["c", "NNF"]]
    mapping, not_found = uniprot_to_genes(list("abcd"), ["db_name"], use_biomart=True)
    assert mapping == dict(a="ABS", b="HKL", c="NNF")
    assert not_found == ["d"]
