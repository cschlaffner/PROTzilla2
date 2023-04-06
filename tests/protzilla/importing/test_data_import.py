from protzilla.constants.paths import PROJECT_PATH
from protzilla.importing import ms_data_import


def test_ms_quant_importer():
    ms_data_import.ms_fragger_import(
        _=None,
        file_path=f"{PROJECT_PATH}/tests/ms_fragger.tsv",
        intensity_name="Intensity",
    )
