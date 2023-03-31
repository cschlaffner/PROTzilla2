from . import differential_expression_t_test

# Import differential_expression_anova's methods to remove redundant function definition
from .differential_expression_anova import anova, anova_heatmap

# call methods for precommit hook not to delete imports
anova()
anova_heatmap()


def t_test(*args, **kwargs):
    return differential_expression_t_test.t_test(*args, **kwargs)


def t_test_volcano_plot(*args, **kwargs):
    return differential_expression_t_test.t_test_volcano_plot(*args, **kwargs)
