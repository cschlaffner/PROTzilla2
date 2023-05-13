import pandas as pd
import time
from unittest.mock import patch

from protzilla.data_integration.enrichment_analysis import (
    go_analysis_with_STRING,
    go_analysis_offline,
    go_analysis_with_enrichr,
    get_functional_enrichment_with_delay,
)


def test_go_analysis_with_STRING_proteins_list():
    current_out = go_analysis_with_STRING(
        proteins=["Protein1", "Protein2", "Protein3"],
        protein_set_dbs=["KEGG"],
        organism=9606,
    )
    assert "messages" in current_out
    assert (
        "dataframe with Protein ID and numeric ranking column"
        in current_out["messages"][0]["msg"]
    )


def test_go_analysis_with_STRING_no_fc_df():
    current_out = go_analysis_with_STRING(
        proteins=pd.DataFrame(["Protein1", "Protein2", "Protein3"]),
        protein_set_dbs=["KEGG"],
        organism=9606,
    )
    assert "messages" in current_out
    assert (
        "dataframe with Protein ID and numeric ranking column"
        in current_out["messages"][0]["msg"]
    )


def test_go_analysis_with_STRING_too_many_col_df():
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 18],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample2", "Protein1", "Gene1", 20],
        ["Sample2", "Protein2", "Gene1", 15],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 14],
        ["Sample3", "Protein3", "Gene1", 3],
    )

    test_intensity_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    current_out = go_analysis_with_STRING(
        proteins=test_intensity_df, protein_set_dbs=["KEGG"], organism=9606
    )
    assert "messages" in current_out
    assert (
        "dataframe with Protein ID and numeric ranking column"
        in current_out["messages"][0]["msg"]
    )


def test_go_analysis_offline_no_protein_sets():
    current_out = go_analysis_offline(
        proteins=["Protein1", "Protein2", "Protein3"],
        protein_sets_path="",
        background=None,
    )

    assert "messages" in current_out
    assert "No file uploaded for protein sets" in current_out["messages"][0]["msg"]


def test_go_analysis_offline_invalid_protein_set_file():
    current_out = go_analysis_offline(
        proteins=["Protein1", "Protein2", "Protein3"],
        protein_sets_path="an_invalid_filetype.png",
        background="",  # no background
    )

    assert "messages" in current_out
    assert "Invalid file type" in current_out["messages"][0]["msg"]
    assert "protein sets" in current_out["messages"][0]["msg"]


def test_go_analysis_offline_invalid_background_set_file():
    current_out = go_analysis_offline(
        proteins=["Protein1", "Protein2", "Protein3"],
        protein_sets_path="a_valid_filetype.gmt",
        background="an_invalid_filetype.png",
    )

    assert "messages" in current_out
    assert "Invalid file type" in current_out["messages"][0]["msg"]
    assert "background" in current_out["messages"][0]["msg"]


@patch("restring.restring.get_functional_enrichment")
def test_get_functional_enrichment_with_delay(mock_enrichment):
    last_call_time = None
    MIN_WAIT_TIME = 1

    protein_list = ["Protein1", "Protein2"]
    string_params = {"species": 9606, "caller_ID": "PROTzilla"}
    mock_data = {
        "term ID": ["GO:0005685", "GO:0070062"],
        "term description": ["U1 snRNP", "Extracellular exosome"],
        "observed gene count": [3, 11],
        "background gene count": [21, 2099],
        "false discovery rate": [0.00058, 0.00058],
        "matching proteins in your network (IDs)": [
            "SNRPA,SNRPF,SNRPE",
            "CTSH,NAMPT,HSPB1,APOE,CD81,ITGA1,PGAM2,LRG1,DDAH2,SOD3,C4B",
        ],
        "matching proteins in your network (labels)": [
            "P09012,P62306,P62304",
            "P09668,P43490,P04792,P02649,P60033,P56199,P15259,P02750,O95865,P08294,P0C0L5",
        ],
    }

    mock_df = pd.DataFrame(mock_data)
    mock_enrichment.return_value = mock_df
    result1 = get_functional_enrichment_with_delay(protein_list, **string_params)
    call_time_first = time.time()
    result2 = get_functional_enrichment_with_delay(protein_list, **string_params)
    call_time_second = time.time()

    assert call_time_second - call_time_first >= MIN_WAIT_TIME
    assert result1.equals(result2)
    assert result1.equals(mock_df)
