import pandas as pd
import time
from unittest.mock import patch
import os
import shutil

from protzilla.constants.paths import PROJECT_PATH
from protzilla.data_integration.enrichment_analysis import (
    go_analysis_with_STRING,
    get_functional_enrichment_with_delay,
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


@patch(
    "protzilla.data_integration.enrichment_analysis.get_functional_enrichment_with_delay"
)
def test_go_analysis_with_STRING(mock_enrichment):
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
        folder_name="test_go_analysis_with_STRING",
    )

    os.chdir(current_dir)
    assert not os.path.exists(
        f"{test_data_folder}tmp_enrichment_results"
    ), "tmp_enrichment_results folder was not deleted properly"
    assert current_out["results"][0].equals(results)
    assert current_out["summaries"][0].equals(summary)


@patch(
    "protzilla.data_integration.enrichment_analysis.get_functional_enrichment_with_delay"
)
def test_go_analysis_with_STRING_and_background(mock_enrichment):
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
        background=f"{test_data_folder}/background_imported_proteins.csv",
        run_name=None,
        folder_name="test_go_analysis_with_STRING",
    )

    os.chdir(current_dir)
    assert current_out["results"][0].equals(results)
    assert current_out["summaries"][0].equals(summary)


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
