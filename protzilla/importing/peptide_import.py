from pathlib import Path


def peptide_import(_, file_path, intensity_name):
    assert intensity_name in ["Intensity", "LFQ intensity"]
    assert Path(file_path).is_file()
