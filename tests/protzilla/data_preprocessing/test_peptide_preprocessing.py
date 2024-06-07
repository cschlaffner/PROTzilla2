import numpy as np
import pandas as pd
import pytest

from protzilla.constants.paths import TEST_DATA_PATH
from protzilla.data_preprocessing.peptide_filter import by_pep_value, by_pep_value_plot
from protzilla.importing import peptide_import


@pytest.fixture
def leftover_peptide_df():
    # sample, protein id, sequence, intensity, pep
    leftover_peptide_protein_list = (
        ["Sample01", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", np.NAN, 0.037779],
        ["Sample02", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", np.NAN, 0.037779],
        ["Sample03", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", 6923600.0, 0.037779],
        ["Sample04", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", np.NAN, 0.037779],
        ["Sample05", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", 37440000.0, 0.037779],
    )

    peptide_df = pd.DataFrame(
        data=leftover_peptide_protein_list,
        columns=["Sample", "Protein ID", "Sequence", "Intensity", "PEP"],
    )
    peptide_df.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)
    return peptide_df


@pytest.fixture
def filtered_peptides_list():
    return ["AAQSTAMNR"]


@pytest.fixture
def peptides_df():
    df = pd.DataFrame(
        (
            ["Sample1", "Protein1", "SEQA", 1000000, 0.00001],
            ["Sample1", "Protein2", "SEQB", 2000000, 0.00002],
            ["Sample1", "Protein2", "SEQC", 3000000, 0.00003],
            ["Sample1", "Protein2", "SEQD", 4000000, 0.00004],
            ["Sample1", "Protein3", "SEQE", 5000000, 0.00005],
            ["Sample1", "Protein3", "SEQF", 6000000, 0.00006],
            ["Sample1", "Protein3", "SEQG", 7000000, 0.00007],
            ["Sample1", "Protein4", "SEQH", 8000000, 0.00008],
            ["Sample1", "Protein5", "SEQI", 9000000, 0.00009],
            ["Sample2", "Protein1", "SEQJ", 10000000, 0.0001],
            ["Sample2", "Protein2", "SEQK", 11000000, 0.00011],
            ["Sample2", "Protein3", "SEQL", 12000000, 0.00012],
            ["Sample2", "Protein4", "SEQM", 13000000, 0.00013],
            ["Sample2", "Protein5", "SEQN", 14000000, 0.00014],
            ["Sample3", "Protein1", "SEQO", 15000000, 0.00015],
            ["Sample3", "Protein2", "SEQP", 16000000, 0.00016],
            ["Sample3", "Protein3", "SEQQ", 17000000, 0.00017],
            ["Sample3", "Protein4", "SEQR", 18000000, 0.00018],
            ["Sample3", "Protein5", "SEQS", 19000000, 0.00019],
            ["Sample4", "Protein1", "SEQT", 20000000, 0.0002],
            ["Sample4", "Protein2", "SEQU", 21000000, 0.00021],
            ["Sample4", "Protein3", "SEQV", 22000000, 0.00022],
            ["Sample4", "Protein4", "SEQW", 23000000, 0.00023],
        ),
        columns=["Sample", "Protein ID", "Sequence", "Intensity", "PEP"],
    )

    return df


def assert_peptide_filtering_matches_protein_filtering(
    result_protein_df: pd.DataFrame,
    initial_peptide_df: pd.DataFrame,
    result_peptide_df: pd.DataFrame,
    filtered_attribue: str,
) -> bool:
    if initial_peptide_df is None:
        assert (
            result_peptide_df is None
        ), "Output peptide dataframe should be None, if no input peptide dataframe is provided"
    else:
        assert (
            result_peptide_df is not None
        ), "Peptide dataframe should not be None, if an input peptide dataframe is provided"
        assert (
            result_peptide_df[filtered_attribue]
            .isin(result_protein_df[filtered_attribue])
            .all()
        ), f"Peptide dataframe should not contain any {filtered_attribue} that were filtered out"
        assert (
            initial_peptide_df[
                initial_peptide_df[filtered_attribue].isin(
                    result_protein_df[filtered_attribue]
                )
            ]
            .isin(result_peptide_df)
            .all()
            .all()
        ), f"Peptide dataframe should contain all entry's on {filtered_attribue} that are in the filtered dataframe"
    return True


def test_pep_filter(show_figures, leftover_peptide_df, filtered_peptides_list):
    import_outputs = peptide_import.peptide_import(
        file_path=f"{TEST_DATA_PATH}/peptides/peptides-vsmall.txt",
        intensity_name="Intensity",
        map_to_uniprot=False,
    )

    method_inputs = {
        "peptide_df": import_outputs["peptide_df"],
        "threshold": 0.0014,
    }
    method_outputs = by_pep_value(**method_inputs)

    fig = by_pep_value_plot(method_inputs, method_outputs, "Pie chart")[0]
    if show_figures:
        fig.show()

    pd.testing.assert_frame_equal(method_outputs["peptide_df"], leftover_peptide_df)
    assert method_outputs["filtered_peptides"] == filtered_peptides_list
