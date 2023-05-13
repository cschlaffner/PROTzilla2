import pandas as pd
import pytest

from protzilla.data_integration.enrichment_analysis import go_analysis_with_STRING, go_analysis_offline, go_analysis_with_enrichr

def test_go_analysis_with_STRING_proteins_list():
    current_out = go_analysis_with_STRING(
        proteins=["Protein1", "Protein2", "Protein3"],
        protein_set_dbs=["KEGG"],
        organism=9606
    )
    assert "messages" in current_out
    assert "dataframe with Protein ID and numeric ranking column" in current_out["messages"][0]["msg"]

def test_go_analysis_with_STRING_no_fc_df():
    current_out = go_analysis_with_STRING(
        proteins=pd.DataFrame(["Protein1", "Protein2", "Protein3"]),
        protein_set_dbs=["KEGG"],
        organism=9606
    )
    assert "messages" in current_out
    assert "dataframe with Protein ID and numeric ranking column" in current_out["messages"][0]["msg"]

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
        ["Sample3", "Protein3", "Gene1", 3]
    )

    test_intensity_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    current_out = go_analysis_with_STRING(
        proteins=test_intensity_df,
        protein_set_dbs=["KEGG"],
        organism=9606
    )
    assert "messages" in current_out
    assert "dataframe with Protein ID and numeric ranking column" in current_out["messages"][0]["msg"]