from statsmodels.stats.multitest import multipletests


def apply_multiple_testing_correction(p_values: list, method: str, alpha: float):
    """
        Applies a multiple testing correction method to a list of p-values
        using a given alpha.
        :param p_values: list of p-values to be corrected
        :type p_values: list
        :param method: the multiple testing correction method to be used.\
            Can be either "Bonferroni" or "Benjamini-Hochberg"
        :type method: str
        :param alpha: the alpha value to be used for the correction
        :type alpha: float
        :return: a tuple containing the corrected p-values and the\
            corrected alpha value (if applicable)
        :rtype: tuple
        """
    to_param = {"Bonferroni": "bonferroni", "Benjamini-Hochberg": "fdr_bh"}
    correction = multipletests(pvals=p_values, alpha=alpha, method=to_param[method])
    if method == "Bonferroni":
        return correction[1], correction[3]
    return correction[1], None
