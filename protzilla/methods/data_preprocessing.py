from __future__ import annotations

from protzilla.data_preprocessing import (
    filter_proteins,
    filter_samples,
    imputation,
    normalisation,
    outlier_detection,
    peptide_filter,
    transformation,
)
from protzilla.steps import Step, StepManager


class DataPreprocessingStep(Step):
    section = "data_preprocessing"
    output_keys = ["protein_df"]

    plot_input_names = ["protein_df"]
    plot_output_names = ["plots"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot_inputs: dict = {}

    def insert_dataframes(self, steps: StepManager, inputs: dict) -> dict:
        inputs["protein_df"] = steps.protein_df
        inputs["peptide_df"] = steps.get_step_output(Step, "peptide_df")
        return inputs


class FilterProteinsBySamplesMissing(DataPreprocessingStep):
    display_name = "By samples missing"
    operation = "filter_proteins"
    method_description = (
        "Filter proteins based on the amount of samples with nan values"
    )

    calc_method = staticmethod(filter_proteins.by_samples_missing)
    plot_method = staticmethod(filter_proteins.by_samples_missing_plot)


class FilterByProteinsCount(DataPreprocessingStep):
    display_name = "Protein Count"
    operation = "filter_samples"
    method_description = "Filter by protein count per sample"

    calc_method = staticmethod(filter_samples.by_protein_count)
    plot_method = staticmethod(filter_samples.by_protein_count_plot)


class FilterSamplesByProteinsMissing(DataPreprocessingStep):
    display_name = "By proteins missing"
    operation = "filter_samples"
    method_description = (
        "Filter samples based on the amount of proteins with nan values"
    )

    calc_method = staticmethod(filter_samples.by_proteins_missing)
    plot_method = staticmethod(filter_samples.by_proteins_missing_plot)


class FilterSamplesByProteinIntensitiesSum(DataPreprocessingStep):
    display_name = "Sum of intensities"
    operation = "filter_samples"
    method_description = "Filter by sum of protein intensities per sample"

    calc_method = staticmethod(filter_samples.by_protein_intensity_sum)
    plot_method = staticmethod(filter_samples.by_protein_intensity_sum_plot)


class OutlierDetectionByPCA(DataPreprocessingStep):
    display_name = "PCA"
    operation = "outlier_detection"
    method_description = "Detect outliers using PCA"

    calc_method = staticmethod(outlier_detection.by_pca)
    plot_method = staticmethod(outlier_detection.by_pca_plot)


class OutlierDetectionByLocalOutlierFactor(DataPreprocessingStep):
    display_name = "Local outlier factor"
    operation = "outlier_detection"
    method_description = "Detect outliers using the local outlier factor"

    calc_method = staticmethod(outlier_detection.by_local_outlier_factor)
    plot_method = staticmethod(outlier_detection.by_local_outlier_factor_plot)


class OutlierDetectionByIsolationForest(DataPreprocessingStep):
    display_name = "Isolation Forest"
    operation = "outlier_detection"
    method_description = "Detect outliers using Isolation Forest"

    calc_method = staticmethod(outlier_detection.by_isolation_forest)
    plot_method = staticmethod(outlier_detection.by_isolation_forest_plot)


class TransformationLog(DataPreprocessingStep):
    display_name = "Log"
    operation = "transformation"
    method_description = "Transform data by log"

    calc_method = staticmethod(transformation.by_log)
    plot_method = staticmethod(transformation.by_log_plot)


class NormalisationByZScore(DataPreprocessingStep):
    display_name = "Z-Score"
    operation = "normalisation"
    method_description = "Normalise data by Z-Score"

    calc_method = staticmethod(normalisation.by_z_score)
    plot_method = staticmethod(normalisation.by_z_score_plot)


class NormalisationByTotalSum(DataPreprocessingStep):
    display_name = "Total sum"
    operation = "normalisation"
    method_description = "Normalise data by total sum"

    calc_method = staticmethod(normalisation.by_totalsum)
    plot_method = staticmethod(normalisation.by_totalsum_plot)


class NormalisationByMedian(DataPreprocessingStep):
    display_name = "Median"
    operation = "normalisation"
    method_description = "Normalise data by median"

    calc_method = staticmethod(normalisation.by_median)
    plot_method = staticmethod(normalisation.by_median_plot)


class NormalisationByReferenceProtein(DataPreprocessingStep):
    display_name = "Reference protein"
    operation = "normalisation"
    method_description = "Normalise data by reference protein"

    calc_method = staticmethod(normalisation.by_reference_protein)
    plot_method = staticmethod(normalisation.by_reference_protein_plot)


class ImputationByMinPerDataset(DataPreprocessingStep):
    display_name = "Min per dataset"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per dataset"

    calc_method = staticmethod(imputation.by_min_per_dataset)
    plot_method = staticmethod(imputation.by_min_per_dataset_plot)


class ImputationByMinPerProtein(DataPreprocessingStep):
    display_name = "Min per protein"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per protein"

    calc_method = staticmethod(imputation.by_min_per_protein)
    plot_method = staticmethod(imputation.by_min_per_protein_plot)


class ImputationByMinPerSample(DataPreprocessingStep):
    display_name = "Min per sample"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per sample"

    calc_method = staticmethod(imputation.by_min_per_protein)
    plot_method = staticmethod(imputation.by_min_per_sample_plot)


class SimpleImputationPerProtein(DataPreprocessingStep):
    display_name = "SimpleImputer"
    operation = "imputation"
    method_description = (
        "Imputation methods include imputation by mean, median and mode. Implements the "
        "sklearn.SimpleImputer class"
    )

    calc_method = staticmethod(imputation.by_simple_imputer)
    plot_method = staticmethod(imputation.by_simple_imputer_plot)


class ImputationByKNN(DataPreprocessingStep):
    display_name = "kNN"
    operation = "imputation"
    method_description = (
        "A function to perform value imputation based on KNN (k-nearest neighbors). Imputes missing "
        "values for each sample based on intensity-wise similar samples. Two samples are close if "
        "the features that neither is missing are close."
    )

    calc_method = staticmethod(imputation.by_knn)
    plot_method = staticmethod(imputation.by_knn_plot)


class ImputationByNormalDistributionSampling(DataPreprocessingStep):
    display_name = "Normal distribution sampling"
    operation = "imputation"
    method_description = "Imputation methods include normal distribution sampling per protein or per dataset"

    calc_method = staticmethod(imputation.by_normal_distribution_sampling)
    plot_method = staticmethod(imputation.by_normal_distribution_sampling_plot)


class FilterPeptidesByPEPThreshold(DataPreprocessingStep):
    display_name = "PEP threshold"
    operation = "filter_peptides"
    method_description = "Filter by PEP-threshold"
    output_keys = ["protein_df", "peptide_df", "filtered_peptides"]

    calc_method = staticmethod(peptide_filter.by_pep_value)
    plot_method = staticmethod(peptide_filter.by_pep_value_plot)
