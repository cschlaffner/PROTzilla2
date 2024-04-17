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
    display_name = "By samples missing"
    operation = "filter_proteins"
    method_description = (
        "Filter proteins based on the amount of samples with nan values"
    )

    parameter_names = ["percentage"]

    def method(self, inputs):
        return filter_proteins.by_samples_missing(**inputs)


class FilterSamplesByProteinsMissing(DataPreprocessingStep):
    display_name = "By proteins missing"
    operation = "filter_samples"
    method_description = (
        "Filter samples based on the amount of proteins with nan values"
    )

    parameter_names = ["percentage"]

    def method(self, inputs):
        return filter_samples.by_proteins_missing(**inputs)


class OutlierDetectionByPCA(DataPreprocessingStep):
    display_name = "PCA"
    operation = "outlier_detection"
    method_description = "Detect outliers using PCA"

    parameter_names = ["number_of_components", "threshold"]

    def method(self, kwargs):
        return outlier_detection.by_pca(**kwargs)


class OutlierDetectionByLocalOutlierFactor(DataPreprocessingStep):
    display_name = "LOF"
    operation = "outlier_detection"
    method_description = "Detect outliers using LOF"

    parameter_names = ["number_of_neighbors", "n_jobs"]

    def method(self, inputs):
        return outlier_detection.by_lof(**inputs)


class OutlierDetectionByIsolationForest(DataPreprocessingStep):
    display_name = "Isolation Forest"
    operation = "outlier_detection"
    method_description = "Detect outliers using Isolation Forest"

    parameter_names = ["n_estimators", "n_jobs"]

    def method(self, inputs):
        return outlier_detection.by_isolation_forest(**inputs)


class TransformationLog(DataPreprocessingStep):
    display_name = "Log"
    operation = "transformation"
    method_description = "Transform data by log"

    parameter_names = ["log_base"]

    def method(self, inputs):
        return transformation.by_log(**inputs)


class NormalisationByZScore(DataPreprocessingStep):
    display_name = "Z-Score"
    operation = "normalisation"
    method_description = "Normalise data by Z-Score"

    parameter_names = []

    def method(self, inputs):
        return normalisation.by_z_score(**inputs)


class NormalisationByTotalSum(DataPreprocessingStep):
    display_name = "Total sum"
    operation = "normalisation"
    method_description = "Normalise data by total sum"

    parameter_names = []

    def method(self, inputs):
        return normalisation.by_totalsum(**inputs)


class NormalisationByMedian(DataPreprocessingStep):
    display_name = "Median"
    operation = "normalisation"
    method_description = "Normalise data by median"

    parameter_names = ["percentile"]

    def method(self, inputs):
        return normalisation.by_median(**inputs)


class NormalisationByReferenceProtein(DataPreprocessingStep):
    display_name = "Reference protein"
    operation = "normalisation"
    method_description = "Normalise data by reference protein"

    parameter_names = ["reference_protein"]

    def method(self, inputs):
        return normalisation.by_reference_protein(**inputs)


class ImputationByMinPerDataset(DataPreprocessingStep):
    display_name = "Min per dataset"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per dataset"

    parameter_names = ["shrinking_value"]

    def method(self, inputs):
        return imputation.by_min_per_dataset(**inputs)


class ImputationByMinPerProtein(DataPreprocessingStep):
    display_name = "Min per protein"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per protein"

    parameter_names = ["shrinking_value"]

    def method(self, inputs):
        return imputation.by_min_per_protein(**inputs)

    def plot(self, inputs):
        inputs["df"] = self.inputs["protein_df"]
        inputs["result_df"] = self.output["protein_df"]
        self.plots = Plots(imputation.by_min_per_protein_plot(**inputs))


class ImputationByMinPerSample(DataPreprocessingStep):
    display_name = "Min per sample"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per sample"

    parameter_names = ["shrinking_value"]

    def method(self, inputs):
        return by_min_per_protein(**inputs)
