from __future__ import annotations

import pandas as pd

from protzilla.data_preprocessing.imputation import by_min_per_protein
from protzilla.steps import Step, StepManager


class DataPreprocessingStep(Step):
    section = "data_preprocessing"

    def get_input_dataframe(self, steps: StepManager):
        return steps.protein_df


class ImputationMinPerProtein(DataPreprocessingStep):
    name = "Min per dataset"
    step = "imputation"
    method_id = "by_min_per_protein"
    method_description = "Impute missing values by the minimum per protein"

    parameter_names = ["shrinking_value"]
    output_names = ["intensity_df"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return by_min_per_protein(dataframe, **kwargs)

    def get_input_dataframe(self, steps: StepManager):
        return steps.protein_df
