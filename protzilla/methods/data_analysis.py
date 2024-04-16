from protzilla.data_analysis.differential_expression_t_test import t_test
from protzilla.steps import Step, StepManager


class DataAnalysisStep(Step):
    section = "data_analysis"

    def get_input_dataframe(self, steps: StepManager, **kwargs) -> dict | None:
        return kwargs


class DifferentialExpression_TTest(DataAnalysisStep):
    name = "t-test"
    step = "differential_expression"
    method_description = (
        "A function to conduct a two sample t-test between groups defined in the clinical data. The "
        "t-test is conducted on the level of each protein. The p-values are corrected for multiple "
        "testing. The fold change is calculated by group2/group1."
    )

    parameter_names = [
        "ttest_type",
        "intensity_df",
        "multiple_testing_correction",
        "alpha",
        "log_base",
        "grouping",
        "group1",
        "group2",
        "metadata_df",
    ]
    output_names = ["intensity_df"]

    def method(self, **kwargs):
        return t_test(**kwargs)

    def get_input_dataframe(self, steps: StepManager, kwargs) -> dict | None:
        kwargs["intensity_df"] = steps.protein_df
        kwargs["metadata_df"] = steps.metadata_df
        return kwargs

    def plot(self, **kwargs):
        raise NotImplementedError("Plotting is not implemented yet for this step.")
