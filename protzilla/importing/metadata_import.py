import os

import pandas as pd
from django.contrib import messages
from pandas import DataFrame

from protzilla.constants.paths import PROJECT_PATH
from protzilla.utilities import random_string


def file_importer(file_path: str) -> (DataFrame, str):
    """
    Imports a file based on its file extension and returns a pandas DataFrame or None if the file format is not
    supported / the file doesn't exist.
    """
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
        return None, "The file upload is empty. Please select a metadata file."
    else:
        return (
            None,
            "File format not supported. \
        Supported file formats are csv, xlsx, psv or tsv",
        )
    return meta_df, dict()


def metadata_import_method(df: pd.DataFrame, file_path: str, feature_orientation: str):
    meta_df, msg = file_importer(file_path)
    if meta_df is None:
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
        meta_df.to_csv(file_path, index=False)
        return metadata_import_method(df, file_path, "Columns")

    elif file_path.startswith(
        f"{PROJECT_PATH}/tests/protzilla/importing/conversion_tmp_"
    ):
        os.remove(file_path)
    if "replicate" in meta_df.columns:
        # this indicates a DIANN metadata file with replicate information, we now want to calculate the median across
        # all MS runs for a sample then instead of having intensities for each MS run in our dataframe, we
        # have intensities for each sample
        # note that up until now, "Sample" in the intensity df referred to the ms run
        res = pd.merge(
            df,
            meta_df[["MS run", "sample name"]],
            left_on="Sample",
            right_on="MS run",
            how="left",
        )
        res.groupby(["Protein ID", "sample name"], as_index=False).median()

    return df, {"metadata": meta_df}


def metadata_import_method_diann(df, file_path, groupby_sample=False):
    meta_df, msg = file_importer(file_path)
    if meta_df is None:
        return df, dict(
            meta_df=None,
            messages=[dict(level=messages.ERROR, msg=msg)],
        )
    if file_path.startswith(
        f"{PROJECT_PATH}/tests/protzilla/importing/conversion_tmp_"
    ):
        os.remove(file_path)

    # this indicates a DIANN metadata file with replicate information, we now want to calculate the median across
    # all MS runs for a sample then instead of having intensities for each MS run in our dataframe, we
    # have intensities for each sample
    # note that up until now, "Sample" in the intensity df referred to the ms run
    if groupby_sample:
        res = pd.merge(
            df,
            meta_df[["MS run", "sample name"]],
            left_on="Sample",
            right_on="MS run",
            how="left",
        )
        res = res.groupby(["Protein ID", "sample name"], as_index=False).median()
        res.rename(columns={"sample name": "Sample"}, inplace=True)
        return res, {"metadata": meta_df}

    return df, {"metadata": meta_df}
