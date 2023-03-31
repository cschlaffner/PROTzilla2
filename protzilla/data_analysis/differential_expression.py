from . import differential_expression_anova, differential_expression_t_test


def anova(*args, **kwargs):
    return differential_expression_anova.anova(*args, **kwargs)


def t_test(*args, **kwargs):
    return differential_expression_t_test.t_test(*args, **kwargs)


def t_test_volcano_plot(*args, **kwargs):
    return differential_expression_t_test.t_test_volcano_plot(*args, **kwargs)
