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


def test_pep_filter(show_figures, leftover_peptide_df, filtered_peptides_list):
    import_outputs = peptide_import.peptide_import(
        file_path=f"{TEST_DATA_PATH}/peptides-vsmall.txt",
        intensity_name="Intensity",
    )

    method_inputs = {
        "protein_df": None,
        "peptide_df": import_outputs["peptide_df"],
        "threshold": 0.0014,
    }
    method_outputs = by_pep_value(**method_inputs)

    fig = by_pep_value_plot(method_inputs, method_outputs, "Pie chart")[0]
    if show_figures:
        fig.show()

    pd.testing.assert_frame_equal(method_outputs["peptide_df"], leftover_peptide_df)
    assert method_outputs["filtered_peptides"] == filtered_peptides_list
