import math

import numpy as np


def generate_tics(lower_bound, upper_bound, log: bool):
    """
    Generates a dictionary, mapping equally spaced positions for labels, in the interval between min and max

    :param lower_bound: lower bound of the interval to create labels for
    :param upper_bound: upper bound of the interval to create labels for
    :param log: specifies whether the scale is logarithmic, and the labels should be pow 10
    :return: the dictionary
    """
    temp = math.floor(np.log10(upper_bound - lower_bound) / 2)
    step_size = pow(10, temp)
    first_step = math.ceil(lower_bound / step_size) * step_size
    last_step = math.ceil(upper_bound / step_size) * step_size + 3 * step_size
    tickvals = np.arange(first_step, last_step, step_size)
    if log:
        ticktext = np.vectorize(lambda x: millify(pow(10, x)))(tickvals)
    else:
        ticktext = np.vectorize(lambda x: millify(x))(tickvals)
    return dict(
        tickmode="array",
        tickvals=tickvals,
        ticktext=ticktext,
    )

def millify(n)->str:
    """
    Writes the number n in shortened style with shorthand symbol for every power of 1000

    :param n: the number to be written in shortened style
    :return: a String containing the shortened number
    """
    millnames = ["", "K", "M", "B", "T", "Q", "Q", "S", "S", "O", "N"]
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    return "{:.0f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])
