import os
import shutil
import time
import requests
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from protzilla.constants.paths import PROJECT_PATH
from protzilla.data_integration.enrichment_analysis import (
    get_functional_enrichment_with_delay,
    go_analysis_offline,
    go_analysis_with_enrichr,
    go_analysis_with_STRING,
    merge_restring_dfs,
    merge_up_down_regulated_proteins_results,
)


@patch("restring.restring.get_functional_enrichment")
def test_get_functional_enrichment_with_delay(mock_enrichment):
    last_call_time = None
    MIN_WAIT_TIME = 1

    protein_list = [
        "P09012,P62306,P62304",
        "P09668,P43490,P04792,P02649,P60033,P56199,P15259,P02750,O95865,P08294,P0C0L5",
    ]
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


def test_merge_restring_dfs():
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    KEGG_result = pd.read_csv(
        f"{test_data_folder}/KEGG_results.csv", header=0, index_col=0
    )
    KEGG_summary = pd.read_csv(
        f"{test_data_folder}/KEGG_summary.csv", header=0, index_col=0
    )
    Process_result = pd.read_csv(
        f"{test_data_folder}/Process_results.csv", header=0, index_col=0
    )
    Process_summary = pd.read_csv(
        f"{test_data_folder}/Process_summary.csv", header=0, index_col=0
    )
    merged_results = pd.read_csv(f"{test_data_folder}/merged_results.csv", header=0)
    merged_summaries = pd.read_csv(f"{test_data_folder}/merged_summaries.csv", header=0)

    result = merge_restring_dfs(dict(KEGG=KEGG_result, Process=Process_result))
    summary = merge_restring_dfs(dict(KEGG=KEGG_summary, Process=Process_summary))

    column_names = ["term", "common", "Gene_set"]
    for column in column_names:
        assert result[column].equals(merged_results[column])

    numerical_equal = np.isclose(
        result["enrichment_details"],
        merged_results["enrichment_details"],
        rtol=1e-05,
        atol=1e-08,
    )
    assert numerical_equal.all()
    assert summary.equals(merged_summaries)


@patch(
    "protzilla.data_integration.enrichment_analysis.get_functional_enrichment_with_delay"
)
@pytest.mark.parametrize(
    "background",
    [
        None,
        f"{PROJECT_PATH}/tests/test_data/enrichment_data/background_imported_proteins.csv",
    ],
)
def test_go_analysis_with_STRING(mock_enrichment, background):
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    proteins_df = pd.read_csv(
        f"{test_data_folder}/input-t_test-log2_fold_change_df.csv"
    )

    up_path = f"{test_data_folder}/UP_enrichment.KEGG.tsv"
    up_df = pd.read_csv(up_path, header=0, sep="\t")
    down_path = f"{test_data_folder}/DOWN_enrichment.KEGG.tsv"
    down_df = pd.read_csv(down_path, header=0, sep="\t")

    results = pd.read_csv(f"{test_data_folder}/KEGG_results.csv", header=0, index_col=0)
    summary = pd.read_csv(f"{test_data_folder}/KEGG_summary.csv", header=0, index_col=0)
    mock_enrichment.side_effect = [up_df, down_df]

    # copy files to test aggregation
    test_folder = f"{test_data_folder}/tmp_enrichment_results/test_go_analysis_with_STRING/enrichment_details/"
    os.makedirs(test_folder, exist_ok=True)
    shutil.copy(up_path, test_folder)
    shutil.copy(down_path, test_folder)
    current_dir = os.getcwd()
    os.chdir(test_data_folder)

    current_out = go_analysis_with_STRING(
        proteins=proteins_df,
        protein_set_dbs=["KEGG"],
        organism=9606,
        direction="both",
        run_name=None,
        background=background,
        folder_name="test_go_analysis_with_STRING",
    )

    os.chdir(current_dir)
    assert not os.path.exists(
        f"{test_data_folder}tmp_enrichment_results"
    ), "tmp_enrichment_results folder was not deleted properly"
    assert current_out["result"].equals(results)
    assert current_out["summary"].equals(summary)


@patch(
    "protzilla.data_integration.enrichment_analysis.get_functional_enrichment_with_delay"
)
def test_go_analysis_with_STRING_one_direction_missing(mock_enrichment):
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    proteins_df = pd.read_csv(
        f"{test_data_folder}/input-t_test-log2_fold_change_df.csv"
    )
    up_proteins_df = proteins_df[proteins_df["log2_fold_change"] > 0]
    down_proteins_df = proteins_df[proteins_df["log2_fold_change"] < 0]

    up_path = f"{test_data_folder}/UP_enrichment.KEGG.tsv"
    up_df = pd.read_csv(up_path, header=0, sep="\t")
    down_path = f"{test_data_folder}/DOWN_enrichment.KEGG.tsv"
    down_df = pd.read_csv(down_path, header=0, sep="\t")
    mock_enrichment.side_effect = [up_df, down_df]

    # copy files to test aggregation
    test_folder = f"{test_data_folder}/tmp_enrichment_results/test_go_analysis_with_STRING/enrichment_details/"
    os.makedirs(test_folder, exist_ok=True)
    shutil.copy(up_path, test_folder)
    current_dir = os.getcwd()
    os.chdir(test_data_folder)

    current_out = go_analysis_with_STRING(
        proteins=up_proteins_df,
        protein_set_dbs=["KEGG"],
        organism=9606,
        direction="both",
        run_name=None,
        folder_name="test_go_analysis_with_STRING",
    )

    os.chdir(current_dir)
    assert "messages" in current_out
    assert "No downregulated proteins" in current_out["messages"][0]["msg"]

    os.makedirs(test_folder, exist_ok=True)
    shutil.copy(down_path, test_folder)
    current_dir = os.getcwd()
    os.chdir(test_data_folder)

    current_out = go_analysis_with_STRING(
        proteins=down_proteins_df,
        protein_set_dbs=["KEGG"],
        organism=9606,
        direction="both",
        run_name=None,
        folder_name="test_go_analysis_with_STRING",
    )

    os.chdir(current_dir)
    assert "messages" in current_out
    assert "No upregulated proteins" in current_out["messages"][0]["msg"]


def test_go_analysis_with_STRING_no_upregulated_proteins():
    proteins_df = pd.DataFrame(
        {
            "Protein ID": ["Protein1", "Protein2", "Protein3"],
            "log2_fold_change": [-1.0, -0.5, -0.0],
        }
    )

    current_out = go_analysis_with_STRING(
        proteins=proteins_df,
        protein_set_dbs=["KEGG"],
        organism=9606,
        direction="up",
    )

    assert "messages" in current_out
    assert "No upregulated proteins" in current_out["messages"][0]["msg"]


def test_go_analysis_with_STRING_no_downregulated_proteins():
    proteins_df = pd.DataFrame(
        {
            "Protein ID": ["Protein1", "Protein2", "Protein3"],
            "log2_fold_change": [1.0, 0.5, 0.0],
        }
    )

    current_out = go_analysis_with_STRING(
        proteins=proteins_df,
        protein_set_dbs=["KEGG"],
        organism=9606,
        direction="down",
    )

    assert "messages" in current_out
    assert "No downregulated proteins" in current_out["messages"][0]["msg"]


def test_go_analysis_with_STRING_no_proteins():
    proteins_df = pd.DataFrame(
        {
            "Protein ID": [],
            "log2_fold_change": [],
        }
    )

    current_out = go_analysis_with_STRING(
        proteins=proteins_df,
        protein_set_dbs=["KEGG"],
        organism=9606,
        direction="both",
    )

    print(current_out)
    assert "messages" in current_out
    assert "No proteins" in current_out["messages"][0]["msg"]


def test_go_analysis_with_STRING_proteins_list():
    current_out = go_analysis_with_STRING(
        proteins=["Protein1", "Protein2", "Protein3"],
        protein_set_dbs=["KEGG"],
        organism=9606,
    )
    assert "messages" in current_out
    assert (
        "dataframe with Protein ID and direction of expression change column"
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
        "dataframe with Protein ID and direction of expression change column"
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
        "dataframe with Protein ID and direction of expression change column"
        in current_out["messages"][0]["msg"]
    )


def test_go_analysis_with_enrichr_wrong_proteins_input():
    current_out = go_analysis_with_enrichr(
        proteins="Protein1;Protein2;aStringOfProteins",
        protein_sets=["KEGG"],
        organism="human",
    )

    assert "messages" in current_out
    assert (
        "dataframe with Protein ID and direction of expression change column"
        in current_out["messages"][0]["msg"]
    )


@pytest.mark.internet()
@patch(
    "protzilla.data_integration.enrichment_analysis.uniprot_ids_to_uppercase_gene_symbols"
)
def test_go_analysis_with_enrichr(mock_gene_mapping):
    # Check if enrichr API is available
    api_url = "https://maayanlab.cloud/Enrichr/addList"
    try:
        response = requests.get(api_url)
        if response.status_code != 200:
            pytest.skip("Enrichr API is currently unavailable")
    except requests.exceptions.RequestException:
        pytest.skip("Enrichr API is currently unavailable")

    proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
        "Protein4",
        "Protein5",
        "Protein6;Protein7;Protein8",
        "Protein9;Protein10;Protein11",
        "Protein12;Protein13",
    ]
    proteins_df = pd.DataFrame({"Protein ID": proteins, "fold_change": [1.0] * 8})
    protein_sets = ["Reactome_2013"]
    organism = "human"
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    results = pd.read_csv(
        f"{test_data_folder}/Reactome_enrichment_enrichr.csv", sep="\t"
    )

    mock_gene_mapping.return_value = {
        "ENO1": "Protein1",
        "ENO2": "Protein2",
        "ENO3": "Protein3",
        "HK2": "Protein4",
        "HK1": "Protein6",
        "HK3": "Protein7",
        "IDH3B": "Protein8",
        "ATP6V1G2": "Protein9",
        "GPT2": "Protein10",
        "SDHB": "Protein11",
        "COX6B1": "Protein12;Protein13",
    }, ["Protein5"]
    current_out = go_analysis_with_enrichr(proteins_df, protein_sets, organism, "up")
    df = current_out["results"]

    column_names = ["Term", "Genes", "Gene_set", "Overlap", "Proteins"]
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


@pytest.mark.parametrize(
    "protein_sets_path",
    [
        f"{PROJECT_PATH}/tests/test_data/enrichment_data/protein_sets.json",
        f"{PROJECT_PATH}/tests/test_data/enrichment_data/protein_sets.csv",
        f"{PROJECT_PATH}/tests/test_data/enrichment_data/protein_sets.txt",
    ],
)
def test_go_analysis_offline_protein_sets(
    protein_sets_path, go_analysis_offline_result_no_bg
):
    results = pd.DataFrame(go_analysis_offline_result_no_bg)
    proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
        "Protein4",
        "Protein5",
        "Protein6",
    ]
    proteins_df = pd.DataFrame({"Protein ID": proteins, "fold_change": [1.0] * 6})

    current_out = go_analysis_offline(
        proteins=proteins_df,
        protein_sets_path=protein_sets_path,
        direction="up",
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
def test_go_analysis_offline_background(
    background_path, go_analysis_offline_result_with_bg
):
    test_data_folder = f"{PROJECT_PATH}/tests/test_data/enrichment_data"
    results = pd.DataFrame(go_analysis_offline_result_with_bg)
    proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
        "Protein4",
        "Protein5",
        "Protein6",
    ]
    proteins_df = pd.DataFrame({"Protein ID": proteins, "fold_change": [-1.0] * 6})

    current_out = go_analysis_offline(
        proteins=proteins_df,
        protein_sets_path=f"{test_data_folder}/protein_sets.txt",
        background=background_path,
        direction="down",
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
    proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
    ]
    proteins_df = pd.DataFrame({"Protein ID": proteins, "fold_change": [1.0] * 3})
    current_out = go_analysis_offline(
        proteins=proteins_df, protein_sets_path="", background=None, direction="up"
    )

    assert "messages" in current_out
    assert "No file uploaded for protein sets" in current_out["messages"][0]["msg"]


def test_go_analysis_offline_invalid_protein_set_file():
    proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
    ]
    proteins_df = pd.DataFrame({"Protein ID": proteins, "fold_change": [1.0] * 3})
    current_out = go_analysis_offline(
        proteins=proteins_df,
        protein_sets_path="an_invalid_filetype.png",
        background="",  # no background
        direction="up",
    )

    assert "messages" in current_out
    assert "Invalid file type" in current_out["messages"][0]["msg"]
    assert "protein sets" in current_out["messages"][0]["msg"]


def test_go_analysis_offline_invalid_background_set_file():
    proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
    ]
    proteins_df = pd.DataFrame({"Protein ID": proteins, "fold_change": [1.0] * 3})
    current_out = go_analysis_offline(
        proteins=proteins_df,
        protein_sets_path="a_valid_filetype.gmt",
        background="an_invalid_filetype.png",
        direction="up",
    )

    assert "messages" in current_out
    assert "Invalid file type" in current_out["messages"][0]["msg"]
    assert "background" in current_out["messages"][0]["msg"]


def test_merge_up_down_regulated_proteins_results():
    up_enriched = pd.DataFrame(
        {
            "Gene_set": ["Set1", "Set2", "Set4"],
            "Term": ["Term1", "Term2", "Term4"],
            "Adjusted P-value": [0.01, 0.05, 0.001],
            "Proteins": ["Protein1", "Protein2", "Protein4;Protein5"],
            "Genes": ["Gene1", "Gene2", "Gene4;GeneX"],
            "Overlap": ["1/10", "1/30", "2/40"],
        }
    )

    down_enriched = pd.DataFrame(
        {
            "Gene_set": ["Set2", "Set3", "Set4"],
            "Term": ["Term2", "Term3", "Term4"],
            "Adjusted P-value": [0.02, 0.03, 0.0001],
            "Proteins": ["Protein3", "Protein4", "Protein3"],
            "Genes": ["GeneX", "Gene4", "GeneX"],
            "Overlap": ["1/30", "1/40", "1/40"],
        }
    )

    expected_output = pd.DataFrame(
        {
            "Gene_set": ["Set1", "Set2", "Set3", "Set4"],
            "Term": ["Term1", "Term2", "Term3", "Term4"],
            "Adjusted P-value": [0.01, 0.02, 0.03, 0.0001],
            "Proteins": [
                "Protein1",
                "Protein2;Protein3",
                "Protein4",
                "Protein3;Protein4;Protein5",
            ],
            "Genes": ["Gene1", "Gene2;GeneX", "Gene4", "Gene4;GeneX"],
            "Overlap": ["1/10", "2/30", "1/40", "2/40"],
        }
    )

    merged = merge_up_down_regulated_proteins_results(
        up_enriched, down_enriched, mapped=True
    )
    merged.set_index(["Gene_set", "Term"], inplace=True)
    expected_output.set_index(["Gene_set", "Term"], inplace=True)
    merged = merged.sort_index()
    expected_output = expected_output.sort_index()

    for col in ["Genes", "Proteins"]:
        merged[col] = merged[col].apply(lambda x: set(x.split(";")))
        expected_output[col] = expected_output[col].apply(lambda x: set(x.split(";")))
        merged[col] = merged[col].apply(lambda x: sorted(x))
        expected_output[col] = expected_output[col].apply(lambda x: sorted(x))

    pd.testing.assert_frame_equal(merged, expected_output)
