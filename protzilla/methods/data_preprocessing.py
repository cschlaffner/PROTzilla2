from __future__ import annotations

from protzilla.data_preprocessing.imputation import by_min_per_protein
from protzilla.steps import Step, StepManager


class DataPreprocessingStep(Step):
    section = "data_preprocessing"

    def get_input_dataframe(self, steps: StepManager, kwargs) -> dict | None:
        kwargs["protein_df"] = steps.protein_df
        return kwargs


class ImputationMinPerProtein(DataPreprocessingStep):
    name = "Min per dataset"
    step = "imputation"
    method_id = "by_min_per_protein"
    method_description = "Impute missing values by the minimum per protein"

    parameter_names = ["shrinking_value"]
    output_names = ["intensity_df"]

    def method(self, **kwargs):
        return by_min_per_protein(**kwargs)

    def plot(self, **kwargs):
        raise NotImplementedError("Plotting is not implemented yet for this step.")
