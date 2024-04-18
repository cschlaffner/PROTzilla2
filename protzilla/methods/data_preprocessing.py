from __future__ import annotations

import pandas as pd

from protzilla.data_preprocessing import filter_samples, outlier_detection, transformation, normalisation, imputation, \
    filter_proteins, imputation, peptide_filter

from protzilla.steps import Step, StepManager


class DataPreprocessingStep(Step):
    section = "data_preprocessing"
    output_names = ["protein_df"]

    def insert_dataframes(self, steps: StepManager, inputs: dict) -> dict:
        inputs["protein_df"] = steps.protein_df
        return inputs


class FilterProteinsBySamplesMissing(DataPreprocessingStep):
    name = "By samples missing"
    step = "filter_proteins"
    method_description = (
        "Filter proteins based on the amount of samples with nan values"
    )

    parameter_names = ["percentage"]

    def method(self, inputs):
        return filter_proteins.by_samples_missing(**inputs)


class FilterByProteinsCount(DataPreprocessingStep):
    name = "Protein Count"
    step = "filter_samples"
    method_description = "Filter by protein count per sample"

    parameter_names = ["deviation_threshold"]

    def method(self, inputs):
        return filter_samples.protein_count_filter(**inputs)


class FilterSamplesByProteinsMissing(DataPreprocessingStep):
    name = "By proteins missing"
    step = "filter_samples"
    method_description = (
        "Filter samples based on the amount of proteins with nan values"
    )

    parameter_names = ["percentage"]

    def method(self, inputs):
        return filter_samples.by_proteins_missing(**inputs)


class FilterSamplesByProteinIntensitiesSum(DataPreprocessingStep):
    name = "Sum of intensities"
    step = "filter_samples"
    method_description = (
        "Filter by sum of protein intensities per sample"
    )

    parameter_names = ["deviation_threshold"]

    def method(self, inputs):
        return filter_samples.by_protein_intensity_sum(inputs)


class OutlierDetectionByPCA(DataPreprocessingStep):
    name = "PCA"
    step = "outlier_detection"
    method_description = "Detect outliers using PCA"

    parameter_names = ["number_of_components", "threshold"]

    def method(self, inputs):
        return outlier_detection.by_pca(**inputs)


class OutlierDetectionByLocalOutlierFactor(DataPreprocessingStep):
    name = "LOF"
    step = "outlier_detection"
    method_description = "Detect outliers using LOF"

    parameter_names = ["number_of_neighbors"]

    def method(self, inputs):
        return outlier_detection.by_lof(**inputs)


class OutlierDetectionByIsolationForest(DataPreprocessingStep):
    name = "Isolation Forest"
    step = "outlier_detection"
    method_description = "Detect outliers using Isolation Forest"

    parameter_names = ["n_estimators"]

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


class ImputationByMinPerSample(DataPreprocessingStep):
    name = "Min per sample"
    step = "imputation"
    method_description = "Impute missing values by the minimum per sample"

    parameter_names = ["shrinking_value"]

    def method(self, inputs):
        return imputation.by_min_per_protein(**inputs)


class SimpleImputationPerProtein(DataPreprocessingStep):
    name = "SimpleImputer"
    step = "imputation"
    method_description = "Imputation methods include imputation by mean, median and mode. Implements the " \
                         "sklearn.SimpleImputer class"

    parameter_names = ["strategy"]

    def method(self, inputs):
        return imputation.by_simple_imputer(**inputs)


class ImputationByKNN(DataPreprocessingStep):
    name = "kNN"
    step = "imputation"
    method_description = "A function to perform value imputation based on KNN (k-nearest neighbors). Imputes missing " \
                         "values for each sample based on intensity-wise similar samples. Two samples are close if " \
                         "the features that neither is missing are close."

    parameter_names = ["number_of_neighbours"]

    def method(self, inputs):
        return imputation.by_knn(**inputs)


class ImputationByNormalDistributionSampling(DataPreprocessingStep):
    name = "Normal distribution sampling"
    step = "imputation"
    method_description = "Imputation methods include normal distribution sampling per protein or per dataset"

    parameter_names = ["strategy", "down_shift", "scaling_factor"]

    def method(self, inputs):
        return imputation.by_normal_distribution_sampling(**inputs)


class FilterPeptidesByPEPThreshold(DataPreprocessingStep):
    name = "PEP threshold"
    step = "filter_peptides"
    method_description = "Filter by PEP-threshold"

    parameter_names = ["threshold", "peptide_df"]

    def method(self, inputs):
        return peptide_filter.by_pep_value(**inputs)
