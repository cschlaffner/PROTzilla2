from __future__ import annotations

from protzilla.data_preprocessing import imputation
from protzilla.steps import Step, StepManager, Plots


class DataPreprocessingStep(Step):
    section = "data_preprocessing"
    output_names = ["protein_df"]

    plot_input_names = ["protein_df"]
    plot_output_names = ["plots"]

    def insert_dataframes(self, steps: StepManager, inputs: dict) -> dict:
        inputs["protein_df"] = steps.protein_df
        return inputs

    def plot(self, inputs):
        raise NotImplementedError("Plotting is not implemented yet for this step.")


class FilterProteinsBySamplesMissing(DataPreprocessingStep):
    name = "By samples missing"
    step = "filter_proteins"
    method_description = (
        "Filter proteins based on the amount of samples with nan values"
    )

    parameter_names = ["percentage"]

    def method(self, inputs):
        return filter_proteins.by_samples_missing(**inputs)


class FilterSamplesByProteinsMissing(DataPreprocessingStep):
    name = "By proteins missing"
    step = "filter_samples"
    method_description = (
        "Filter samples based on the amount of proteins with nan values"
    )

    parameter_names = ["percentage"]

    def method(self, inputs):
        return filter_samples.by_proteins_missing(**inputs)


class OutlierDetectionByPCA(DataPreprocessingStep):
    name = "PCA"
    step = "outlier_detection"
    method_description = "Detect outliers using PCA"

    parameter_names = ["number_of_components", "threshold"]

    def method(self, kwargs):
        return outlier_detection.by_pca(**kwargs)


class OutlierDetectionByLocalOutlierFactor(DataPreprocessingStep):
    name = "LOF"
    step = "outlier_detection"
    method_description = "Detect outliers using LOF"

    parameter_names = ["number_of_neighbors", "n_jobs"]

    def method(self, inputs):
        return outlier_detection.by_lof(**inputs)


class OutlierDetectionByIsolationForest(DataPreprocessingStep):
    name = "Isolation Forest"
    step = "outlier_detection"
    method_description = "Detect outliers using Isolation Forest"

    parameter_names = ["n_estimators", "n_jobs"]

    def method(self, inputs):
        return outlier_detection.by_isolation_forest(**inputs)


class TransformationLog(DataPreprocessingStep):
    name = "Log"
    step = "transformation"
    method_description = "Transform data by log"

    parameter_names = ["log_base"]

    def method(self, inputs):
        return transformation.by_log(**inputs)


class NormalisationByZScore(DataPreprocessingStep):
    name = "Z-Score"
    step = "normalisation"
    method_description = "Normalise data by Z-Score"

    parameter_names = []

    def method(self, inputs):
        return normalisation.by_z_score(**inputs)


class NormalisationByTotalSum(DataPreprocessingStep):
    name = "Total sum"
    step = "normalisation"
    method_description = "Normalise data by total sum"

    parameter_names = []

    def method(self, inputs):
        return normalisation.by_totalsum(**inputs)


class NormalisationByMedian(DataPreprocessingStep):
    name = "Median"
    step = "normalisation"
    method_description = "Normalise data by median"

    parameter_names = ["percentile"]

    def method(self, inputs):
        return normalisation.by_median(**inputs)


class NormalisationByReferenceProtein(DataPreprocessingStep):
    name = "Reference protein"
    step = "normalisation"
    method_description = "Normalise data by reference protein"

    parameter_names = ["reference_protein"]

    def method(self, inputs):
        return normalisation.by_reference_protein(**inputs)


class ImputationByMinPerDataset(DataPreprocessingStep):
    name = "Min per dataset"
    step = "imputation"
    method_description = "Impute missing values by the minimum per dataset"

    parameter_names = ["shrinking_value"]

    def method(self, inputs):
        return imputation.by_min_per_dataset(**inputs)


class ImputationByMinPerProtein(DataPreprocessingStep):
    name = "Min per protein"
    step = "imputation"
    method_description = "Impute missing values by the minimum per protein"

    parameter_names = ["shrinking_value"]

    def method(self, inputs):
        return imputation.by_min_per_protein(**inputs)

    def plot(self, inputs):
        inputs["df"] = self.inputs["protein_df"]
        inputs["result_df"] = self.output["protein_df"]
        self.plots = Plots(imputation.by_min_per_protein_plot(**inputs))


class ImputationByMinPerSample(DataPreprocessingStep):
    name = "Min per sample"
    step = "imputation"
    method_description = "Impute missing values by the minimum per sample"

    parameter_names = ["shrinking_value"]

    def method(self, inputs):
        return by_min_per_protein(**inputs)
