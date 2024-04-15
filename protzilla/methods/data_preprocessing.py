from __future__ import annotations

import pandas as pd

from protzilla.data_preprocessing.imputation import by_min_per_protein
from protzilla.steps import Step, StepManager


class DataPreprocessingStep(Step):
    section = "data_preprocessing"
    output_names = ["protein_df"]

    def get_input_dataframe(self, steps: StepManager):
        return steps.protein_df


class FilterProteinsBySamplesMissing(DataPreprocessingStep):
    name = "By samples missing"
    step = "filter_proteins"
    method_id = "by_samples_missing"
    method_description = (
        "Filter proteins based on the amount of samples with nan values"
    )

    parameter_names = ["percentage"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return filter_proteins.by_samples_missing(dataframe, **kwargs)


class FilterSamplesByProteinsMissing(DataPreprocessingStep):
    name = "By proteins missing"
    step = "filter_samples"
    method_id = "by_proteins_missing"
    method_description = (
        "Filter samples based on the amount of proteins with nan values"
    )

    parameter_names = ["percentage"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return filter_samples.by_proteins_missing(dataframe, **kwargs)


class OutlierDetectionByPCA(DataPreprocessingStep):
    name = "PCA"
    step = "outlier_detection"
    method_id = "by_pca"
    method_description = "Detect outliers using PCA"

    parameter_names = ["number_of_components", "threshold"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return outlier_detection.by_pca(dataframe, **kwargs)


class OutlierDetectionByLocalOutlierFactor(DataPreprocessingStep):
    name = "LOF"
    step = "outlier_detection"
    method_id = "by_lof"
    method_description = "Detect outliers using LOF"

    parameter_names = ["number_of_neighbors", "n_jobs"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return outlier_detection.by_lof(dataframe, **kwargs)


class OutlierDetectionByIsolationForest(DataPreprocessingStep):
    name = "Isolation Forest"
    step = "outlier_detection"
    method_id = "by_isolation_forest"
    method_description = "Detect outliers using Isolation Forest"

    parameter_names = ["n_estimators", "n_jobs"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return outlier_detection.by_isolation_forest(dataframe, **kwargs)


class TransformationLog(DataPreprocessingStep):
    name = "Log"
    step = "transformation"
    method_id = "by_log"
    method_description = "Transform data by log"

    parameter_names = ["log_base"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return transformation.by_log(dataframe, **kwargs)


class NormalisationByZScore(DataPreprocessingStep):
    name = "Z-Score"
    step = "normalisation"
    method_id = "by_z_score"
    method_description = "Normalise data by Z-Score"

    parameter_names = []

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return normalisation.by_z_score(dataframe, **kwargs)


class NormalisationByTotalSum(DataPreprocessingStep):
    name = "Total sum"
    step = "normalisation"
    method_id = "by_total_sum"
    method_description = "Normalise data by total sum"

    parameter_names = []

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return normalisation.by_totalsum(dataframe, **kwargs)


class NormalisationByMedian(DataPreprocessingStep):
    name = "Median"
    step = "normalisation"
    method_id = "by_median"
    method_description = "Normalise data by median"

    parameter_names = ["percentile"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return normalisation.by_median(dataframe, **kwargs)


class NormalisationByReferenceProtein(DataPreprocessingStep):
    name = "Reference protein"
    step = "normalisation"
    method_id = "by_reference_protein"
    method_description = "Normalise data by reference protein"

    parameter_names = ["reference_protein"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return normalisation.by_reference_protein(dataframe, **kwargs)


class ImputationByMinPerDataset(DataPreprocessingStep):
    name = "Min per dataset"
    step = "imputation"
    method_id = "by_min_per_dataset"
    method_description = "Impute missing values by the minimum per dataset"

    parameter_names = ["shrinking_value"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return imputation.by_min_per_dataset(dataframe, **kwargs)


class ImputationByMinPerProtein(DataPreprocessingStep):
    name = "Min per protein"
    step = "imputation"
    method_id = "by_min_per_protein"
    method_description = "Impute missing values by the minimum per protein"

    parameter_names = ["shrinking_value"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return imputation.by_min_per_protein(dataframe, **kwargs)


class ImputationByMinPerSample(DataPreprocessingStep):
    name = "Min per sample"
    step = "imputation"
    method_id = "by_min_per_sample"
    method_description = "Impute missing values by the minimum per sample"

    parameter_names = ["shrinking_value"]

    def method(self, dataframe: pd.DataFrame, **kwargs):
        return by_min_per_protein(dataframe, **kwargs)