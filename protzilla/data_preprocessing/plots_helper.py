import numpy as np
import math


def generate_log_tics(min, max):
    temp = math.floor(np.log10(max - min) / 2)
    step_size = pow(10, temp)
    first_step = math.ceil(min / step_size) * step_size
    last_step = math.ceil(max / step_size) * step_size + 3 * step_size
    tickvals = np.arange(first_step, last_step, step_size)
    ticktext = np.vectorize(lambda x: millify(pow(10, x)))(tickvals)
    return dict(
        tickmode='array',
        tickvals=tickvals,
        ticktext=ticktext,
    )
def generate_lin_tics(min, max):
    temp = math.floor(np.log10(max - min) / 2)
    step_size = pow(10, temp)
    first_step = math.ceil(min / step_size) * step_size
    last_step = math.ceil(max / step_size) * step_size + 3 * step_size
    tickvals = np.arange(first_step, last_step, step_size)
    ticktext = np.vectorize(lambda x: millify(x))(tickvals)
    return dict(
        tickmode='array',
        tickvals=tickvals,
        ticktext=ticktext,
    )


def millify(n):
    millnames = ['', 'K', 'M', 'B', 'T', 'Q', 'Q', 'S', 'S', 'O', 'N']
    n = float(n)
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return '{:.0f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])
