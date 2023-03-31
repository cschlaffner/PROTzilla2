# Import differential_expression_anova's methods to remove redundant function definition
from .differential_expression_anova import anova, anova_heatmap
from .differential_expression_t_test import t_test, t_test_volcano_plot


# call methods for precommit hook not to delete imports
def unused():
    anova(**{})
    anova_heatmap(**{})
    t_test(**{})
    t_test_volcano_plot(**{})
