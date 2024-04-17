from protzilla.data_analysis.differential_expression_t_test import t_test
from protzilla.steps import Step, StepManager, Plots


class DataAnalysisStep(Step):
    section = "data_analysis"

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs


class PlotStep(DataAnalysisStep):
    step = "plot"

    def handle_outputs(self, output_dict: dict):
        plots = output_dict.pop("plots", [])
        self.plots = Plots(plots)


class DifferentialExpression_TTest(DataAnalysisStep):
    display_name = "t-test"
    operation = "differential_expression"
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

    def method(self, inputs: dict) -> dict:
        return t_test(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["intensity_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs

    def plot(self, inputs):
        raise NotImplementedError("Plotting is not implemented yet for this step.")
