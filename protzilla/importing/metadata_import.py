import os

import pandas as pd

from protzilla.constants.paths import PROJECT_PATH
from protzilla.utilities.random import random_string


def metadata_import_method(df, file_path, feature_orientation):
    if file_path.endswith(".csv"):
        meta_df = pd.read_csv(
            file_path,
            sep=",",
            low_memory=False,
            na_values=[""],
            keep_default_na=True,
            skipinitialspace=True,
        )
    elif file_path.endswith(".xlsx"):
        meta_df = pd.read_excel(file_path)
    elif file_path.endswith(".psv"):
        meta_df = pd.read_csv(file_path, sep="|", low_memory=False)
    elif file_path.endswith(".tsv"):
        meta_df = pd.read_csv(file_path, sep="\t", low_memory=False)
    else:
        raise TypeError(
            "File format not supported. \
        Supported file formats are csv, xlsx, psv or tsv"
        )

    # always return metadata in the same orientation (features as columns)
    # as the dtype get lost when transposing, we save the df to disk after
    # changing the format and read it again as "Columns"-oriented
    if feature_orientation.startswith("Rows"):
        meta_df = meta_df.transpose()
        meta_df.reset_index(inplace=True)
        meta_df.rename(columns=meta_df.iloc[0], inplace=True)
        meta_df.drop(index=0, inplace=True)
        meta_df.index = meta_df.index - 1

        file_path = f"{PROJECT_PATH}/tests/protzilla/importing/conversion_tmp_{random_string()}.csv"
        print(file_path)
        meta_df.to_csv(file_path, index=False)
        return metadata_import_method(df, file_path, "Columns")

    elif file_path.startswith(
        f"{PROJECT_PATH}/tests/protzilla/importing/conversion_tmp_"
    ):
        os.remove(file_path)

    return df, {"metadata": meta_df}
