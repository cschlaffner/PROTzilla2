import time
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
import requests

from protzilla.constants.paths import PROJECT_PATH

# order is important to ensure correctness of patched functions
from protzilla.data_integration.enrichment_analysis_helper import *  # isort:skip
from protzilla.data_integration.enrichment_analysis import *  # isort:skip
from protzilla.data_integration.enrichment_analysis_gsea import *  # isort:skip


@pytest.fixture
def data_folder_tests():
    return f"{PROJECT_PATH}/tests/test_data/enrichment_data"


@patch("protzilla.data_integration.enrichment_analysis_helper.biomart_query")
def test_uniprot_ids_to_uppercase_gene_symbols(mock_biomart_query):
    proteins = [
        "Protein1",
        "Protein2;ProteinX",
        "Protein03",
        "Protein3-1",
        "Protein4_VAR_A12345",
        "Protein5",
        "Protein6",
        "Protein7;Protein8",
    ]
    mock_biomart_query.return_value = [
        ("Protein1", "GENE1"),
        ("Protein2", "GENE2"),
        ("ProteinX", "GENE2"),
        ("Protein03", "GENE3"),
        ("Protein3", "GENE3"),
        ("Protein4", "GENE4"),
        ("Protein7", "GENE7"),
        ("Protein8", "GENE8"),
    ]

    expected_gene_to_groups = {
        "GENE1": ["Protein1"],
        "GENE2": ["Protein2;ProteinX"],
        "GENE3": [
            "Protein03",
            "Protein3-1",
        ],  # this should not happen but is handled in case it does
        "GENE4": ["Protein4_VAR_A12345"],
        "GENE7": ["Protein7;Protein8"],
        "GENE8": ["Protein7;Protein8"],
    }
    expected_group_to_genes = {
        "Protein1": ["GENE1"],
        "Protein2;ProteinX": ["GENE2"],
        "Protein03": ["GENE3"],
        "Protein3-1": ["GENE3"],
        "Protein4_VAR_A12345": ["GENE4"],
        "Protein7;Protein8": ["GENE7", "GENE8"],
    }
    expected_filtered_groups = ["Protein5", "Protein6"]

    (
        gene_to_groups,
        group_to_genes,
        filtered_groups,
    ) = uniprot_ids_to_uppercase_gene_symbols(proteins)

    for key in gene_to_groups:
        assert set(gene_to_groups[key]) == set(expected_gene_to_groups[key])
    for key in group_to_genes:
        assert set(group_to_genes[key]) == set(expected_group_to_genes[key])
    assert filtered_groups == expected_filtered_groups


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
    string_params = {"species": 9606, "caller_ID": "PROTzilla"}
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
            "p_value": [0.05, 0.2, 0.3],
            "fdr": [0.4, 0.6, 0.7],
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
        f"{PROJECT_PATH}/tests/test_data/enrichment_data/background_imported_proteins.csv",
    ],
)
def test_go_analysis_with_STRING(mock_enrichment, background, data_folder_tests):
    proteins_df = pd.read_csv(
        f"{data_folder_tests}/input-t_test-log2_fold_change_df.csv"
    )

    up_df = pd.read_csv(
        f"{data_folder_tests}/up_enrichment_KEGG_Process.csv", header=0, index_col=0
    )
    down_df = pd.read_csv(
        f"{data_folder_tests}/down_enrichment_KEGG_Process.csv", header=0, index_col=0
    )

    results = pd.read_csv(f"{data_folder_tests}/merged_KEGG_process.csv", header=0)
    mock_enrichment.side_effect = [up_df, down_df]

    out_df = go_analysis_with_STRING(
        proteins=proteins_df,
        protein_set_dbs=["KEGG", "Process"],
        organism=9606,
        direction="both",
        background=background,
    )["enriched_df"]

    for col in ["inputGenes", "preferredNames"]:
        out_df[col] = out_df[col].apply(lambda x: set(x.split(",")))
        results[col] = results[col].apply(lambda x: set(x.split(",")))
        out_df[col] = out_df[col].apply(lambda x: sorted(x))
        results[col] = results[col].apply(lambda x: sorted(x))

    pd.testing.assert_frame_equal(results, out_df, check_dtype=False)


@patch(
    "protzilla.data_integration.enrichment_analysis.get_functional_enrichment_with_delay"
)
def test_go_analysis_with_STRING_one_direction_missing(
    mock_enrichment, data_folder_tests
):
    proteins_df = pd.read_csv(
        f"{data_folder_tests}/input-t_test-log2_fold_change_df.csv"
    )
    up_proteins_df = proteins_df[proteins_df["log2_fold_change"] > 0]
    down_proteins_df = proteins_df[proteins_df["log2_fold_change"] < 0]

    up_df = pd.read_csv(f"{data_folder_tests}/up_enrichment_KEGG_Process.csv", header=0)
    down_df = pd.read_csv(
        f"{data_folder_tests}/down_enrichment_KEGG_Process.csv", header=0
    )
    mock_enrichment.side_effect = [up_df, down_df]

    current_out = go_analysis_with_STRING(
        proteins=up_proteins_df,
        protein_set_dbs=["KEGG", "Process"],
        organism=9606,
        direction="both",
    )
    assert "messages" in current_out
    assert "No downregulated proteins" in current_out["messages"][0]["msg"]

    current_out = go_analysis_with_STRING(
        proteins=down_proteins_df,
        protein_set_dbs=["KEGG", "Process"],
        organism=9606,
        direction="both",
    )

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
def test_go_analysis_with_enrichr(mock_gene_mapping, data_folder_tests):
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
    results = pd.read_csv(
        f"{data_folder_tests}/Reactome_enrichment_enrichr.csv", sep="\t"
    )

    mock_gene_mapping.return_value = (
        {
            "ENO1": ["Protein1"],
            "ENO2": ["Protein2"],
            "ENO3": ["Protein3"],
            "HK2": ["Protein4"],
            "HK1": ["Protein6"],
            "HK3": ["Protein7"],
            "IDH3B": ["Protein8"],
            "ATP6V1G2": ["Protein9"],
            "GPT2": ["Protein10"],
            "SDHB": ["Protein11"],
            "COX6B1": ["Protein12;Protein13"],
        },
        {
            "Protein1": ["ENO1"],
            "Protein2": ["ENO2"],
            "Protein3": ["ENO3"],
            "Protein4": ["HK2"],
            "Protein6": ["HK1"],
            "Protein7": ["HK3"],
            "Protein8": ["IDH3B"],
            "Protein9": ["ATP6V1G2"],
            "Protein10": ["GPT2"],
            "Protein11": ["SDHB"],
            "Protein12;Protein13": ["COX6B1"],
        },
        ["Protein5"],
    )
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
    background_path, go_analysis_offline_result_with_bg, data_folder_tests
):
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
        protein_sets_path=f"{data_folder_tests}/protein_sets.txt",
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


@pytest.mark.parametrize(
    "protein_sets_path",
    [
        f"{PROJECT_PATH}/tests/test_data/enrichment_data/protein_sets.json",
        f"{PROJECT_PATH}/tests/test_data/enrichment_data/protein_sets.csv",
        f"{PROJECT_PATH}/tests/test_data/enrichment_data/protein_sets.txt",
    ],
)
def test_read_protein_or_gene_sets_file(protein_sets_path):
    expected_output = {
        "Set1": [
            "Protein1",
            "Protein2",
            "Protein3",
            "Protein4",
            "Protein7",
            "Protein8",
            "Protein9",
            "Protein10",
        ],
        "Set2": [
            "Protein1",
            "Protein3",
            "Protein5",
            "Protein6",
            "Protein7",
            "Protein8",
            "Protein9",
            "Protein10",
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
    a_made_up_path = f"{data_folder_tests}/a_made_up_wrong_file.png"
    out_dict = read_protein_or_gene_sets_file(a_made_up_path)

    assert "messages" in out_dict
    assert "Invalid file type" in out_dict["messages"][0]["msg"]


def test_create_ranked_df(data_folder_tests):
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
    group_to_genes = {
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
        ranking_direction="ascending",
        group_to_genes=group_to_genes,
        filtered_groups=["Protein7", "Protein8"],  # not in group_to_genes
    )
    assert ranked_df.equals(expected_df)


def test_create_ranked_df_descending(data_folder_tests):
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
    group_to_genes = {
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
        ranking_direction="descending",
        group_to_genes=group_to_genes,
        filtered_groups=["Protein7", "Protein8"],  # not in group_to_genes
    )
    assert ranked_df.equals(expected_df)


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
    group_to_genes = {
        "Protein1": ["Gene1", "Gene1-1"],  # multiple genes per group
        "Protein2": ["Gene2"],
        "Protein3": ["Gene3"],
        "Protein4": ["Gene3"],  # duplicate gene
    }

    wide_df = create_genes_intensity_wide_df(
        protein_df=protein_df,
        protein_groups=protein_df["Protein ID"].unique().tolist(),
        samples=protein_df["Sample"].unique().tolist(),
        group_to_genes=group_to_genes,
        filtered_groups=["Protein5"],  # not in group_to_genes
    )

    expected_df = pd.DataFrame(
        np.array(
            [
                ["Gene1", 10.0, 1.0, 100.0],
                ["Gene1-1", 10.0, 1.0, 100.0],
                ["Gene2", 20.0, 2.0, 90.0],
                ["Gene3", 35.0, 3.5, 75.0],
            ]
        ),
        columns=["Gene symbol", "Sample1", "Sample2", "Sample3"],
    )
    expected_df[["Sample1", "Sample2", "Sample3"]] = expected_df[
        ["Sample1", "Sample2", "Sample3"]
    ].astype(float)
    expected_df = expected_df.set_index("Gene symbol")
    pd.testing.assert_frame_equal(wide_df, expected_df, check_dtype=False)


def test_gsea_log2_metric_with_negative_values(data_folder_tests):
    proteins = pd.read_csv(
        f"{data_folder_tests}/input-t_test-significant_proteins_intensity_df.csv",
        index_col=0,
    )
    metadata_df = pd.read_csv(f"{data_folder_tests}/metadata_full.csv")

    current_out = gsea(
        proteins,
        metadata_df=metadata_df,
        grouping="Group",
        gene_sets_enrichr=["KEGG_2016"],
        min_size=4,
        number_of_permutations=500,
        ranking_method="log2_ratio_of_classes",
    )
    assert "messages" in current_out
    assert "Negative values" in current_out["messages"][0]["msg"]
    assert "use a different ranking method" in current_out["messages"][0]["msg"]


@pytest.mark.internet
@patch(
    "protzilla.data_integration.enrichment_analysis_gsea.uniprot_ids_to_uppercase_gene_symbols"
)
def test_gsea(mock_mapping, data_folder_tests):
    proteins = pd.read_csv(
        f"{data_folder_tests}/input-t_test-significant_proteins_intensity_df.csv",
        index_col=0,
    )
    metadata_df = pd.read_csv(
        f"{data_folder_tests}/metadata_full.csv",
    )
    expected_enriched_df = pd.read_csv(
        f"{data_folder_tests}/gsea_result_sig_prot_pre_mapped.csv", index_col=0
    )

    with open(f"{data_folder_tests}/gene_mapping.json", "r") as f:
        data = json.load(f)
        gene_to_groups = data["gene_to_groups"]
        group_to_genes = data["group_to_genes"]
        filtered_groups = data["filtered_groups"]
        mock_mapping.return_value = gene_to_groups, group_to_genes, filtered_groups

    current_out = gsea(
        protein_df=proteins,
        metadata_df=metadata_df,
        grouping="Group",
        gene_sets_enrichr=["KEGG_2016"],
        min_size=7,
        number_of_permutations=500,
    )
    assert "messages" in current_out
    assert "Some proteins could not be mapped" in current_out["messages"][0]["msg"]

    column_names = ["Name", "Term", "Tag %", "Gene %", "Lead_genes", "Lead_proteins"]
    # Compare all specified columns
    for column in column_names:
        assert expected_enriched_df[column].equals(current_out["enriched_df"][column])

    # Compare the numeric columns separately with a tolerance for numerical equality
    numerical_columns = [
        "ES",
        "NES",
        "NOM p-val",
        "FDR q-val",
        "FWER p-val",
    ]
    current_out["enriched_df"][numerical_columns] = current_out["enriched_df"][
        numerical_columns
    ].astype(float)
    for column in numerical_columns:
        expected_enriched_df[column]
        numerical_equal = np.isclose(
            expected_enriched_df[column],
            current_out["enriched_df"][column],
            rtol=1e-05,
            atol=1e-08,
        )
        assert numerical_equal.all()


def test_gsea_wrong_protein_df(data_folder_tests):
    proteins = pd.read_csv(
        f"{data_folder_tests}/input-t_test-significant_proteins_pvalues_df.csv",
        index_col=0,
    )  # not an intensity df

    current_out = gsea(
        proteins,
        metadata_df=pd.DataFrame(columns=["Group"]),
        grouping="Group",
    )
    assert "messages" in current_out
    assert "Input must be a dataframe" in current_out["messages"][0]["msg"]


def test_gsea_no_gene_sets(data_folder_tests):
    proteins = pd.read_csv(
        f"{data_folder_tests}/input-t_test-significant_proteins_intensity_df.csv",
        index_col=0,
    )
    current_out = gsea(
        proteins,
        metadata_df=pd.DataFrame(columns=["Group"]),
        grouping="Group",
    )
    assert "messages" in current_out
    assert "No gene sets provided" in current_out["messages"][0]["msg"]


def test_gsea_wrong_gene_sets(data_folder_tests):
    proteins = pd.read_csv(
        f"{data_folder_tests}/input-t_test-significant_proteins_intensity_df.csv",
        index_col=0,
    )
    current_out = gsea(
        proteins,
        metadata_df=pd.DataFrame(columns=["Group"]),
        grouping="Group",
        gene_sets_path="a_made_up_path.png",
    )
    assert "messages" in current_out  # read_protein_or_gene_sets_file should fail


@patch(
    "protzilla.data_integration.enrichment_analysis_gsea.uniprot_ids_to_uppercase_gene_symbols"
)
def test_gsea_no_gene_symbols(mock_gene_mapping):
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
    mock_gene_mapping.return_value = ({}, {}, ["Protein1", "Protein2"])
    current_out = gsea(
        protein_df,
        metadata_df=pd.DataFrame(columns=["Group"]),
        grouping="Group",
        gene_sets_enrichr=["KEGG_2019_Human"],
    )

    assert "messages" in current_out
    assert "All proteins could not be mapped" in current_out["messages"][0]["msg"]


@patch(
    "protzilla.data_integration.enrichment_analysis_gsea.uniprot_ids_to_uppercase_gene_symbols"
)
def test_gsea_wrong_sample_group_amount(mock_mapping):
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
    metadata_df = pd.DataFrame(
        data=(
            ["Sample1", "Group1"],
            ["Sample2", "Group2"],
            ["Sample3", "Group3"],  # too many groups
        ),
        columns=["Sample", "Group"],
    )
    mock_mapping.return_value = (
        {"Gene1": ["Protein1"], "Gene2": ["Protein2"]},
        {"Protein1": ["Gene1"], "Protein2": ["Gene2"]},
        [],
    )
    current_out = gsea(
        protein_df=protein_df,
        metadata_df=metadata_df,
        grouping="Group",
        gene_sets_path="a_made_up_path_but_valid_filetype.gmt",
    )

    assert "messages" in current_out
    assert (
        "Input samples have to belong to exactly two groups"
        in current_out["messages"][0]["msg"]
    )


@patch(
    "protzilla.data_integration.enrichment_analysis_gsea.uniprot_ids_to_uppercase_gene_symbols"
)
def test_gsea_catch_fail(mock_mapping):
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
    mock_mapping.return_value = (
        {"Gene1": ["Protein1"], "Gene2": ["Protein2"]},
        {"Protein1": ["Gene1"], "Protein2": ["Gene2"]},
        [],
    )
    current_out = gsea(
        protein_df=protein_df,
        metadata_df=metadata_df,
        grouping="Group",
        gene_sets_path="a_made_up_path_but_valid_filetype.gmt",
    )  # gp.gsea() should fail
    assert "messages" in current_out
    assert "GSEA failed. Please check your input" in current_out["messages"][0]["msg"]


@pytest.mark.internet
@patch(
    "protzilla.data_integration.enrichment_analysis_gsea.uniprot_ids_to_uppercase_gene_symbols"
)
def test_gsea_preranked(mock_mapping, data_folder_tests):
    proteins_significant = pd.read_csv(
        f"{data_folder_tests}/input-t_test-significant_proteins_pvalues_df.csv",
        index_col=0,
    )
    expected_ranking = pd.read_csv(
        f"{data_folder_tests}/gsea_preranked_rank.csv", index_col=0
    )
    expected_ranking = expected_ranking["prerank"]  # convert to series
    expected_enriched_df = pd.read_csv(
        f"{data_folder_tests}/gsea_preranked_enriched.csv", index_col=0
    )

    with open(f"{data_folder_tests}/gene_mapping.json", "r") as f:
        data = json.load(f)
        gene_to_groups = data["gene_to_groups"]
        group_to_genes = data["group_to_genes"]
        filtered_groups = data["filtered_groups"]
        mock_mapping.return_value = gene_to_groups, group_to_genes, filtered_groups

    current_out = gsea_preranked(
        proteins_significant, "ascending", gene_sets_enrichr=["KEGG_2019_Human"]
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
        assert expected_enriched_df[column].equals(current_out["enriched_df"][column])

    # Compare the numeric columns separately with a tolerance for numerical equality
    numerical_columns = [
        "ES",
        "NES",
        "NOM p-val",
        "FDR q-val",
        "FWER p-val",
    ]
    current_out["enriched_df"][numerical_columns] = current_out["enriched_df"][
        numerical_columns
    ].astype(float)
    for column in numerical_columns:
        expected_enriched_df[column]
        numerical_equal = np.isclose(
            expected_enriched_df[column],
            current_out["enriched_df"][column],
            rtol=1e-05,
            atol=1e-08,
        )
        assert numerical_equal.all()


def test_gsea_preranked_wrong_protein_df():
    df = pd.DataFrame(
        {"Protein ID": ["Protein1", "Protein2"], "Sample1": ["Sample1", "Sample2"]}
    )

    current_out = gsea_preranked(df)
    assert "messages" in current_out
    assert "Proteins must be a dataframe" in current_out["messages"][0]["msg"]


def test_gsea_preranked_no_gene_sets(data_folder_tests):
    proteins_df = pd.read_csv(
        f"{data_folder_tests}/input-t_test-significant_proteins_pvalues_df.csv",
        index_col=0,
    )
    current_out = gsea_preranked(proteins_df)
    assert "messages" in current_out
    assert "No gene sets provided" in current_out["messages"][0]["msg"]


def test_gsea_preranked_wrong_gene_sets(data_folder_tests):
    proteins_df = pd.read_csv(
        f"{data_folder_tests}/input-t_test-significant_proteins_pvalues_df.csv",
        index_col=0,
    )
    current_out = gsea_preranked(proteins_df, gene_sets_path="a_made_up_path.png")
    assert "messages" in current_out  # read_protein_or_gene_sets_file should fail


@patch(
    "protzilla.data_integration.enrichment_analysis_gsea.uniprot_ids_to_uppercase_gene_symbols"
)
def test_gsea_preranked_no_gene_symbols(mock_gene_mapping):
    proteins_df = pd.DataFrame(
        data=(
            ["Protein1", 0.01],
            ["Protein2", 0.02],
        ),
        columns=["Protein ID", "corrected_p_value"],
    )
    mock_gene_mapping.return_value = ({}, {}, ["Protein1", "Protein2"])
    current_out = gsea_preranked(
        proteins_df,
        gene_sets_enrichr=["KEGG_2019_Human"],
    )

    assert "messages" in current_out
    assert "All proteins could not be mapped" in current_out["messages"][0]["msg"]


@patch(
    "protzilla.data_integration.enrichment_analysis_gsea.uniprot_ids_to_uppercase_gene_symbols"
)
def test_gsea_preranked_catch_fail(mock_mapping):
    proteins_df = pd.DataFrame(
        data=(
            ["Protein1", 0.01],
            ["Protein2", 0.02],
        ),
        columns=["Protein ID", "corrected_p_value"],
    )
    mock_mapping.return_value = (
        {"Gene1": "Protein1", "Gene2": "Protein2"},
        {"Protein1": ["Gene1"], "Protein2": ["Gene2"]},
        [],
    )
    current_out = gsea_preranked(
        proteins_df,
        gene_sets_path="a_made_up_path_but_valid_filetype.gmt",
    )  # gp.prerank() function should fail

    assert "messages" in current_out
    assert "An error occurred while running GSEA" in current_out["messages"][0]["msg"]
