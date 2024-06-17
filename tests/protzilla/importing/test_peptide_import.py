import logging

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

    peptide_df["Intensity"] = intensity_name_to_intensities[intensity_name]
    peptide_df = peptide_df[["Sample", "Protein ID", "Sequence", "Intensity", "PEP"]]
    peptide_df.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)

    return peptide_df


def evidence_df(intensity_name):
    # sample, protein id, sequence, intensity, pep
    peptide_protein_list = (
        [
            "AD01_C1_INSOLUBLE_02",
            "P36578",
            "AAAAAAALQAK",
            1362600,
            "Unmodified",
            "_AAAAAAALQAK_",
            None,
            0.05224,
            "AD01_BA39-Cohort1_INSOLUBLE_02",
        ],
        [
            "AD06_C1_INSOLUBLE_01",
            "P36578",
            "AAAAAAALQAK",
            5739600,
            "Unmodified",
            "_AAAAAAALQAK_",
            None,
            0.01578,
            "AD06_BA39-Cohort1_INSOLUBLE_01",
        ],
        [
            "CTR17_C2_INSOLUBLE_01",
            "O75822;O75822-2;O75822-3",
            "AAAAAAAGDSDSWDADAFSVEDPVRK",
            13249000,
            "Acetyl (Protein N-term)",
            "_(Acetyl (Protein N-term))AAAAAAAGDSDSWDADAFSVEDPVRK_",
            1.00000,
            0.00000,
            "CTR17_BA39-Cohort2_INSOLUBLE_01",
        ],
    )

    peptide_df = pd.DataFrame(
        data=peptide_protein_list,
        columns=[
            "Sample",
            "Protein ID",
            "Sequence",
            intensity_name,
            "Modifications",
            "Modified sequence",
            "Missed cleavages",
            "PEP",
            "Raw file",
        ],
    )

    peptide_df.sort_values(
        by=["Sample", "Protein ID", "Sequence", "Modifications"],
        ignore_index=True,
        inplace=True,
    )

    return peptide_df


@pytest.mark.parametrize("intensity_name", ["LFQ intensity", "Intensity"])
def test_peptide_import(intensity_name):
    outputs = peptide_import.peptide_import(
        file_path=f"{TEST_DATA_PATH}/peptides/peptides-vsmall.txt",
        intensity_name=intensity_name,
        map_to_uniprot=False,
    )

    if "messages" in outputs and outputs["messages"]:
        for message in outputs["messages"]:
            if message["level"] == logging.ERROR:
                assert False, message["msg"]

    pd.testing.assert_frame_equal(
        outputs["peptide_df"], peptide_df(intensity_name), check_dtype=False
    )


def test_peptide_import_ibaq():
    outputs = peptide_import.peptide_import(
        file_path=f"{TEST_DATA_PATH}/peptides/peptides-vsmall.txt",
        intensity_name="iBAQ",
        map_to_uniprot=False,
    )

    pd.testing.assert_frame_equal(
        outputs["peptide_df"], peptide_df("LFQ intensity"), check_dtype=False
    )


@pytest.mark.parametrize("intensity_name", ["Intensity"])
def test_evidence_import(intensity_name):
    outputs = peptide_import.evidence_import(
        file_path=f"{TEST_DATA_PATH}/peptides/evidence-vsmall.txt",
        intensity_name=intensity_name,
        map_to_uniprot=False,
    )

    if "messages" in outputs and outputs["messages"]:
        for message in outputs["messages"]:
            if message["level"] == logging.ERROR:
                assert False, message["msg"]

    assert np.allclose(
        outputs["peptide_df"]["PEP"],
        evidence_df(intensity_name)["PEP"],
        rtol=1e-02,  # Relative tolerance
        atol=1e-04,  # Absolute tolerance
    )

    pd.testing.assert_frame_equal(
        outputs["peptide_df"].drop(columns=["PEP"]),
        evidence_df(intensity_name).drop(columns=["PEP"]),
        check_dtype=False,
    )
