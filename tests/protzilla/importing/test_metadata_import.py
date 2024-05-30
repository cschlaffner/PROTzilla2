import pandas as pd

from protzilla.constants.paths import PROJECT_PATH
from protzilla.methods.importing import (
    DiannImport,
    MetadataColumnAssignment,
    MetadataImport,
    MetadataImportMethodDiann,
)
from protzilla.steps import Step


def test_metadata_import(run_imported):
    run_imported.step_add(MetadataImport())
    run_imported.step_next()
    run_imported.step_calculate(
        {
            "file_path": f"{PROJECT_PATH}/tests/metadata_cut_columns.csv",
            "feature_orientation": "Columns (samples in rows, features in columns)",
        }
    )
    test_metadata = pd.read_csv(f"{PROJECT_PATH}/tests/metadata_cut_columns.csv")
    pd.testing.assert_frame_equal(
        test_metadata, run_imported.current_outputs["metadata_df"]
    )


def test_metadata_import_diann(run_empty):
    run_empty.step_add(DiannImport())
    run_empty.step_calculate(
        {
            "file_path": f"{PROJECT_PATH}/tests/test_data/DIANN_data/20230605 24h prodi DMSO report.pg_matrix.tsv",
            "map_to_uniprot": "False",
        }
    )
    assert (
        run_empty.current_outputs["protein_df"] is not None
    ), "DIA-NN MS data import failed."
    assert not run_empty.current_outputs[
        "protein_df"
    ].empty, "DIA-NN MS data import failed."
    run_empty.step_add(MetadataImportMethodDiann())
    run_empty.step_next()
    run_empty.step_calculate(
        {
            "file_path": f"{PROJECT_PATH}/tests/test_data/DIANN_data/sample run relationship.xlsx",
            "groupby_sample": True,
        }
    )
    test_metadata = pd.read_csv(
        f"{PROJECT_PATH}/tests/test_data/DIANN_data/correct_metadata_table.csv"
    )
    test_protein_df = pd.read_csv(
        f"{PROJECT_PATH}/tests/test_data/DIANN_data/correct_protein_df.csv"
    )
    pd.testing.assert_frame_equal(
        test_metadata, run_empty.current_outputs["metadata_df"]
    )
    pd.testing.assert_frame_equal(
        test_protein_df, run_empty.steps.get_step_output(DiannImport, "protein_df")
    )


def test_metadata_orientation(run_empty):
    run_empty.step_add(MetadataImport())
    run_empty.step_next()
    run_empty.step_calculate(
        {
            "file_path": f"{PROJECT_PATH}/tests/metadata_cut_columns.csv",
            "feature_orientation": "Columns (samples in rows, features in columns)",
        }
    )
    metadata_df_a = run_empty.current_outputs["metadata_df"]
    run_empty.step_calculate(
        {
            "file_path": f"{PROJECT_PATH}/tests/metadata_cut_rows.csv",
            "feature_orientation": "Rows (samples in columns, features in rows)",
        }
    )
    metadata_df_b = run_empty.current_outputs["metadata_df"]
    assert metadata_df_a.shape == metadata_df_b.shape
    assert metadata_df_a.columns.tolist() == metadata_df_b.columns.tolist()
    assert metadata_df_a.equals(metadata_df_b)


def test_metadata_column_assignment(run_empty):
    run_empty.step_add(MetadataImport())
    run_empty.step_next()
    run_empty.step_calculate(
        {
            "file_path": f"{PROJECT_PATH}/tests/metadata_cut_columns.csv",
            "feature_orientation": "Columns (samples in rows, features in columns)",
        }
    )
    assert (
        run_empty.current_outputs["metadata_df"] is not None
        and not run_empty.current_outputs["metadata_df"].empty
    )
    assert "Sample" in run_empty.current_outputs["metadata_df"].columns
    run_empty.step_add(MetadataColumnAssignment())
    run_empty.step_next()
    run_empty.step_calculate(
        {
            "metadata_required_column": "Sample_renamed",
            "metadata_unknown_column": "Sample",
        }
    )
    assert (
        "Sample_renamed"
        in run_empty.steps.get_step_output(
            Step, "metadata_df", include_current_step=True
        ).columns
    )

    run_empty.step_calculate(
        {
            "metadata_required_column": "Sample",
            "metadata_unknown_column": "Sample_renamed",
        }
    )
    assert (
        "Sample"
        in run_empty.steps.get_step_output(
            Step, "metadata_df", include_current_step=True
        ).columns
    )
