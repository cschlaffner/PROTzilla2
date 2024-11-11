from unittest.mock import patch

import time
import pandas as pd
import numpy as np
import pytest
import requests

from protzilla.constants.paths import PROJECT_PATH

# order is important to ensure correctness of patched functions
# isort:skip_file
from protzilla.data_integration.enrichment_analysis_helper import (
    read_protein_or_gene_sets_file,
    read_background_file,
)
from protzilla.data_integration.enrichment_analysis import (
    get_functional_enrichment_with_delay,
    GO_analysis_offline,
    GO_analysis_with_Enrichr,
    GO_analysis_with_STRING,
    merge_up_down_regulated_dfs_restring,
    merge_up_down_regulated_dfs_gseapy,
)
from protzilla.data_integration.enrichment_analysis_gsea import (
    create_genes_intensity_wide_df,
    gsea,
    gsea_preranked,
    create_ranked_df,
)

# isort:end_skip_file


@pytest.fixture
def data_folder_tests():
    return PROJECT_PATH / "tests/test_data/enrichment_data"


@patch("restring.restring.get_functional_enrichment")
def test_get_functional_enrichment_with_delay(mock_enrichment):
    MIN_WAIT_TIME = 1

    protein_list = [
        "P09972",
        "P04406",
        "P21796",
        "P10515",
        "P23368",
        "P07195",
        "P02746",
        "P02747",
        "P02745",
        "P06132",
        "P00450",
        "P07814",
        "P13716",
    ]
    string_params = {"species": 9606}
    mock_data = {
        "category": ["Process", "Process", "KEGG"],
        "term": ["GO:0006090", "GO:0098883", "hsa00860"],
        "number_of_genes": [6, 3, 4],
        "number_of_genes_in_background": [69, 8, 41],
        "ncbiTaxonId": [9606, 9606, 9606],
        "inputGenes": [
            "P09972,P04406,P21796,P10515,P23368,P07195",
            "P02746,P02747,P02745",
            "P06132,P00450,P07814,P13716",
        ],
        "preferredNames": [
            "ALDOC,GAPDH,VDAC1,DLAT,ME2,LDHB",
            "C1QB,C1QC,C1QA",
            "UROD,CP,EPRS,ALAD",
        ],
        "p_value": [1.38e-05, 5.21e-05, 0.00027],
        "fdr": [0.0024, 0.0073, 0.0056],
        "description": [
            "Pyruvate metabolic process",
            "Synapse pruning",
            "Porphyrin and chlorophyll metabolism",
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


def test_merge_up_down_regulated_dfs_restring():
    # columns are simplified for testing purposes
    # left out columns just get copied over like fdr is here
    up_df = pd.DataFrame(
        {
            "category": ["cat1", "cat2"],
            "term": ["term1", "term2"],
            "p_value": [0.1, 0.2],
            "fdr": [0.5, 0.6],
            "inputGenes": ["protein1,protein2", "protein3"],
            "preferredNames": ["gene1,gene2", "gene3"],
            "number_of_genes": [2, 1],
            "number_of_genes_in_background": [20, 100],
            "ncbiTaxonId": [9606, 9606],
        }
    )

    down_df = pd.DataFrame(
        {
            "category": ["cat1", "cat3"],
            "term": ["term1", "term3"],
            "p_value": [0.05, 0.3],
            "fdr": [0.4, 0.7],
            "inputGenes": ["protein2,protein4", "protein5"],
            "preferredNames": ["gene2,gene4", "gene5"],
            "number_of_genes": [2, 1],
            "number_of_genes_in_background": [20, 50],
            "ncbiTaxonId": [9606, 9606],
        }
    )

    expected_output = pd.DataFrame(
        {
            "category": ["cat1", "cat2", "cat3"],
            "term": ["term1", "term2", "term3"],
            "p_value": [0.1, 0.2, 0.3],
            "fdr": [0.5, 0.6, 0.7],
            "inputGenes": ["protein2,protein4,protein1", "protein3", "protein5"],
            "preferredNames": ["gene2,gene4,gene1", "gene3", "gene5"],
            "number_of_genes": [3, 1, 1],
            "number_of_genes_in_background": [20, 100, 50],
            "ncbiTaxonId": [9606, 9606, 9606],
        }
    )

    merged = merge_up_down_regulated_dfs_restring(up_df, down_df)
    merged.set_index(["category", "term"], inplace=True)
    expected_output.set_index(["category", "term"], inplace=True)
    merged = merged.sort_index()
    expected_output = expected_output.sort_index()

    columns = ["inputGenes", "preferredNames"]
    for col in columns:
        merged[col] = merged[col].apply(lambda x: set(x.split(",")))
        expected_output[col] = expected_output[col].apply(lambda x: set(x.split(",")))
        merged[col] = merged[col].apply(lambda x: sorted(x))
        expected_output[col] = expected_output[col].apply(lambda x: sorted(x))

    pd.testing.assert_frame_equal(merged, expected_output, check_dtype=False)


@patch(
    "protzilla.data_integration.enrichment_analysis.get_functional_enrichment_with_delay"
)
@pytest.mark.parametrize(
    "background",
    [
        None,
        PROJECT_PATH
        / "tests/test_data/enrichment_data/background_imported_proteins.csv",
    ],
)
def test_GO_analysis_with_STRING(mock_enrichment, background, data_folder_tests):
    proteins_df = pd.read_csv(
        data_folder_tests / "input-t_test-log2_fold_change_df.csv"
    )

    up_df = pd.read_csv(
        data_folder_tests / "up_enrichment_KEGG_Process.csv", header=0, index_col=0
    )
    down_df = pd.read_csv(
        data_folder_tests / "down_enrichment_KEGG_Process.csv", header=0, index_col=0
    )

    results = pd.read_csv(data_folder_tests / "merged_KEGG_process.csv", header=0)
    mock_enrichment.side_effect = [up_df, down_df]

    out_df = GO_analysis_with_STRING(
        proteins_df=proteins_df,
        gene_sets_restring=["KEGG", "Process"],
        organism=9606,
        differential_expression_col="log2_fold_change",
        background_path=background,
        direction="both",
    )["enrichment_df"]

    for col in ["inputGenes", "preferredNames"]:
        out_df[col] = out_df[col].apply(lambda x: set(x.split(",")))
        results[col] = results[col].apply(lambda x: set(x.split(",")))
        out_df[col] = out_df[col].apply(lambda x: sorted(x))
        results[col] = results[col].apply(lambda x: sorted(x))

    pd.testing.assert_frame_equal(results, out_df, check_dtype=False)


@patch(
    "protzilla.data_integration.enrichment_analysis.get_functional_enrichment_with_delay"
)
def test_GO_analysis_with_STRING_one_direction_missing(
    mock_enrichment, data_folder_tests
):
    proteins_df = pd.read_csv(
        data_folder_tests / "input-t_test-log2_fold_change_df.csv"
    )
    up_proteins_df = proteins_df[proteins_df["log2_fold_change"] > 0]
    down_proteins_df = proteins_df[proteins_df["log2_fold_change"] < 0]

    up_df = pd.read_csv(data_folder_tests / "up_enrichment_KEGG_Process.csv", header=0)
    down_df = pd.read_csv(
        data_folder_tests / "down_enrichment_KEGG_Process.csv", header=0
    )
    mock_enrichment.side_effect = [up_df, down_df]

    current_out = GO_analysis_with_STRING(
        proteins_df=up_proteins_df,
        gene_sets_restring=["KEGG", "Process"],
        organism=9606,
        differential_expression_col="log2_fold_change",
        direction="both",
    )
    assert "messages" in current_out
    assert "No downregulated proteins" in current_out["messages"][0]["msg"]

    current_out = GO_analysis_with_STRING(
        proteins_df=down_proteins_df,
        gene_sets_restring=["KEGG", "Process"],
        organism=9606,
        differential_expression_col="log2_fold_change",
        direction="both",
    )

    assert "messages" in current_out
    assert "No upregulated proteins" in current_out["messages"][0]["msg"]


def test_GO_analysis_with_STRING_no_upregulated_proteins():
    proteins_df = pd.DataFrame(
        {
            "Protein ID": ["Protein1", "Protein2", "Protein3"],
            "log2_fold_change": [-1.0, -0.5, -0.0],
        }
    )

    current_out = GO_analysis_with_STRING(
        proteins_df=proteins_df,
        gene_sets_restring=["KEGG"],
        organism=9606,
        differential_expression_col="log2_fold_change",
        direction="up",
    )

    assert "messages" in current_out
    assert "No upregulated proteins" in current_out["messages"][0]["msg"]


def test_GO_analysis_with_STRING_no_downregulated_proteins():
    proteins_df = pd.DataFrame(
        {
            "Protein ID": ["Protein1", "Protein2", "Protein3"],
            "log2_fold_change": [1.0, 0.5, 0.0],
        }
    )

    current_out = GO_analysis_with_STRING(
        proteins_df=proteins_df,
        gene_sets_restring=["KEGG"],
        organism=9606,
        differential_expression_col="log2_fold_change",
        direction="down",
    )

    assert "messages" in current_out
    assert "No downregulated proteins" in current_out["messages"][0]["msg"]


def test_GO_analysis_with_STRING_no_knowledge_base():
    proteins_df = pd.DataFrame(
        {
            "Protein ID": ["Protein1", "Protein2", "Protein3"],
            "log2_fold_change": [1.0, 0.5, 0.0],
        }
    )

    current_out = GO_analysis_with_STRING(
        proteins_df=proteins_df,
        gene_sets_restring=None,
        organism=9606,
        differential_expression_col="log2_fold_change",
        direction="both",
    )

    assert "messages" in current_out
    assert any(
        "No knowledge databases" in message["msg"]
        for message in current_out["messages"]
    )


def test_GO_analysis_with_STRING_no_proteins():
    proteins_df = pd.DataFrame(
        {
            "Protein ID": [],
            "log2_fold_change": [],
        }
    )

    current_out = GO_analysis_with_STRING(
        proteins_df=proteins_df,
        gene_sets_restring=["KEGG"],
        organism=9606,
        differential_expression_col="log2_fold_change",
        direction="both",
    )

    assert "messages" in current_out
    assert "No proteins" in current_out["messages"][0]["msg"]


def test_GO_analysis_with_STRING_proteins_list():
    current_out = GO_analysis_with_STRING(
        proteins_df=["Protein1", "Protein2", "Protein3"],
        gene_sets_restring=["KEGG"],
        organism=9606,
    )
    assert "messages" in current_out
    assert (
        "dataframe with Protein ID and direction of expression change column"
        in current_out["messages"][0]["msg"]
    )


def test_GO_analysis_with_STRING_no_fc_df():
    current_out = GO_analysis_with_STRING(
        proteins_df=pd.DataFrame(["Protein1", "Protein2", "Protein3"]),
        gene_sets_restring=["KEGG"],
        organism=9606,
    )
    assert "messages" in current_out
    assert (
        "dataframe with Protein ID and direction of expression change column"
        in current_out["messages"][0]["msg"]
    )


def test_GO_analysis_with_STRING_too_many_col_df():
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

    current_out = GO_analysis_with_STRING(
        proteins_df=test_intensity_df, gene_sets_restring=["KEGG"], organism=9606
    )
    assert "messages" in current_out
    assert (
        "dataframe with Protein ID and direction of expression change column"
        in current_out["messages"][0]["msg"]
    )


def test_GO_analysis_with_enrichr_wrong_proteins_input():
    current_out = GO_analysis_with_Enrichr(
        proteins_df="Protein1;Protein2;aStringOfProteins",
        organism="human",
        differential_expression_col="log2_fold_change",
        gene_sets_enrichr=["KEGG"],
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )

    assert "messages" in current_out
    assert (
        "dataframe with Protein ID and direction of expression change column"
        in current_out["messages"][0]["msg"]
    )


def test_GO_analysis_with_enrichr_wrong_gene_sets_input():
    current_out = GO_analysis_with_Enrichr(
        proteins_df=pd.DataFrame(
            {"Protein ID": ["Protein1"], "log2_fold_change": [1.0]}
        ),
        organism="human",
        differential_expression_col="log2_fold_change",
        gene_sets_path="aMadeUpInputFormat.abc",
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )
    assert "messages" in current_out


def test_GO_analysis_with_no_gene_sets_input():
    current_out = GO_analysis_with_Enrichr(
        proteins_df=pd.DataFrame(
            {"Protein ID": ["Protein1"], "log2_fold_change": [1.0]}
        ),
        organism="human",
        differential_expression_col="log2_fold_change",
        gene_sets_path=None,
        gene_sets_enrichr=None,
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )

    assert "messages" in current_out
    assert "No gene sets provided" in current_out["messages"][0]["msg"]


@patch("protzilla.data_integration.database_query.uniprot_groups_to_genes")
def test_GO_analysis_with_Enrichr(mock_gene_mapping, data_folder_tests):
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
    results = pd.read_csv(
        data_folder_tests / "Reactome_enrichment_enrichr_2022.csv",
        index_col=0,
    )
    gene_mapping_df = pd.DataFrame(
        {
            "Protein ID": [
                "Protein2",
                "Protein3",
                "Protein4",
                "Protein6;Protein7;Protein8",
                "Protein6;Protein7;Protein8",
                "Protein6;Protein7;Protein8",
                "Protein9;Protein10;Protein11",
                "Protein9;Protein10;Protein11",
            ],
            "Gene": ["ENO2", "ENO3", "HK2", "HK1", "HK3", "IDH3B", "GPT2", "SDHB"],
        }
    )

    filtered_protein_ids = (["Protein1", "Protein5", "Protein12;Protein13"],)

    current_out = GO_analysis_with_Enrichr(
        proteins_df=pd.DataFrame({"Protein ID": proteins, "fold_change": [1.0] * 8}),
        gene_mapping_df=gene_mapping_df,
        organism="human",
        differential_expression_col="fold_change",
        direction="up",
        gene_sets_path=data_folder_tests / "Reactome_2022.txt",
        background_path=None,
    )
    df = current_out["enrichment_df"]

    for col in ["Proteins", "Genes"]:
        df[col] = df[col].apply(lambda x: set(x.split(";")))
        results[col] = results[col].apply(lambda x: set(x.split(";")))
        df[col] = df[col].apply(lambda x: sorted(x))
        results[col] = results[col].apply(lambda x: sorted(x))

    column_names = ["Term", "Gene_set", "Overlap", "Proteins", "Genes"]
    # Compare all specified columns
    for column in column_names:
        assert df[column].equals(results[column])

    # Compare the numeric columns separately with a tolerance for numerical equality
    numerical_columns = ["Odds Ratio", "P-value", "Adjusted P-value", "Combined Score"]
    for column in numerical_columns:
        numerical_equal = np.isclose(
            df[column], results[column], rtol=1e-05, atol=1e-08
        )
        assert numerical_equal.all()

    assert "messages" in current_out
    assert "No background provided" in current_out["messages"][0]["msg"]
    assert "Some proteins could not be mapped" in current_out["messages"][1]["msg"]


def test_GO_analysis_Enrichr_wrong_background_file(data_folder_tests):
    current_out = GO_analysis_with_Enrichr(
        proteins_df=pd.DataFrame(
            {"Protein ID": ["Protein1"], "log2_fold_change": [1.0]}
        ),
        organism="human",
        differential_expression_col="log2_fold_change",
        direction="both",
        gene_sets_path=data_folder_tests / "Reactome_2022.txt",
        background_path="aMadeUpInputFormat.abc",
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )
    assert "messages" in current_out
    assert "Invalid file type for background" in current_out["messages"][0]["msg"]


@pytest.fixture
def GO_analysis_offline_result_no_bg():
    return {
        "Gene_set": ["gs_ind_0", "gs_ind_0"],
        "Term": ["Set1", "Set2"],
        "Overlap": ["4/8", "4/8"],
        "P-value": [1.000000e00, 1.000000e00],
        "Adjusted P-value": [1.000000e00, 1.000000e00],
        "Odds Ratio": [5.294118e-01, 5.294118e-01],
        "Combined Score": [0.000000e00, 0.000000e00],
        "Genes": [
            "Gene3;Gene2;Gene4;Gene1",
            "Gene5;Gene6;Gene3;Gene1",
        ],
        "Proteins": [
            "Protein3;Protein2;Protein4;Protein1",
            "Protein5;Protein6;Protein3;Protein1",
        ],
    }


@pytest.fixture
def GO_analysis_offline_result_with_bg():
    return {
        "Gene_set": ["gs_ind_0", "gs_ind_0"],
        "Term": ["Set1", "Set2"],
        "Overlap": ["4/8", "4/8"],
        "P-value": [7.272727e-01, 7.272727e-01],
        "Adjusted P-value": [7.272727e-01, 7.272727e-01],
        "Odds Ratio": [9.529412e-01, 9.529412e-01],
        "Genes": [
            "Gene3;Gene2;Gene4;Gene1",
            "Gene5;Gene6;Gene3;Gene1",
        ],
        "Proteins": [
            "Protein3;Protein2;Protein4;Protein1",
            "Protein5;Protein6;Protein3;Protein1",
        ],
    }


@pytest.fixture
def offline_mock_mapping():
    data = {
        "Protein ID": [
            "Protein1",
            "Protein2",
            "Protein3",
            "Protein4",
            "Protein5",
            "Protein6",
        ],
        "Gene": ["Gene1", "Gene2", "Gene3", "Gene4", "Gene5", "Gene6"],
    }
    mapping_df = pd.DataFrame(data)
    filtered = []
    return mapping_df, filtered


@pytest.mark.parametrize(
    "protein_sets_path",
    [
        PROJECT_PATH / "tests/test_data/enrichment_data/gene_sets.json",
        PROJECT_PATH / "tests/test_data/enrichment_data/gene_sets.csv",
        PROJECT_PATH / "tests/test_data/enrichment_data/gene_sets.txt",
    ],
)
def test_GO_analysis_offline_protein_sets(
    protein_sets_path,
    GO_analysis_offline_result_no_bg,
    offline_mock_mapping,
):
    results = pd.DataFrame(GO_analysis_offline_result_no_bg)
    proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
        "Protein4",
        "Protein5",
        "Protein6",
    ]
    proteins_df = pd.DataFrame({"Protein ID": proteins, "fold_change": [1.0] * 6})

    current_out = GO_analysis_offline(
        proteins_df=proteins_df,
        gene_sets_path=protein_sets_path,
        differential_expression_col="fold_change",
        direction="up",
        gene_mapping_df=offline_mock_mapping[0],
    )
    df = current_out["enrichment_df"]

    # Convert last column to list of sets because order can change
    cols = ["Genes", "Proteins"]
    for col in cols:
        df[col] = df[col].apply(lambda x: set(x.split(";")))
        results[col] = results[col].apply(lambda x: set(x.split(";")))
        df[col] = df[col].apply(lambda x: sorted(x))
        results[col] = results[col].apply(lambda x: sorted(x))

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
        PROJECT_PATH / "tests/test_data/enrichment_data//background_test_genes.csv",
        PROJECT_PATH / "tests/test_data/enrichment_data//background_test_genes.txt",
    ],
)
def test_GO_analysis_offline_background(
    background_path,
    GO_analysis_offline_result_with_bg,
    data_folder_tests,
    offline_mock_mapping,
):
    results = pd.DataFrame(GO_analysis_offline_result_with_bg)
    proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
        "Protein4",
        "Protein5",
        "Protein6",
    ]
    proteins_df = pd.DataFrame({"Protein ID": proteins, "fold_change": [-1.0] * 6})

    current_out = GO_analysis_offline(
        proteins_df=proteins_df,
        gene_sets_path=data_folder_tests / "gene_sets.txt",
        differential_expression_col="fold_change",
        differential_expression_threshold=1.0,  # all are downregulated
        direction="down",
        background_path=background_path,
        gene_mapping_df=offline_mock_mapping[0],
    )
    df = current_out["enrichment_df"]

    # Convert last column to list of sets because order can change
    cols = ["Genes", "Proteins"]
    for col in cols:
        df[col] = df[col].apply(lambda x: set(x.split(";")))
        results[col] = results[col].apply(lambda x: set(x.split(";")))
        df[col] = df[col].apply(lambda x: sorted(x))
        results[col] = results[col].apply(lambda x: sorted(x))

    column_names = ["Term", "Genes", "Proteins", "Gene_set", "Overlap"]
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


def test_GO_analysis_offline_no_protein_sets():
    proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
    ]
    proteins_df = pd.DataFrame({"Protein ID": proteins, "fold_change": [1.0] * 3})
    current_out = GO_analysis_offline(
        proteins_df=proteins_df,
        gene_sets_path="",
        differential_expression_col="fold_change",
        direction="up",
        background=None,
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )

    assert "messages" in current_out
    assert "No file uploaded for protein sets" in current_out["messages"][0]["msg"]


def test_GO_analysis_offline_invalid_protein_set_file():
    proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
    ]
    proteins_df = pd.DataFrame({"Protein ID": proteins, "fold_change": [1.0] * 3})
    current_out = GO_analysis_offline(
        proteins_df=proteins_df,
        gene_sets_path="an_invalid_filetype.png",
        differential_expression_col="fold_change",
        direction="up",
        background="",
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )

    assert "messages" in current_out
    assert "Invalid file type" in current_out["messages"][0]["msg"]
    assert "protein sets" in current_out["messages"][0]["msg"]


def test_GO_analysis_offline_invalid_background_set_file():
    proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
    ]
    proteins_df = pd.DataFrame({"Protein ID": proteins, "fold_change": [1.0] * 3})
    current_out = GO_analysis_offline(
        proteins_df=proteins_df,
        gene_sets_path="a_valid_filetype.gmt",
        differential_expression_col="fold_change",
        direction="up",
        background_path="an_invalid_filetype.png",
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
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
            "Adjusted P-value": [0.01, 0.05, 0.03, 0.001],
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

    merged = merge_up_down_regulated_dfs_gseapy(up_enriched, down_enriched)
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


@pytest.mark.parametrize(
    "protein_sets_path",
    [
        PROJECT_PATH / "tests/test_data/enrichment_data/gene_sets.json",
        PROJECT_PATH / "tests/test_data/enrichment_data/gene_sets.csv",
        PROJECT_PATH / "tests/test_data/enrichment_data/gene_sets.txt",
    ],
)
def test_read_protein_or_gene_sets_file(protein_sets_path):
    expected_output = {
        "Set1": [
            "Gene1",
            "Gene2",
            "Gene3",
            "Gene4",
            "Gene7",
            "Gene8",
            "Gene9",
            "Gene10",
        ],
        "Set2": [
            "Gene1",
            "Gene3",
            "Gene5",
            "Gene6",
            "Gene7",
            "Gene8",
            "Gene9",
            "Gene10",
        ],
    }

    result_dict = read_protein_or_gene_sets_file(protein_sets_path)
    assert result_dict == expected_output


def test_read_protein_or_gene_sets_file_gmt_path():
    a_made_up_path = "test_data/a_gmt_file.gmt"
    out_path = read_protein_or_gene_sets_file(a_made_up_path)
    assert out_path == a_made_up_path


def test_read_protein_or_gene_sets_file_no_path():
    out_dict = read_protein_or_gene_sets_file("")
    assert "messages" in out_dict
    assert "No file uploaded for protein sets." in out_dict["messages"][0]["msg"]


def test_read_protein_or_gene_sets_file_invalid_filetype(data_folder_tests):
    a_made_up_path = data_folder_tests / "a_made_up_wrong_file.png"
    out_dict = read_protein_or_gene_sets_file(a_made_up_path)

    assert "messages" in out_dict
    assert "Invalid file type" in out_dict["messages"][0]["msg"]


@pytest.mark.parametrize(
    "background_path",
    [
        PROJECT_PATH / "tests/test_data/enrichment_data//background_test_genes.csv",
        PROJECT_PATH / "tests/test_data/enrichment_data//background_test_genes.txt",
    ],
)
def test_read_background_file(background_path):
    expected_output = [
        "Gene1",
        "Gene2",
        "Gene3",
        "Gene4",
        "Gene5",
        "Gene6",
        "Gene7",
        "Gene8",
        "Gene9",
        "Gene10",
        "Gene11",
        "Gene12",
    ]

    result_list = read_background_file(background_path)
    assert result_list == expected_output


def test_read_background_file_no_path():
    assert read_background_file("") is None
    assert read_background_file(None) is None


def test_read_background_file_invalid_filetype():
    out_dict = read_background_file("a_made_up_wrong_file.png")

    assert "messages" in out_dict
    assert "Invalid file type" in out_dict["messages"][0]["msg"]


def test_create_genes_intensity_wide_df(data_folder_tests):
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 10],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 30],
        ["Sample1", "Protein4", "Gene4", 40],
        ["Sample1", "Protein5", "Gene5", 50],
        ["Sample2", "Protein1", "Gene1", 1],
        ["Sample2", "Protein2", "Gene2", 2],
        ["Sample2", "Protein3", "Gene3", 3],
        ["Sample2", "Protein4", "Gene4", 4],
        ["Sample2", "Protein5", "Gene5", 5],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 90],
        ["Sample3", "Protein3", "Gene3", 80],
        ["Sample3", "Protein4", "Gene4", 70],
        ["Sample3", "Protein5", "Gene5", 60],
    )
    protein_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    protein_group_to_genes = {
        "Protein1": ["Gene1", "Gene1-1"],  # multiple genes per group
        "Protein2": ["Gene2"],
        "Protein3": ["Gene3"],
        "Protein4": ["Gene3"],  # duplicate gene
    }

    wide_df = create_genes_intensity_wide_df(
        protein_df=protein_df,
        protein_groups=protein_df["Protein ID"].unique().tolist(),
        samples=protein_df["Sample"].unique().tolist(),
        protein_group_to_genes=protein_group_to_genes,
        filtered_groups=["Protein5"],  # not in protein_group_to_genes
    )

    expected_df = pd.DataFrame(
        {
            "Gene symbol": ["Gene1", "Gene1-1", "Gene2", "Gene3"],
            "Sample1": [10.0, 10.0, 20.0, 35.0],
            "Sample2": [1.0, 1.0, 2.0, 3.5],
            "Sample3": [100.0, 100.0, 90.0, 75.0],
        }
    )
    expected_df[["Sample1", "Sample2", "Sample3"]] = expected_df[
        ["Sample1", "Sample2", "Sample3"]
    ].astype(float)
    expected_df = expected_df.set_index("Gene symbol")
    pd.testing.assert_frame_equal(wide_df, expected_df, check_dtype=False)


def test_gsea_log2_metric_with_negative_values(data_folder_tests):
    proteins = pd.read_csv(
        data_folder_tests / "input-t_test-significant_proteins_intensity_df.csv",
        index_col=0,
    )
    metadata_df = pd.read_csv(data_folder_tests / "metadata_full.csv")

    current_out = gsea(
        proteins,
        metadata_df=metadata_df,
        grouping="Group",
        group1="CTR",
        group2="AD",
        gene_sets_enrichr=["KEGG_2016"],
        min_size=4,
        number_of_permutations=500,
        ranking_method="log2_ratio_of_classes",
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )
    assert "messages" in current_out
    assert "Negative values" in current_out["messages"][0]["msg"]
    assert "use a different ranking method" in current_out["messages"][0]["msg"]


def test_gsea(data_folder_tests):
    proteins = pd.read_csv(
        data_folder_tests / "input-t_test-significant_proteins_intensity_df.csv",
        index_col=0,
    )
    metadata_df = pd.read_csv(data_folder_tests / "metadata_full.csv")
    expected_enrichment_df = pd.read_csv(
        data_folder_tests / "gsea_result_sig_prot.csv", index_col=0
    )

    mock_mapping_df = pd.read_csv(data_folder_tests / "gene_mapping.csv")

    current_out = gsea(
        protein_df=proteins,
        metadata_df=metadata_df,
        grouping="Group",
        group1="CTR",
        group2="AD",
        gene_sets_enrichr=["KEGG_2016"],
        min_size=7,
        number_of_permutations=500,
        gene_mapping_df=mock_mapping_df,
    )
    assert "messages" in current_out
    assert "Some proteins could not be mapped" in current_out["messages"][0]["msg"]

    column_names = ["Name", "Term", "Tag %", "Gene %", "Lead_genes", "Lead_proteins"]
    # Compare all specified columns
    for column in column_names:
        assert expected_enrichment_df[column].equals(
            current_out["enrichment_df"][column]
        )

    # Compare the numeric columns separately with a tolerance for numerical equality
    numerical_columns = [
        "ES",
        "NES",
        "NOM p-val",
        "FDR q-val",
        "FWER p-val",
    ]
    current_out["enrichment_df"][numerical_columns] = current_out["enrichment_df"][
        numerical_columns
    ].astype(float)
    for column in numerical_columns:
        numerical_equal = np.isclose(
            expected_enrichment_df[column],
            current_out["enrichment_df"][column],
            rtol=1e-05,
            atol=1e-08,
        )
        assert numerical_equal.all()


def test_gsea_wrong_protein_df(data_folder_tests):
    proteins = pd.read_csv(
        data_folder_tests / "input-t_test-significant_proteins_pvalues_df.csv",
        index_col=0,
    )  # not an intensity df

    current_out = gsea(
        proteins,
        metadata_df=pd.DataFrame({"Group": ["CTR", "CTR", "AD"]}),
        grouping="Group",
        group1="CTR",
        group2="AD",
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )
    assert "messages" in current_out
    assert "Input must be a dataframe" in current_out["messages"][0]["msg"]


def test_gsea_no_gene_sets(data_folder_tests):
    proteins = pd.read_csv(
        data_folder_tests / "input-t_test-significant_proteins_intensity_df.csv",
        index_col=0,
    )
    current_out = gsea(
        proteins,
        metadata_df=pd.DataFrame({"Group": ["CTR", "CTR", "AD"]}),
        grouping="Group",
        group1="CTR",
        group2="AD",
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )
    assert "messages" in current_out
    assert "No gene sets provided" in current_out["messages"][0]["msg"]


def test_gsea_wrong_gene_sets(data_folder_tests):
    proteins = pd.read_csv(
        data_folder_tests / "input-t_test-significant_proteins_intensity_df.csv",
        index_col=0,
    )
    current_out = gsea(
        proteins,
        metadata_df=pd.DataFrame(columns=["Group"]),
        grouping="Group",
        group1="CTR",
        group2="AD",
        gene_sets_path="a_made_up_path.png",
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )
    assert "messages" in current_out  # read_protein_or_gene_sets_file should fail


def test_gsea_no_gene_symbols(data_folder_tests):
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 10],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample2", "Protein1", "Gene1", 1],
        ["Sample2", "Protein2", "Gene2", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 90],
    )
    protein_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    metadata_df = pd.read_csv(data_folder_tests / "metadata_full.csv")
    current_out = gsea(
        protein_df,
        metadata_df=metadata_df,
        grouping="Group",
        group1="CTR",
        group2="AD",
        gene_sets_enrichr=["KEGG_2019_Human"],
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )

    assert "messages" in current_out
    assert (
        "No proteins could be mapped to gene symbols"
        in current_out["messages"][0]["msg"]
    )


def test_gsea_grouping_not_in_metadata_df():
    current_out = gsea(
        protein_df=pd.DataFrame(),
        metadata_df=pd.DataFrame(),
        grouping="Group",
        gene_sets_path="a_made_up_path_but_valid_filetype.gmt",
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )

    assert "messages" in current_out
    assert "Grouping column not in metadata df" in current_out["messages"][0]["msg"]


def test_gsea_group_not_in_grouping():
    current_out = gsea(
        protein_df=pd.DataFrame(),
        metadata_df=pd.DataFrame(columns=["Group"]),
        grouping="Group",
        group1="Group1",
        group2="Group2",
        gene_sets_path="a_made_up_path_but_valid_filetype.gmt",
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )

    assert "messages" in current_out
    assert "Group names should be in metadata df" in current_out["messages"][0]["msg"]


def test_gsea_catch_fail():
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 10],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample2", "Protein1", "Gene1", 1],
        ["Sample2", "Protein2", "Gene2", 2],
    )
    protein_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    metadata_df = pd.DataFrame(
        data=(
            ["Sample1", "Group1"],
            ["Sample2", "Group2"],
        ),
        columns=["Sample", "Group"],
    )
    mock_mapping_df = pd.DataFrame(
        {"Protein ID": ["Protein1", "Protein2"], "Gene": ["Gene1", "Gene2"]}
    )

    current_out = gsea(
        protein_df=protein_df,
        metadata_df=metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        gene_sets_path="a_made_up_path_but_valid_filetype.gmt",
        gene_mapping_df=mock_mapping_df,
    )  # gp.gsea() should fail
    assert "messages" in current_out
    assert "GSEA failed. Please check your input" in current_out["messages"][0]["msg"]


def test_create_ranked_df():
    test_p_value_list = (
        ["Protein1", 0.01],
        ["Protein2", 0.02],
        ["Protein3-1;Protein3-2;Protein4", 0.03],
        ["CON__Protein3-1;CON__Protein3-2;CON__Protein3", 0.035],
        ["Protein5", 0.04],
        ["Protein6", 0.001],
        ["Protein7", 0.0001],
        ["Protein8", 1],
    )
    proteins_df = pd.DataFrame(
        data=test_p_value_list,
        columns=["Protein ID", "corrected_p_value"],
    )
    protein_group_to_genes = {
        "Protein1": ["Gene1"],
        "Protein2": ["Gene2"],
        "Protein3-1;Protein3-2;Protein4": ["Gene3", "Gene4"],  # multiple genes
        "CON__Protein3-1;CON__Protein3-2;CON__Protein3": ["Gene3"],  # duplicate gene
        "Protein5": ["Gene5"],
        "Protein6": ["Gene6"],
    }
    expected_list = [
        ["Gene6", 0.001],
        ["Gene1", 0.01],
        ["Gene2", 0.02],
        ["Gene4", 0.03],
        ["Gene3", 0.035],
        ["Gene5", 0.04],
    ]
    expected_df = pd.DataFrame(
        data=expected_list,  # sorted by pvalue
        columns=["Gene symbol", "Ranking value"],
    ).set_index("Gene symbol")

    ranked_df = create_ranked_df(
        protein_groups=proteins_df["Protein ID"].unique().tolist(),
        protein_df=proteins_df,
        ranking_column="corrected_p_value",
        ranking_direction="ascending",
        protein_group_to_genes=protein_group_to_genes,
        filtered_groups=["Protein7", "Protein8"],  # not in protein_group_to_genes
    )
    assert ranked_df.equals(expected_df)


def test_create_ranked_df_descending():
    test_log2fc_list = (
        ["Protein1", -0.01],
        ["Protein2", -0.02],
        ["Protein3-1;Protein3-2;Protein4", 0.03],
        ["CON__Protein3-1;CON__Protein3-2;CON__Protein3", 0.035],
        ["Protein5", 0.04],
        ["Protein6", -0.001],
        ["Protein7", 0.0001],
        ["Protein8", 1],
    )
    proteins_df = pd.DataFrame(
        data=test_log2fc_list,
        columns=["Protein ID", "log2fc"],
    )
    protein_group_to_genes = {
        "Protein1": ["Gene1"],
        "Protein2": ["Gene2"],
        "Protein3-1;Protein3-2;Protein4": ["Gene3", "Gene4"],  # multiple genes
        "CON__Protein3-1;CON__Protein3-2;CON__Protein3": ["Gene3"],  # duplicate gene
        "Protein5": ["Gene5"],
        "Protein6": ["Gene6"],
    }
    expected_list = [
        ["Gene5", 0.04],
        ["Gene3", 0.03],
        ["Gene4", 0.03],
        ["Gene6", -0.001],
        ["Gene1", -0.01],
        ["Gene2", -0.02],
    ]
    expected_df = pd.DataFrame(
        data=expected_list,  # sorted by log2fc
        columns=["Gene symbol", "Ranking value"],
    ).set_index("Gene symbol")

    ranked_df = create_ranked_df(
        protein_groups=proteins_df["Protein ID"].unique().tolist(),
        protein_df=proteins_df,
        ranking_column="log2fc",
        ranking_direction="descending",
        protein_group_to_genes=protein_group_to_genes,
        filtered_groups=["Protein7", "Protein8"],  # not in protein_group_to_genes
    )
    assert ranked_df.equals(expected_df)


def test_gsea_preranked(data_folder_tests):
    proteins_significant = pd.read_csv(
        data_folder_tests / "input-t_test-significant_proteins_pvalues_df.csv",
        index_col=0,
    )
    expected_ranking = pd.read_csv(
        data_folder_tests / "gsea_preranked_rank.csv", index_col=0
    )
    expected_ranking = expected_ranking["prerank"]  # convert to series
    expected_enrichment_df = pd.read_csv(
        data_folder_tests / "gsea_preranked_enriched.csv", index_col=0
    )

    mock_mapping_df = pd.read_csv(data_folder_tests / "gene_mapping.csv")

    current_out = gsea_preranked(
        protein_df=proteins_significant,
        ranking_column="corrected_p_value",
        ranking_direction="ascending",
        gene_sets_enrichr=["KEGG_2019_Human"],
        gene_mapping_df=mock_mapping_df,
    )
    assert "messages" in current_out
    assert "Some proteins could not be mapped" in current_out["messages"][0]["msg"]

    numerical_equal = np.isclose(
        current_out["ranking"], expected_ranking, rtol=1e-05, atol=1e-08
    )
    assert numerical_equal.all()

    column_names = ["Name", "Term", "Tag %", "Gene %", "Lead_genes", "Lead_proteins"]
    # Compare all specified columns
    for column in column_names:
        assert expected_enrichment_df[column].equals(
            current_out["enrichment_df"][column]
        )

    # Compare the numeric columns separately with a tolerance for numerical equality
    numerical_columns = [
        "ES",
        "NES",
        "NOM p-val",
        "FDR q-val",
        "FWER p-val",
    ]
    current_out["enrichment_df"][numerical_columns] = current_out["enrichment_df"][
        numerical_columns
    ].astype(float)
    for column in numerical_columns:
        numerical_equal = np.isclose(
            expected_enrichment_df[column],
            current_out["enrichment_df"][column],
            rtol=1e-05,
            atol=1e-08,
        )
        assert numerical_equal.all()


def test_gsea_preranked_wrong_protein_df():
    df = pd.DataFrame(
        {"Protein ID": ["Protein1", "Protein2"], "Sample1": ["Sample1", "Sample2"]}
    )

    current_out = gsea_preranked(
        df, gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"])
    )
    assert "messages" in current_out
    assert "Proteins must be a dataframe" in current_out["messages"][0]["msg"]


def test_gsea_preranked_no_gene_sets(data_folder_tests):
    proteins_df = pd.read_csv(
        data_folder_tests / "input-t_test-significant_proteins_pvalues_df.csv",
        index_col=0,
    )
    current_out = gsea_preranked(
        protein_df=proteins_df,
        ranking_column="corrected_p_value",
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )
    assert "messages" in current_out
    assert "No gene sets provided" in current_out["messages"][0]["msg"]


def test_gsea_preranked_wrong_gene_sets(data_folder_tests):
    proteins_df = pd.read_csv(
        data_folder_tests / "input-t_test-significant_proteins_pvalues_df.csv",
        index_col=0,
    )
    current_out = gsea_preranked(
        proteins_df,
        gene_sets_path="a_made_up_path.png",
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )
    assert "messages" in current_out  # read_protein_or_gene_sets_file should fail


def test_gsea_preranked_no_gene_symbols():
    proteins_df = pd.DataFrame(
        data=(
            ["Protein1", 0.01],
            ["Protein2", 0.02],
        ),
        columns=["Protein ID", "corrected_p_value"],
    )

    current_out = gsea_preranked(
        proteins_df,
        ranking_column="corrected_p_value",
        gene_sets_enrichr=["KEGG_2019_Human"],
        gene_mapping_df=pd.DataFrame(columns=["Protein ID", "Gene"]),
    )

    assert "messages" in current_out
    assert "No proteins could be mapped" in current_out["messages"][0]["msg"]
