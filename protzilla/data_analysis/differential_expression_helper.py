import logging
import math

from statsmodels.stats.multitest import multipletests


def apply_multiple_testing_correction(
    p_values: list, method: str, alpha: float
) -> tuple:
    """
    Applies a multiple testing correction method to a list of p-values
    using a given alpha.
    :param p_values: list of p-values to be corrected
    :param method: the multiple testing correction method to be used.\
        Can be either "Bonferroni" or "Benjamini-Hochberg"
    :param alpha: the alpha value to be used for the correction
    :return: a tuple containing the corrected p-values and (depending on the correction method)\
          either the input alpha value or the corrected alpha value
    """
    assert method in [
        "Bonferroni",
        "Benjamini-Hochberg",
    ], "Invalid multiple testing correction method"
    assert all(
        isinstance(i, (int, float)) and not math.isnan(i) and i is not None
        for i in p_values
    ), "List contains non-number or NaN values"
    assert 0 <= alpha <= 1, "Alpha value must be between 0 and 1"

    to_param = {"Bonferroni": "bonferroni", "Benjamini-Hochberg": "fdr_bh"}
    correction = multipletests(pvals=p_values, alpha=alpha, method=to_param[method])
    assert all(
        isinstance(i, (int, float)) and not math.isnan(i) and i is not None
        for i in correction[1]
    ), "Corrected p-Values contain non-number or NaN values, indicating an unfiltered\
     dataset / incorrect imputation"
    # for Bonferroni: alpha values are changed, p-values stay the same
    # for Benjamin-Hochberg: alpha values stay the same, p-values are changed
    if method == "Bonferroni":
        return p_values, correction[3]
    return correction[1], alpha


def _map_log_base(log_base: str) -> int | None:
    log_base_mapping = {"log2": 2, "log10": 10, "None": None}
    return log_base_mapping.get(log_base, None)


INVALID_PROTEINGROUP_DATA_MSG = {
    "level": logging.WARNING,
    "msg": "Due do missing or identical values, the p-values for some protein groups could not be calculated. These groups were omitted from the analysis. "
    "To prevent this, please add filtering and imputation steps to your workflow before running the analysis.",
}
