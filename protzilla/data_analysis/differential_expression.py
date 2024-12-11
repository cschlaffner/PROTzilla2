# Import differential_expression_anova's methods to remove redundant function definition
from .differential_expression_anova import anova
from .differential_expression_linear_model import linear_model
from .differential_expression_t_test import t_test
from .differential_expression_mann_whitney import mann_whitney_test_on_intensity_data, mann_whitney_test_on_ptm_data
from .differential_expression_kruskal_wallis import kruskal_wallis_test_on_intensity_data, kruskal_wallis_test_on_ptm_data



# call methods for precommit hook not to delete imports
def unused():
    anova(**{})
    t_test(**{})
    linear_model(**{})
    mann_whitney_test_on_ptm_data(**{})
    mann_whitney_test_on_intensity_data(**{})
    kruskal_wallis_test_on_intensity_data(**{})
    kruskal_wallis_test_on_ptm_data(**{})
