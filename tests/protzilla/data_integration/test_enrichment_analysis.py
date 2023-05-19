import pandas as pd
import numpy as np
from unittest.mock import patch

from protzilla.constants.paths import PROJECT_PATH
from protzilla.data_integration.enrichment_analysis import (
    go_analysis_with_enrichr,
)

def test_go_analysis_with_enrichr_wrong_proteins_input():
    current_out = go_analysis_with_enrichr(
        proteins="Protein1;Protein2;aStringOfProteins",
        protein_sets=["KEGG"],
        organism="human",
    )

    assert "messages" in current_out
    assert "Invalid input" in current_out["messages"][0]["msg"]


@patch(
    "protzilla.data_integration.enrichment_analysis.uniprot_ids_to_uppercase_gene_symbols"
)
def test_go_analysis_with_enrichr(mock_gene_symbols):
    proteins = ["Protein1", "Protein2", "Protein3", "Protein4", "Protein5", "Protein6"]
    protein_sets = ["Reactome_2013"]
    organism = "human"
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    results = pd.read_csv(f"{test_data_folder}/Reactome_enrichment_enrichr.csv")

    mock_gene_symbols.return_value = [
        "ENO1",
        "ENO2",
        "ENO3",
        "HK2",
        "HK1",
        "HK3",
        "IDH3B",
        "ATP6V1G2",
        "GPT2",
        "SDHB",
        "COX6B1",
    ], ["Protein5"]
    current_out = go_analysis_with_enrichr(proteins, protein_sets, organism)
    df = current_out["results"]

    column_names = ["Term", "Genes", "Gene_set", "Overlap"]
    # Compare all specified columns
    for column in column_names:
        assert df[column].equals(results[column])

    # Compare the numeric columns separately with a tolerance for numerical equality
    numerical_columns = [
        "Odds Ratio",
        "P-value",
        "Adjusted P-value",
        "Old P-value",
        "Old Adjusted P-value",
        "Combined Score",
    ]
    for column in numerical_columns:
        numerical_equal = np.isclose(
            df[column], results[column], rtol=1e-05, atol=1e-08
        )
        assert numerical_equal.all()

    assert "messages" in current_out
    assert "Some proteins could not be mapped" in current_out["messages"][0]["msg"]
