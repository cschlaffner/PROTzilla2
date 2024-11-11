from unittest.mock import patch

import pandas as pd

from protzilla.data_integration.database_query import (
    uniprot_groups_to_genes,
    uniprot_to_genes,
)


@patch("protzilla.data_integration.database_query.uniprot_to_genes")
def test_uniprot_groups_to_genes(mock_uniprot_to_genes):
    mock_uniprot_to_genes.return_value = dict(a="ABS", b="HKL", c="NNF"), ["d"]
    gene_mapping_df, filtered = uniprot_groups_to_genes(
        ["a;b;c", "a-1;b-1_4", "c;d", "d-4;d-8"], ["db_name"], use_biomart=False
    ).values()
    assert set(filtered) == {"d-4;d-8"}
    assert gene_mapping_df["Protein ID"].to_dict() == {
        0: "a;b;c",
        1: "a;b;c",
        2: "a;b;c",
        3: "a-1;b-1_4",
        4: "a-1;b-1_4",
        5: "c;d",
    }
    assert set(gene_mapping_df["Gene"].to_list()) == {
        "ABS",
        "NNF",
        "HKL",
        "ABS",
        "HKL",
        "NNF",
    }
    assert set(gene_mapping_df["Protein ID"].to_list()) == {"a;b;c", "a-1;b-1_4", "c;d"}


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
