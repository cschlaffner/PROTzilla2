import pathlib

import pandas as pd

SELECTED_COLUMNS = ["Protein IDs", "Gene names"]


def max_quant_import(_, file_path, intensity_name):
    assert intensity_name in ["Intensity", "iBAQ", "LFQ intensity"]
    assert pathlib.Path.is_file(file_path)
    read = pd.read_csv(
        file_path,
        sep="\t",
        low_memory=False,
        na_values=["", 0],
        keep_default_na=True,
    )
    df = read.drop(columns=["Intensity", "iBAQ", "iBAQ peptides"])
    id_df = df[SELECTED_COLUMNS]
    intensity_df = df.filter(regex=f"^{intensity_name} ", axis=1)
    intensity_df.columns = [c[len(intensity_name) + 1 :] for c in intensity_df.columns]
    molten = pd.melt(
        pd.concat([id_df, intensity_df], axis=1),
        id_vars=SELECTED_COLUMNS,
        var_name="Sample",
        value_name=intensity_name,
    )
    molten = molten.rename(columns={"Protein IDs": "Protein ID", "Gene names": "Gene"})
    ordered = molten[["Sample", "Protein ID", "Gene", intensity_name]]
    ordered.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)
    return ordered, {}
