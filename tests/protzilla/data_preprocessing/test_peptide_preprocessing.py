import pandas as pd
import pytest

from protzilla.constants.paths import TEST_DATA_PATH
from protzilla.data_preprocessing.peptide_filter import by_pep_value, by_pep_value_plot
from protzilla.importing import peptide_import


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

