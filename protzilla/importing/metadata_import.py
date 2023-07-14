import os

import pandas as pd
from django.contrib import messages

from protzilla.constants.paths import PROJECT_PATH
from protzilla.utilities import random_string
from protzilla.utilities.async_tasks import async_to_csv, write_to_csv


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
    elif file_path == "":
        msg = "The file upload is empty. Please select a metadata file."
        return df, dict(
            meta_df=None,
            messages=[dict(level=messages.ERROR, msg=msg)],
        )
    else:
        msg = "File format not supported. \
        Supported file formats are csv, xlsx, psv or tsv"
        return df, dict(
            meta_df=None,
            messages=[dict(level=messages.ERROR, msg=msg)],
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
        write_to_csv(meta_df, file_path, index=False)
        return metadata_import_method(df, file_path, "Columns")

    elif file_path.startswith(
        f"{PROJECT_PATH}/tests/protzilla/importing/conversion_tmp_"
    ):
        os.remove(file_path)

    return df, {"metadata": meta_df}
