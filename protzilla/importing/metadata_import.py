import os

import pandas as pd
from django.contrib import messages
from pandas import DataFrame

from protzilla.constants.paths import PROJECT_PATH
from protzilla.utilities import random_string


def file_importer(file_path: str) -> tuple[pd.DataFrame, str]:
    """
    Imports a file based on its file extension and returns a pandas DataFrame or None if the file format is not
    supported / the file doesn't exist.
    """
    try:
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
            return (
                pd.DataFrame(),
                "The file upload is empty. Please select a metadata file.",
            )
        else:
            return (
                pd.DataFrame(),
                "File format not supported. \
            Supported file formats are csv, xlsx, psv or tsv",
            )
        msg = "Metadata file successfully imported."
        return meta_df, msg
    except pd.errors.EmptyDataError:
        msg = "The file is empty."
        return pd.DataFrame(), msg


def metadata_import_method(
    df: pd.DataFrame, file_path: str, feature_orientation: str
) -> tuple[pd.DataFrame, dict]:
    """
        Imports a metadata file and returns the intensity dataframe and a dict with a message if the file import failed,
        and the metadata dataframe if the import was successful.

    returns: (DataFrame, dict)
    """
    meta_df, msg = file_importer(file_path)
    if meta_df.empty:
        return df, dict(
            metadata=None,
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

    return df, {"metadata": meta_df, "messages": [dict(level=messages.INFO, msg=msg)]}


def metadata_import_method_diann(
    df: DataFrame, file_path: str, groupby_sample: bool = False
) -> (DataFrame, dict):
    """
    This method imports a metadata file with run relationship information and returns the intensity dataframe and the
    metadata dataframe. If the import fails, it returns the unchanged dataframe and a dict with a message about the
    error.
    """
    meta_df, msg = file_importer(file_path)
    if meta_df.empty:
        return df, dict(
            metadata=None,
            messages=[dict(level=messages.ERROR, msg=msg)],
        )

    if file_path.startswith(
        f"{PROJECT_PATH}/tests/protzilla/importing/conversion_tmp_"
    ):
        os.remove(file_path)

    if groupby_sample:
        # we want to take the median of all MS runs (column "Sample" in the intensity df) for each Sample
        # (column "sample name" in the metadata df)
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


def metadata_column_assignment(
    df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    metadata_required_column: str = None,
    metadata_unknown_column: str = None,
):
    """
    This function renames a column in the metadata dataframe to the required column name.

    :param df: this is passed for consistency, but not used
    :type df: pandas DataFrame
    :param metadata_df: the metadata dataframe to be changed
    :type metadata_df: float
    :param metadata_required_column: the name of the column in the dataframe that is used for the metadata assignment
    :type metadata_df: str
    :param metadata_unknown_column: the name of the column in the metadata dataframe that is renamed to the
     required column name
    :type metadata_unknown_column: str
    :return: returns the unchanged dataframe and a dict with messages, potentially empty if no messages
    :rtype: pd.DataFrame, dict
    """

    # TODO add info box in UI explaining that no option for unknown columns means all columns are named correctly
    # check if required column already in metadata, if so give error message
    if metadata_required_column is None or metadata_unknown_column is None:
        msg = f"You can proceed, as there is nothing that needs to be changed."
        return df, dict(messages=[dict(level=messages.INFO, msg=msg)])

    if metadata_required_column in metadata_df.columns:
        msg = f"Metadata already contains column '{metadata_required_column}'. \
        Please rename the column or select another column."
        return df, dict(messages=[dict(level=messages.ERROR, msg=msg)])
    # rename given in metadata_sample_column column to "Sample" if it is called otherwise
    renamed_metadata_df = metadata_df.rename(
        columns={metadata_unknown_column: metadata_required_column}, inplace=True
    )
    return df, dict()
