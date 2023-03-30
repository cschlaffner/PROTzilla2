from . import differential_expression_anova, differential_expression_t_test


def anova(**kwargs):
    differential_expression_anova.anova(kwargs)


def t_test(**kwargs):
    differential_expression_t_test.t_test(kwargs)


def t_test_volcano_plot(**kwargs):
    differential_expression_t_test.t_test_volcano_plot(kwargs)
