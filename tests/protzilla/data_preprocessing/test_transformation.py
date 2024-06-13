import numpy as np
import pandas as pd
import pytest

from protzilla.data_preprocessing.transformation import by_log, by_log_plot


@pytest.fixture
def log2_transformation_df():
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 2],
        ["Sample1", "Protein2", "Gene2", 4],
        ["Sample1", "Protein3", "Gene3", 8],
        ["Sample1", "Protein4", "Gene4", 16],
        ["Sample2", "Protein1", "Gene1", 4],
        ["Sample2", "Protein2", "Gene2", np.nan],
        ["Sample2", "Protein3", "Gene3", 4],
        ["Sample2", "Protein4", "Gene4", 4],
        ["Sample3", "Protein1", "Gene1", 8],
        ["Sample3", "Protein2", "Gene2", 8],
        ["Sample3", "Protein3", "Gene3", 8],
        ["Sample3", "Protein4", "Gene4", 8],
        ["Sample4", "Protein1", "Gene1", 1024],
        ["Sample4", "Protein2", "Gene2", 1024],
        ["Sample4", "Protein3", "Gene3", 1024],
        ["Sample4", "Protein4", "Gene4", 1024],
    )
    return pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )


@pytest.fixture
def log2_transformation_expected_df():
    assertion_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 1.0],
        ["Sample1", "Protein2", "Gene2", 2.0],
        ["Sample1", "Protein3", "Gene3", 3.0],
        ["Sample1", "Protein4", "Gene4", 4.0],
        ["Sample2", "Protein1", "Gene1", 2.0],
        ["Sample2", "Protein2", "Gene2", np.nan],
        ["Sample2", "Protein3", "Gene3", 2.0],
        ["Sample2", "Protein4", "Gene4", 2.0],
        ["Sample3", "Protein1", "Gene1", 3.0],
        ["Sample3", "Protein2", "Gene2", 3.0],
        ["Sample3", "Protein3", "Gene3", 3.0],
        ["Sample3", "Protein4", "Gene4", 3.0],
        ["Sample4", "Protein1", "Gene1", 10.0],
        ["Sample4", "Protein2", "Gene2", 10.0],
        ["Sample4", "Protein3", "Gene3", 10.0],
        ["Sample4", "Protein4", "Gene4", 10.0],
    )
    return pd.DataFrame(
        data=assertion_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )


@pytest.fixture
def log10_transformation_df():
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 1],
        ["Sample1", "Protein2", "Gene2", 10],
        ["Sample1", "Protein3", "Gene3", 100],
        ["Sample1", "Protein4", "Gene4", 1000],
        ["Sample2", "Protein1", "Gene1", np.nan],
        ["Sample2", "Protein2", "Gene2", 100],
        ["Sample2", "Protein3", "Gene3", 100],
        ["Sample2", "Protein4", "Gene4", 100],
        ["Sample3", "Protein1", "Gene1", 10000],
        ["Sample3", "Protein2", "Gene2", 10000],
        ["Sample3", "Protein3", "Gene3", 10000],
        ["Sample3", "Protein4", "Gene4", 10000],
        ["Sample4", "Protein1", "Gene1", 100000],
        ["Sample4", "Protein2", "Gene2", 100000],
        ["Sample4", "Protein3", "Gene3", 100000],
        ["Sample4", "Protein4", "Gene4", 100000],
    )
    return pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )


@pytest.fixture
def log10_transformation_expected_df():
    assertion_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 0.0],
        ["Sample1", "Protein2", "Gene2", 1.0],
        ["Sample1", "Protein3", "Gene3", 2.0],
        ["Sample1", "Protein4", "Gene4", 3.0],
        ["Sample2", "Protein1", "Gene1", np.nan],
        ["Sample2", "Protein2", "Gene2", 2.0],
        ["Sample2", "Protein3", "Gene3", 2.0],
        ["Sample2", "Protein4", "Gene4", 2.0],
        ["Sample3", "Protein1", "Gene1", 4.0],
        ["Sample3", "Protein2", "Gene2", 4.0],
        ["Sample3", "Protein3", "Gene3", 4.0],
        ["Sample3", "Protein4", "Gene4", 4.0],
        ["Sample4", "Protein1", "Gene1", 5.0],
        ["Sample4", "Protein2", "Gene2", 5.0],
        ["Sample4", "Protein3", "Gene3", 5.0],
        ["Sample4", "Protein4", "Gene4", 5.0],
    )
    return pd.DataFrame(
        data=assertion_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )


@pytest.fixture
def log2_transformation_expected_peptide_intensities():
    return pd.Series(
        [
            19.93157,
            20.93157,
            21.51653,
            21.93157,
            22.25350,
            22.51653,
            22.73892,
            22.93157,
            23.10149,
            23.25350,
            23.39100,
            23.51653,
            23.63201,
            23.73892,
            23.83846,
            23.93157,
            24.01903,
            24.10149,
            24.17950,
            24.25350,
            24.32389,
            24.39100,
            24.45513,
        ]
    )


@pytest.fixture
def log10_transformation_expected_peptide_intensities():
    return pd.Series(
        [
            6.00000,
            6.30103,
            6.47712,
            6.60206,
            6.69897,
            6.77815,
            6.84510,
            6.90309,
            6.95424,
            7.00000,
            7.04139,
            7.07918,
            7.11394,
            7.14613,
            7.17609,
            7.20412,
            7.23045,
            7.25527,
            7.27875,
            7.30103,
            7.32222,
            7.34242,
            7.36173,
        ]
    )


def test_log2_transformation(
    show_figures,
    log2_transformation_df,
    log2_transformation_expected_df,
    peptides_df,
    log2_transformation_expected_peptide_intensities,
):
    method_inputs = {
        "protein_df": log2_transformation_df,
        "peptide_df": peptides_df,
        "log_base": "log2",
    }
    method_outputs = by_log(**method_inputs)

    fig = by_log_plot(method_inputs, method_outputs, "Boxplot", "Protein ID")[0]
    if show_figures:
        fig.show()

    result_df = method_outputs["protein_df"]
    assert result_df.equals(
        log2_transformation_expected_df
    ), f"The results of the transformation: {result_df} \
            are not equal to the expected result: {log2_transformation_expected_df}"

    assert np.allclose(
        method_outputs["peptide_df"]["Intensity"],
        log2_transformation_expected_peptide_intensities,
        rtol=1e-02,  # Relative tolerance
        atol=1e-04,  # Absolute tolerance
    )


def test_log10_transformation(
    show_figures,
    log10_transformation_df,
    log10_transformation_expected_df,
    peptides_df,
    log10_transformation_expected_peptide_intensities,
):
    method_inputs = {
        "protein_df": log10_transformation_df,
        "peptide_df": peptides_df,
        "log_base": "log10",
    }
    method_output = by_log(**method_inputs)

    fig = by_log_plot(
        method_inputs,
        method_output,
        "Boxplot",
        "Protein ID",
    )[0]
    if show_figures:
        fig.show()

    result_df = method_output["protein_df"]
    assert result_df.equals(
        log10_transformation_expected_df
    ), f"The results of the transformation: {result_df} \
            are not equal to the expected result: {log10_transformation_expected_df}"

    assert np.allclose(
        method_output["peptide_df"]["Intensity"],
        log10_transformation_expected_peptide_intensities,
        rtol=1e-02,  # Relative tolerance
        atol=1e-04,  # Absolute tolerance
    )


@pytest.mark.parametrize("log_base", ["log2", "log10"])
def test_by_log_without_peptide_df(log2_transformation_df, log_base):
    method_outputs = by_log(log2_transformation_df, None, log_base=log_base)

    assert (
        method_outputs["peptide_df"] is None
    ), "The peptide DataFrame should be None, if no input peptide DataFrame is given."


def test_log_by_0_transformation():
    # TODO 41 test expected behaviour when 0 occurs in df
    df = pd.DataFrame(
        data=(["Sample1", "Protein1", "Gene1", 0.0],),
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    by_log(df, None, log_base="log2")
