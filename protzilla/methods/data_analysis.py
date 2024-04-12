from protzilla.steps import Step, StepManager


class DataAnalysis(Step):
    section = "data_analysis"

    def get_input_dataframe(self, steps: StepManager):
        return steps.preprocessed_output
