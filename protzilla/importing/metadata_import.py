import os

import pandas as pd
from django.contrib import messages

from protzilla.constants.paths import PROJECT_PATH
from protzilla.utilities import random_string


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
        meta_df.to_csv(file_path, index=False)
        return metadata_import_method(df, file_path, "Columns")

    elif file_path.startswith(
        f"{PROJECT_PATH}/tests/protzilla/importing/conversion_tmp_"
    ):
        os.remove(file_path)

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
