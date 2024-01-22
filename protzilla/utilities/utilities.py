import base64
import io
import operator
import os
from itertools import groupby
from random import choices
from string import ascii_letters

import pandas as pd
import psutil


# recipie from https://docs.python.org/3/library/itertools.html
def unique_justseen(iterable, key=None):
    """List unique elements, preserving order. Remember only the element just seen."""
    # unique_justseen('AAAABBBCCDAABBB') --> A B C D A B
    # unique_justseen('ABBcCAD', str.lower) --> A B c A D
    return map(next, map(operator.itemgetter(1), groupby(iterable, key)))


def random_string():
    return "".join(choices(ascii_letters, k=16))


def get_memory_usage():
    memory_mb = psutil.Process(os.getpid()).memory_info().rss / 1024**2
    return f"{round(memory_mb, 1)} MB"


def clean_uniprot_id(uniprot_id):
    if "-" in uniprot_id:
        uniprot_id = uniprot_id.split("-")[0]
    if "_" in uniprot_id:
        uniprot_id = uniprot_id.split("_")[0]
    return uniprot_id


def fig_to_base64(fig):
    """
    Convert a matplotlib figure to base64. This is used to display the figure in the browser.

    :param fig: matplotlib figure
    :type fig: matplotlib.figure.Figure

    :return: base64 encoded image
    :rtype: bytes
    """
    img = io.BytesIO()
    fig.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    return base64.b64encode(img.getvalue())


def default_intensity_column(
    intensity_df: pd.DataFrame, intensity_column_name: str = None
) -> str:
    """
    Returns the default intensity column name if no column name is provided.

    :param intensity_df: The column for which to determine the intensity column name
    :param intensity_column_name: If provided, this column name is returned.
    :return:
    """

    possible_substring_identifiers = ["intensity", "ibaq", "lfq", "spectral count"]

    if intensity_column_name is not None:
        return intensity_column_name
    matched_columns = [
        col
        for col in intensity_df.columns
        if any(
            [substring in col.lower() for substring in possible_substring_identifiers]
        )
    ]
    if matched_columns:
        return matched_columns[0]

    raise ValueError(
        "No intensity column name provided and no default intensity column could be determined."
        "Please provide the intensity column name manually to the function call."
    )


def exists_message(messages, msg):
    """
    Checks if a message exists in a list of messages.

    :param messages: a list of messages
    :type messages: list
    :param msg: the message to check
    :type msg: dict

    :return: True if the message exists, False otherwise
    :rtype: bool
    """
    return any(message == msg for message in messages)
