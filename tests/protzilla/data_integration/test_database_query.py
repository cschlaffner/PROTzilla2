import pandas as pd

from protzilla.data_integration.database_query import (
    uniprot_groups_to_genes,
    uniprot_to_genes,
)
from unittest.mock import patch


@patch("protzilla.data_integration.database_query.uniprot_to_genes")
def test_uniprot_groups_to_genes(mock):
    mock.return_value = dict(a="ABS", b="HKL", c="NNF"), ["d"]
    print(uniprot_groups_to_genes(["a;b;c", "a-1;b-1_4", "c;d", "d-4"]))


@patch("protzilla.data_integration.database_query.uniprot_databases")
@patch("protzilla.data_integration.database_query.biomart_query")
def test_uniprot_to_genes_biomart(mock_biomart, mock_databases):
    mock_databases.return_value = []
    mock_biomart.return_value = [["a", "ABS"], ["b", "HKL"], ["c", "NNF"]]
    print(uniprot_to_genes(list("abcd")))


@patch("protzilla.data_integration.database_query.uniprot_query_dataframe")
@patch("protzilla.data_integration.database_query.uniprot_columns")
@patch("protzilla.data_integration.database_query.uniprot_databases")
@patch("protzilla.data_integration.database_query.biomart_query")
def test_uniprot_to_genes_database(
    mock_biomart, mock_databases, mock_columns, mock_query
):
    mock_query.return_value = pd.DataFrame(
        {"Gene Names": ["ABS", "HKL", "NNF"]}, index=["a", "b", "c"]
    )
    mock_columns.return_value = ["Gene Names"]
    mock_databases.return_value = ["hi"]
    mock_biomart.return_value = []
    print(uniprot_to_genes(list("abcd")))


@patch("protzilla.data_integration.database_query.uniprot_query_dataframe")
@patch("protzilla.data_integration.database_query.uniprot_columns")
@patch("protzilla.data_integration.database_query.uniprot_databases")
@patch("protzilla.data_integration.database_query.biomart_query")
def test_uniprot_to_genes_both(mock_biomart, mock_databases, mock_columns, mock_query):
    mock_query.return_value = pd.DataFrame(
        {"Gene Names": ["ABS", "HKL"]}, index=["a", "b"]
    )
    mock_columns.return_value = ["Gene Names"]
    mock_databases.return_value = ["hi"]
    mock_biomart.return_value = [["c", "NNF"]]
    print(uniprot_to_genes(list("abcd")))
