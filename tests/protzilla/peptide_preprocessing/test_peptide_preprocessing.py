import numpy as np
import pandas as pd
import pytest

from protzilla.constants.paths import TEST_DATA_PATH
from protzilla.importing import peptide_import
from protzilla.peptide_preprocessing.peptide_filter import by_pep_value


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
def filtered_peptides_df():
    filtered_peptides = (
        ["Sample01", "P46459;P46459-2", "AAQSTAMNR", 253840.0, 0.0013764],
        ["Sample02", "P46459;P46459-2", "AAQSTAMNR", 1371200.0, 0.0013764],
        ["Sample03", "P46459;P46459-2", "AAQSTAMNR", 3048300.0, 0.0013764],
        ["Sample04", "P46459;P46459-2", "AAQSTAMNR", np.NAN, 0.0013764],
        ["Sample05", "P46459;P46459-2", "AAQSTAMNR", np.NAN, 0.0013764],
    )
    filtered_peptides_df = pd.DataFrame(
        data=filtered_peptides,
        columns=["Sample", "Protein ID", "Sequence", "Intensity", "PEP"],
    )
    filtered_peptides_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True, inplace=True
    )
    return filtered_peptides_df


def test_pep_filter(leftover_peptide_df, filtered_peptides_df):
    peptide_df, _ = peptide_import.peptide_import(
        _=None,
        file_path=f"{TEST_DATA_PATH}/peptides-vsmall.txt",
        intensity_name="Intensity",
    )
    threshold = 0.0014
    df, out = by_pep_value(peptide_df, threshold)

    pd.testing.assert_frame_equal(df, leftover_peptide_df)
    pd.testing.assert_frame_equal(out["filtered_peptides"], filtered_peptides_df)
