# Import differential_expression_anova's methods to remove redundant function definition
from .differential_expression_anova import anova
from .differential_expression_t_test import t_test


# call methods for precommit hook not to delete imports
def unused():
    anova(**{})
    t_test(**{})
