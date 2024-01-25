import logging
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from protzilla.constants.paths import PROJECT_PATH
from protzilla.importing import ms_data_import


def ms_fragger_import_intensity_df(intensity_name):
    ms_fragger_list = (
        ["DDM_0pt1_01", "A2A5R2", "Arfgef2"],
        ["DDM_0pt1_01", "A2A7S8", "Kiaa1522"],
        ["DDM_0pt1_01", "A2A863", "Itgb4"],
        ["DDM_0pt1_01", "A2AGT5", "Ckap5"],
        ["DDM_0pt1_01", "A2AJ76", "Hmcn2"],
        ["DDM_0pt1_02", "A2A5R2", "Arfgef2"],
        ["DDM_0pt1_02", "A2A7S8", "Kiaa1522"],
        ["DDM_0pt1_02", "A2A863", "Itgb4"],
        ["DDM_0pt1_02", "A2AGT5", "Ckap5"],
        ["DDM_0pt1_02", "A2AJ76", "Hmcn2"],
    )

    ms_fragger_df = pd.DataFrame(
        data=ms_fragger_list,
        columns=["Sample", "Protein ID", "Gene"],
    )

    intensities_name_to_intensity = {
        "Spectral Count": [3, 1, 18, 1, 5, 2, 4, 17, 2, 5],
        "Unique Spectral Count": [3, 1, 18, 1, 5, 2, 4, 17, 2, 5],
        "Total Spectral Count": [3, 1, 18, 1, 5, 2, 4, 17, 2, 5],
        "Intensity": [
            1.8210618e7,
            4133918.5,
            1.44354336e8,
            5645782.0,
            9055790.0,
            2.546863e7,
            7812505.5,
            1.39428224e8,
            3202878.8,
            1.9467296e7,
        ],
        "Unique Intensity": [
            1.8210618e7,
            4133918.5,
            1.44354336e8,
            5645782.0,
            9055790.0,
            2.546863e7,
            7812505.5,
            1.39428224e8,
            3202878.8,
            1.9467296e7,
        ],
        "Total Intensity": [
            1.8210618e7,
            4133918.5,
            1.44354336e8,
            5645782.0,
            9055790.0,
            2.546863e7,
            7812505.5,
            1.39428224e8,
            3202878.8,
            1.9467296e7,
        ],
        "MaxLFQ Intensity": [
            1.6028714e7,
            3406362.2,
            3.3995216e7,
            6204635.0,
            4878346.5,
            1.6216802e7,
            8536188.0,
            2.9248888e7,
            8326886.5,
            8998863.0,
        ],
        "MaxLFQ Unique Intensity": [
            1.6028714e7,
            3406362.2,
            3.3995216e7,
            6204635.0,
            4878346.5,
            1.6216802e7,
            8536188.0,
            2.9248888e7,
            8326886.5,
            8998863.0,
        ],
        "MaxLFQ Total Intensity": [
            2.826229e7,
            3406362.2,
            3.3995216e7,
            6204635.0,
            4878346.5,
            1.3986173e7,
            8536188.0,
            2.9248888e7,
            8326886.5,
            8998863.0,
        ],
    }

    ms_fragger_df[intensity_name] = intensities_name_to_intensity[intensity_name]
    ms_fragger_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True, inplace=True
    )

    return ms_fragger_df


def diann_import_intensity_df():
    diann_intensity_df = {
        "Sample": {
            0: "LM07061",
            1: "LM07061",
            2: "LM07061",
            3: "LM07061",
            4: "LM07061",
            5: "LM07062",
            6: "LM07062",
            7: "LM07062",
            8: "LM07062",
            9: "LM07062",
            10: "LM07063",
            11: "LM07063",
            12: "LM07063",
            13: "LM07063",
            14: "LM07063",
        },
        "Protein ID": {
            0: "A0A087WWU8;A0A2R2Y2Q3;A0A494C0P6;J3KN67",
            1: "A0A0B4J2A2;P0DN37",
            2: "A0A0G2JPD3;A0A140T8W8;A0A140T8Y4;A0A1W2PPF8;A0A1W2PR61;Q5SPM2",
            3: "A0A0U1RQV3",
            4: "A0A140T913;A0A140T933;A0A140T955;A0A140T9I0;A0A140T9X5;A0A1W2PPQ2;A0A1W2PRT9;Q53Z42",
            5: "A0A087WWU8;A0A2R2Y2Q3;A0A494C0P6;J3KN67",
            6: "A0A0B4J2A2;P0DN37",
            7: "A0A0G2JPD3;A0A140T8W8;A0A140T8Y4;A0A1W2PPF8;A0A1W2PR61;Q5SPM2",
            8: "A0A0U1RQV3",
            9: "A0A140T913;A0A140T933;A0A140T955;A0A140T9I0;A0A140T9X5;A0A1W2PPQ2;A0A1W2PRT9;Q53Z42",
            10: "A0A087WWU8;A0A2R2Y2Q3;A0A494C0P6;J3KN67",
            11: "A0A0B4J2A2;P0DN37",
            12: "A0A0G2JPD3;A0A140T8W8;A0A140T8Y4;A0A1W2PPF8;A0A1W2PR61;Q5SPM2",
            13: "A0A0U1RQV3",
            14: "A0A140T913;A0A140T933;A0A140T955;A0A140T9I0;A0A140T9X5;A0A1W2PPQ2;A0A1W2PRT9;Q53Z42",
        },
        "Gene": {
            0: np.nan,
            1: np.nan,
            2: np.nan,
            3: np.nan,
            4: np.nan,
            5: np.nan,
            6: np.nan,
            7: np.nan,
            8: np.nan,
            9: np.nan,
            10: np.nan,
            11: np.nan,
            12: np.nan,
            13: np.nan,
            14: np.nan,
        },
        "Intensity": {
            0: 329042.0,
            1: 138322.0,
            2: np.nan,
            3: 122984.0,
            4: 36317.0,
            5: 367477.0,
            6: 572539.0,
            7: np.nan,
            8: 59042.7,
            9: np.nan,
            10: 381325.0,
            11: 96522.7,
            12: np.nan,
            13: 72372.5,
            14: 27456.7,
        },
    }
    return pd.DataFrame(data=diann_intensity_df)


def test_max_quant_import_different_intensity_names():
    for intensity_name in ["Intensity", "iBAQ", "LFQ intensity"]:
        df, out, msg = ms_data_import.max_quant_import(
            _=None,
            file_path=f"{PROJECT_PATH}/tests/test_data/data_import/maxquant_small.tsv",
            intensity_name=intensity_name,
        )
        assert df is not None
        assert intensity_name in df.columns


def test_max_quant_import_file_not_exist():
    df, out, msg = ms_data_import.max_quant_import(
        _=None,
        file_path="non_existent_file_path",
        intensity_name="Intensity",
    )
    assert df is None
    assert msg[0]["level"] == logging.ERROR
    assert "found" in msg[0]["msg"].lower()


def test_max_quant_import_no_protein_ids_column():
    df, out, msg = ms_data_import.max_quant_import(
        _=None,
        file_path=f"{PROJECT_PATH}/tests/test_data/data_import/maxquant_small_noproteincolumn.tsv",
        intensity_name="Intensity",
    )
    assert df is None
    assert msg[0]["level"] == logging.ERROR
    assert "Protein IDs" in msg[0]["msg"]


def test_max_quant_import_invalid_data():
    df, out, msg = ms_data_import.max_quant_import(
        _=None,
        file_path=f"{PROJECT_PATH}/tests/test_data/data_import/maxquant_small_invalid.tsv",
        intensity_name="Intensity",
    )
    assert df is None
    assert msg[0]["level"] == logging.ERROR


@pytest.mark.parametrize(
    "intensity_name",
    [
        "Intensity",
        "MaxLFQ Total Intensity",
        "MaxLFQ Intensity",
        "Total Intensity",
        "MaxLFQ Unique Intensity",
        "Unique Spectral Count",
        "Unique Intensity",
        "Spectral Count",
        "Total Spectral Count",
    ],
)
def test_ms_fragger_import(intensity_name):
    test_intensity_df, _, _ = ms_data_import.ms_fragger_import(
        _=None,
        file_path=f"{PROJECT_PATH}/tests/combined_protein_method_small_cut.tsv",
        intensity_name=intensity_name,
    )

    intensity_df = ms_fragger_import_intensity_df(intensity_name)

    # we do not care about the genes column, it is never used (and replaced by nan)
    intensity_df = intensity_df.drop(columns=["Gene"])
    test_intensity_df = test_intensity_df.drop(columns=["Gene"])

    pd.testing.assert_frame_equal(test_intensity_df, intensity_df)


def test_diann_import():
    test_intensity_df, _, _ = ms_data_import.diann_import(
        _=None,
        file_path=f"{PROJECT_PATH}/tests/diann_intensities.tsv",
    )

    intensity_df = diann_import_intensity_df()

    # we do not care about the genes column, it is never used (and replaced by nan)
    intensity_df = intensity_df.drop(columns=["Gene"])
    test_intensity_df = test_intensity_df.drop(columns=["Gene"])
    pd.testing.assert_frame_equal(test_intensity_df, intensity_df)


def test_filter_rev_con():
    intensity_df, other, messages = ms_data_import.max_quant_import(
        _=None,
        file_path=PROJECT_PATH / "tests" / "proteinGroups_small_cut.txt",
        intensity_name="Intensity",
    )
    protein_ids = intensity_df["Protein ID"].unique().tolist()
    # not the complete group should be filtered out if contains valid ids
    assert "P00000" in protein_ids
    # all instances of rev and con should be filtered out
    assert all(
        not any(
            id_.startswith("CON__") or id_.startswith("REV__")
            for id_ in group.split(";")
        )
        for group in protein_ids
    )


def test_transform_and_clean():
    columns = ["Protein ID", "A", "B", "C"]
    data = [
        ["P00000", 1.0, 6.0, np.nan],
        ["P00000;REV__P12345", np.nan, 2.0, np.nan],
        ["Q11111", 4.0, 4, np.nan],
        ["Q11111;CON__P12345", 4.0, 4.0, np.nan],
    ]
    out_col = ["Sample", "Protein ID", "intensity"]
    expected_output = [
        ["A", "P00000", 1.0],  # add nan and number
        ["A", "Q11111", 4.0],
        ["B", "P00000", 8.0],  # add number and number
        ["B", "Q11111", 4.0],
        ["C", "P00000", np.nan],  # add nan only
        ["C", "Q11111", np.nan],
    ]
    df = pd.DataFrame(data, columns=columns)
    res, other, messages = ms_data_import.transform_and_clean(
        df, "intensity", map_to_uniprot=False
    )
    expected_df = pd.DataFrame(expected_output, columns=out_col)

    # we do not care about the genes column, it is deprecated (and replaced by nan)
    res = res.drop(columns=["Gene"])

    assert res.equals(expected_df)
    assert other["contaminants"] == ["Q11111;CON__P12345"]
    assert other["filtered_proteins"] == ["REV__P12345"]


def test_clean_protein_groups():
    expected = [
        "A0A009IHW8-8-7-6;M99999_7-8;P12345;Q12345-3",
        "P00000;P12345;P12345-1;P12345-11;P12345-9",
        "ENSP12345678901;NP_123456;NP_123456789;XP_123456789",
        "P12345",
        "",
    ]
    test_data = [
        "P12345;Q12345-3;A0A009IHW8-8-7-6;M99999_7-8",
        "P12345-9;P12345;P12345-1;P00000;P12345-11",
        "ENSP12345678901.1;NP_123456;XP_123456789;NP_123456789",
        "P12345_VAR_38832",
        "REV__P12345;YP_123456789;0000000;TAU-98",
    ]
    clean_groups, filtered = ms_data_import.clean_protein_groups(
        test_data, map_to_uniprot=False
    )
    assert clean_groups == expected
    assert filtered == "REV__P12345 YP_123456789 0000000 TAU-98".split()


@patch("protzilla.importing.ms_data_import.map_ids_to_uniprot")
def test_clean_protein_groups_map(ids_to_uniprot_mock):
    ids_to_uniprot_mock.return_value = {"NP_123456": ["P54321", "P12345"]}
    expected = ["P12321;P12345;P54321", ""]
    test_data = ["NP_123456;P12321", "XP_123456789"]
    clean_groups, filtered = ms_data_import.clean_protein_groups(
        test_data, map_to_uniprot=True
    )
    assert clean_groups == expected
    assert filtered == []
