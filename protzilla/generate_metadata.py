import numpy as np
import pandas as pd

from protzilla.importing.ms_data_import import max_quant_import

filepath = (
    "C:\\Users\\Dell\\Documents\\Übungen\\BP\\ExampleData\\MaxQuant_BA46_INSOLUBLE\\"
)

df, _ = max_quant_import(
    "",
    intensity_name="iBAQ",
    file_path=filepath + "proteinGroups.txt",
)

df = df.drop(columns=["Protein ID", "Gene", "iBAQ"])


df = df.drop_duplicates()

df["BioReplicate"] = df["Sample"].str.split("_").str[0]
df["Condition"] = df["Sample"].str.split("\d").str[0]
df["Run"] = df["Sample"]
df["IsotopeLabelType"] = "L"

# arr_values = np.append(arr_values_raw, zeros, axis=0)

arr_head = np.array(
    [["Raw.file"], ["Condition"], ["BioReplicate"], ["Run"], ["IsotopeLabelType"]]
)

arr = np.append(arr_head, df.values.transpose(), axis=1)

arr = arr.transpose()

np.savetxt(filepath + "test\\annotation.txt", arr, fmt="%s")
