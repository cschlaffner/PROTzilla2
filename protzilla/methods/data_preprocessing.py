from __future__ import annotations

import logging
import traceback

from protzilla.data_preprocessing import imputation
from protzilla.steps import Plots, Step, StepManager
from protzilla.utilities import format_trace


class DataPreprocessingStep(Step):
    section = "data_preprocessing"
    output_keys = ["protein_df"]

    plot_input_names = ["protein_df"]
    plot_output_names = ["plots"]

    def insert_dataframes(self, steps: StepManager, inputs: dict) -> dict:
        inputs["protein_df"] = steps.protein_df
        return inputs

    def plot(self, inputs: dict):
        inputs = self.insert_dataframes_for_plot(inputs)
        try:
            self.plots = Plots(self.plot_method(inputs))
        except Exception as e:
            self.messages.append(
                dict(
                    level=logging.ERROR,
                    msg=(
                        f"An error occurred while plotting this step: {e.__class__.__name__} {e} "
                        f"Please check your parameters or report a potential programming issue."
                    ),
                    trace=format_trace(traceback.format_exception(e)),
                )
            )

    def insert_dataframes_for_plot(self, inputs: dict) -> dict:
        return inputs

    def plot_method(self, inputs):
        raise NotImplementedError("Plot method not implemented for this step")


class FilterProteinsBySamplesMissing(DataPreprocessingStep):
    display_name = "By samples missing"
    operation = "filter_proteins"
    method_description = (
        "Filter proteins based on the amount of samples with nan values"
    )

    input_keys = ["percentage"]

    def method(self, inputs):
        return filter_proteins.by_samples_missing(**inputs)


class FilterSamplesByProteinsMissing(DataPreprocessingStep):
    display_name = "By proteins missing"
    operation = "filter_samples"
    method_description = (
        "Filter samples based on the amount of proteins with nan values"
    )

    input_keys = ["percentage"]

    def method(self, inputs):
        return filter_samples.by_proteins_missing(**inputs)


class OutlierDetectionByPCA(DataPreprocessingStep):
    display_name = "PCA"
    operation = "outlier_detection"
    method_description = "Detect outliers using PCA"

    input_keys = ["number_of_components", "threshold"]

    def method(self, kwargs):
        return outlier_detection.by_pca(**kwargs)


class OutlierDetectionByLocalOutlierFactor(DataPreprocessingStep):
    display_name = "LOF"
    operation = "outlier_detection"
    method_description = "Detect outliers using LOF"

    input_keys = ["number_of_neighbors", "n_jobs"]

    def method(self, inputs):
        return outlier_detection.by_lof(**inputs)


class OutlierDetectionByIsolationForest(DataPreprocessingStep):
    display_name = "Isolation Forest"
    operation = "outlier_detection"
    method_description = "Detect outliers using Isolation Forest"

    input_keys = ["n_estimators", "n_jobs"]

    def method(self, inputs):
        return outlier_detection.by_isolation_forest(**inputs)


class TransformationLog(DataPreprocessingStep):
    display_name = "Log"
    operation = "transformation"
    method_description = "Transform data by log"

    input_keys = ["log_base"]

    def method(self, inputs):
        return transformation.by_log(**inputs)


class NormalisationByZScore(DataPreprocessingStep):
    display_name = "Z-Score"
    operation = "normalisation"
    method_description = "Normalise data by Z-Score"

    input_keys = []

    def method(self, inputs):
        return normalisation.by_z_score(**inputs)


class NormalisationByTotalSum(DataPreprocessingStep):
    display_name = "Total sum"
    operation = "normalisation"
    method_description = "Normalise data by total sum"

    input_keys = []

    def method(self, inputs):
        return normalisation.by_totalsum(**inputs)


class NormalisationByMedian(DataPreprocessingStep):
    display_name = "Median"
    operation = "normalisation"
    method_description = "Normalise data by median"

    input_keys = ["percentile"]

    def method(self, inputs):
        return normalisation.by_median(**inputs)


class NormalisationByReferenceProtein(DataPreprocessingStep):
    display_name = "Reference protein"
    operation = "normalisation"
    method_description = "Normalise data by reference protein"

    input_keys = ["reference_protein"]

    def method(self, inputs):
        return normalisation.by_reference_protein(**inputs)


class ImputationByMinPerDataset(DataPreprocessingStep):
    display_name = "Min per dataset"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per dataset"

    input_keys = ["shrinking_value"]

    def method(self, inputs):
        return imputation.by_min_per_dataset(**inputs)


class ImputationByMinPerProtein(DataPreprocessingStep):
    display_name = "Min per protein"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per protein"

    input_keys = ["shrinking_value", "protein_df"]

    def method(self, inputs):
        return imputation.by_min_per_protein(**inputs)

    def insert_dataframes_for_plot(self, inputs: dict) -> dict:
        inputs["df"] = self.inputs["protein_df"]
        inputs["result_df"] = self.output["protein_df"]
        return inputs

    def plot_method(self, inputs):
        return imputation.by_min_per_protein_plot(**inputs)


class ImputationByMinPerSample(DataPreprocessingStep):
    display_name = "Min per sample"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per sample"

    input_keys = ["shrinking_value"]

    def method(self, inputs):
        return by_min_per_protein(**inputs)
