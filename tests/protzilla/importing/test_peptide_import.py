import numpy as np
import pandas as pd
import pytest

from protzilla.constants.paths import TEST_DATA_PATH
from protzilla.importing import peptide_import


def peptide_df(intensity_name):
    # sample, protein id, sequence, intensity, pep
    peptide_protein_list = (
        ["Sample01", "P46459;P46459-2", "AAQSTAMNR", 0.0013764],
        ["Sample02", "P46459;P46459-2", "AAQSTAMNR", 0.0013764],
        ["Sample03", "P46459;P46459-2", "AAQSTAMNR", 0.0013764],
        ["Sample04", "P46459;P46459-2", "AAQSTAMNR", 0.0013764],
        ["Sample05", "P46459;P46459-2", "AAQSTAMNR", 0.0013764],
        ["Sample01", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", 0.037779],
        ["Sample02", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", 0.037779],
        ["Sample03", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", 0.037779],
        ["Sample04", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", 0.037779],
        ["Sample05", "Q13748;Q6PEY2;Q9NY65;Q9NY65-2", "EDLAALEK", 0.037779],
    )

    peptide_df = pd.DataFrame(
        data=peptide_protein_list, columns=["Sample", "Protein ID", "Sequence", "PEP"]
    )

    intensity_name_to_intensities = {
        "LFQ intensity": [
            np.NAN,
            np.NAN,
            253840.0,
            1371200.0,
            3048300.0,
            3957900.0,
            np.NAN,
            8533900.0,
            np.NAN,
            6923600.0,
        ],
        "Intensity": [
            253840.0,
            1371200.0,
            3048300.0,
            np.NAN,
            np.NAN,
            np.NAN,
            np.NAN,
            6923600.0,
            np.NAN,
            37440000.0,
        ],
    }

    peptide_df[intensity_name] = intensity_name_to_intensities[intensity_name]
    peptide_df = peptide_df[["Sample", "Protein ID", "Sequence", intensity_name, "PEP"]]
    peptide_df.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)

    return peptide_df


@pytest.mark.parametrize("intensity_name", ["LFQ intensity", "Intensity"])
def test_peptide_import(intensity_name):
    outputs = peptide_import.peptide_import(
        file_path=f"{TEST_DATA_PATH}/peptides-vsmall.txt",
        intensity_name=intensity_name,
    )

    pd.testing.assert_frame_equal(
        outputs["peptide_df"], peptide_df(intensity_name), check_dtype=False
    )


def test_peptide_import_ibaq():
    outputs = peptide_import.peptide_import(
        file_path=f"{TEST_DATA_PATH}/peptides-vsmall.txt",
        intensity_name="iBAQ",
    )

    pd.testing.assert_frame_equal(
        outputs["peptide_df"], peptide_df("LFQ intensity"), check_dtype=False
    )
