from pathlib import Path

import pandas as pd


def max_quant_import(_, file_path, intensity_name):
    assert intensity_name in ["Intensity", "iBAQ", "LFQ intensity"]
    assert Path(file_path).is_file()
    selected_columns = ["Protein IDs", "Gene names"]
    read = pd.read_csv(
        file_path,
        sep="\t",
        low_memory=False,
        na_values=["", 0],
        keep_default_na=True,
    )
    df = read.drop(columns=["Intensity", "iBAQ", "iBAQ peptides"])
    id_df = df[selected_columns]
    intensity_df = df.filter(regex=f"^{intensity_name} ", axis=1)
    intensity_df.columns = [c[len(intensity_name) + 1 :] for c in intensity_df.columns]
    molten = pd.melt(
        pd.concat([id_df, intensity_df], axis=1),
        id_vars=selected_columns,
        var_name="Sample",
        value_name=intensity_name,
    )
    molten = molten.rename(columns={"Protein IDs": "Protein ID", "Gene names": "Gene"})
    ordered = molten[["Sample", "Protein ID", "Gene", intensity_name]]
    ordered.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)
    return ordered, {}


def ms_fragger_import(_, file_path, intensity_name):
    # iBAQ doesn't exist inmas fragger
    assert intensity_name in ["Intensity", "iBAQ", "LFQ intensity"]
    assert Path(file_path).is_file()
    selected_columns = ["Protein ID", "Gene"]
    df = pd.read_csv(
        file_path,
        sep="\t",
        low_memory=False,
        na_values=["", 0],
        keep_default_na=True,
    )
    id_df = df[selected_columns]
    intensity_df = df.filter(regex=f"{intensity_name}$", axis=1)
    # TODO: which Intensity in the dataframe matches the intensity name "Intensity"?
    #  and what is the differnce between total, unique... intensity?
    intensity_df.columns = [c[: -len(intensity_name) + 1] for c in intensity_df.columns]
    molten = pd.melt(
        pd.concat([id_df, intensity_df], axis=1),
        id_vars=selected_columns,
        var_name="Sample",
        value_name=intensity_name,
    )
    ordered = molten[["Sample", "Protein ID", "Gene", intensity_name]]
    ordered.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)
    return ordered, {}
