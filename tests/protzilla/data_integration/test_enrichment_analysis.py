from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from protzilla.constants.paths import PROJECT_PATH
from protzilla.data_integration.enrichment_analysis import (
    go_analysis_with_enrichr,
)


@pytest.fixture
def go_analysis_offline_result_no_bg():
    return {
        "Gene_set": ["gs_ind_0", "gs_ind_0"],
        "Term": ["Set1", "Set2"],
        "Overlap": ["4/8", "4/8"],
        "P-value": [1.000000e00, 1.000000e00],
        "Adjusted P-value": [1.000000e00, 1.000000e00],
        "Odds Ratio": [5.294118e-01, 5.294118e-01],
        "Genes": [
            "Protein3;Protein2;Protein4;Protein1",
            "Protein5;Protein6;Protein3;Protein1",
        ],
    }


@pytest.fixture
def go_analysis_offline_result_with_bg():
    return {
        "Gene_set": ["gs_ind_0", "gs_ind_0"],
        "Term": ["Set1", "Set2"],
        "Overlap": ["4/8", "4/8"],
        "P-value": [7.272727e-01, 7.272727e-01],
        "Adjusted P-value": [7.272727e-01, 7.272727e-01],
        "Odds Ratio": [9.529412e-01, 9.529412e-01],
        "Genes": [
            "Protein3;Protein2;Protein4;Protein1",
            "Protein5;Protein6;Protein3;Protein1",
        ],
    }


def test_go_analysis_with_enrichr_wrong_proteins_input():
    current_out = go_analysis_with_enrichr(
        proteins="Protein1;Protein2;aStringOfProteins",
        protein_sets=["KEGG"],
        organism="human",
    )

    assert "messages" in current_out
    assert "Invalid input" in current_out["messages"][0]["msg"]


@pytest.mark.internet()
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


@pytest.mark.parametrize(
    "protein_sets_path",
    [
        f"{PROJECT_PATH}/tests/test_data/enrichment_data/protein_sets.json",
        f"{PROJECT_PATH}/tests/test_data/enrichment_data/protein_sets.csv",
        f"{PROJECT_PATH}/tests/test_data/enrichment_data/protein_sets.txt"
    ],
)
def test_go_analysis_offline_protein_sets(protein_sets_path, go_analysis_offline_result_no_bg):
    results = pd.DataFrame(go_analysis_offline_result_no_bg)

    current_out = go_analysis_offline(
        proteins=[
            "Protein1",
            "Protein2",
            "Protein3",
            "Protein4",
            "Protein5",
            "Protein6",
        ],
        protein_sets_path=protein_sets_path,
    )
    df = current_out["results"]

    # Convert last column to list of sets because order can change
    df["Genes"] = df["Genes"].apply(lambda x: set(x.split(";")))
    results["Genes"] = results["Genes"].apply(lambda x: set(x.split(";")))
    df["Genes"] = df["Genes"].apply(lambda x: sorted(x))
    results["Genes"] = results["Genes"].apply(lambda x: sorted(x))

    # Convert the "Odds Ratio" column to a numeric type with the desired precision
    df["Odds Ratio"] = df["Odds Ratio"].astype(np.float64)
    results["Odds Ratio"] = results["Odds Ratio"].astype(np.float64)

    # Compare all columns except the "Odds Ratio" column
    df_without_odds = df.drop(columns=["Odds Ratio"])
    results_without_odds = results.drop(columns=["Odds Ratio"])

    # Assert the remaining columns are equal
    assert df_without_odds.equals(results_without_odds)

    # Compare the "Odds Ratio" column separately with a tolerance for numerical equality
    odds_equal = np.isclose(
        df["Odds Ratio"], results["Odds Ratio"], rtol=1e-05, atol=1e-08
    )
    assert odds_equal.all()


@pytest.mark.parametrize(
    "background_path",
    [
        f"{PROJECT_PATH}/tests/test_data/enrichment_data//background_test_proteins.csv",
        f"{PROJECT_PATH}/tests/test_data/enrichment_data//background_test_proteins.txt",
    ],
)
def test_go_analysis_offline_background(background_path, go_analysis_offline_result_with_bg):
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    results = pd.DataFrame(go_analysis_offline_result_with_bg)

    current_out = go_analysis_offline(
        proteins=[
            "Protein1",
            "Protein2",
            "Protein3",
            "Protein4",
            "Protein5",
            "Protein6",
        ],
        protein_sets_path=f"{test_data_folder}/protein_sets.txt",
        background=background_path
    )
    df = current_out["results"]

    # Convert last column to list of sets because order can change
    df["Genes"] = df["Genes"].apply(lambda x: set(x.split(";")))
    results["Genes"] = results["Genes"].apply(lambda x: set(x.split(";")))
    df["Genes"] = df["Genes"].apply(lambda x: sorted(x))
    results["Genes"] = results["Genes"].apply(lambda x: sorted(x))

    column_names = ["Term", "Genes", "Gene_set", "Overlap"]
    # Compare all specified columns
    for column in column_names:
        assert df[column].equals(results[column])

    # Compare the numeric columns separately with a tolerance for numerical equality
    numerical_columns = ["Odds Ratio", "P-value", "Adjusted P-value"]
    for column in numerical_columns:
        numerical_equal = np.isclose(
            df[column], results[column], rtol=1e-05, atol=1e-08
        )
        assert numerical_equal.all()


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
