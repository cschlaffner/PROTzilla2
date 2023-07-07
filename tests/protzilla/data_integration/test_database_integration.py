from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from protzilla.data_integration.database_integration import add_uniprot_data


@pytest.fixture
def p_value_df():
    return pd.DataFrame(
        {
            "Protein ID": ["P10636", "A234;BBB", "not_found"],
            "p_val": [0.01, 0.4, np.nan],
        }
    )


@patch("protzilla.data_integration.database_query.uniprot_query_dataframe")
def test_add_uniprot_data(mock_uniprot_query_dataframe, p_value_df):
    mock_uniprot_query_dataframe.return_value = pd.DataFrame(
        {"Gene": ["MAPT", "ZXY", "M99"]}, index=["P10636", "A234", "BBB"]
    )
    expected_df = pd.DataFrame(
        {
            "Protein ID": ["P10636", "A234;BBB", "not_found"],
            "p_val": [0.01, 0.4, np.nan],
            "Gene": ["MAPT", "ZXY;M99", None],
        }
    )
    assert expected_df.equals(
        add_uniprot_data(p_value_df, "dummy", "Gene")["results_df"]
    )


@patch("protzilla.data_integration.database_query.uniprot_query_dataframe")
def test_add_uniprot_links(mock_uniprot_query_dataframe, p_value_df):
    links = add_uniprot_data(p_value_df, "dummy", ["Links"])["results_df"]["Links"]
    assert all(all(x.startswith("https://") for x in link.split()) for link in links)
    assert not mock_uniprot_query_dataframe.called


@patch("protzilla.data_integration.database_query.uniprot_query_dataframe")
def test_add_uniprot_no_fileds(mock_uniprot_query_dataframe, p_value_df):
    output = add_uniprot_data(p_value_df, "dummy", [])
    assert p_value_df.equals(output["results_df"])
    assert not mock_uniprot_query_dataframe.called
    assert "messages" in output
    assert "No fields" in output["messages"][0]["msg"]
