import base64
import io
import operator
import os
from itertools import groupby
from random import choices
from string import ascii_letters

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
