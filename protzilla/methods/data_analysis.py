from __future__ import annotations

from protzilla.steps import Step, StepManager


class DataAnalysisStep(Step):
    section = "data_analysis"

    def get_input_dataframe(self, steps: StepManager):
        protein_df
        return NotImplementedError("This method must be implemented in a subclass.")
