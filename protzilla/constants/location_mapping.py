from ..data_analysis import differential_expression, plots
from ..data_preprocessing import (
    filter_proteins,
    filter_samples,
    imputation,
    normalisation,
    outlier_detection,
    transformation,
)
from ..importing import metadata_import, ms_data_import

"""
In this data structure, a method is associated with a location. The location is
determined by the section, step, and method keys found in the workflow_meta 
file that correspond to the method.
"""
method_map = {
    (
        "data_analysis",
        "differential_expression",
        "test_named",
    ): lambda df, **kwargs: print("warning: not implemented")
    or (df, {}),
    (
        "importing",
        "ms_data_import",
        "max_quant_import",
    ): ms_data_import.max_quant_import,
    (
        "importing",
        "ms_data_import",
        "ms_fragger_import",
    ): ms_data_import.ms_fragger_import,
    (
        "importing",
        "metadata_import",
        "metadata_import_method",
    ): metadata_import.metadata_import_method,
    (
        "data_preprocessing",
        "filter_proteins",
        "low_frequency_filter",
    ): filter_proteins.by_low_frequency,
    (
        "data_preprocessing",
        "filter_samples",
        "protein_intensity_sum_filter",
    ): filter_samples.by_protein_intensity_sum,
    (
        "data_preprocessing",
        "filter_samples",
        "protein_count_filter",
    ): filter_samples.by_protein_count,
    (
        "data_preprocessing",
        "outlier_detection",
        "pca",
    ): outlier_detection.by_pca,
    (
        "data_preprocessing",
        "outlier_detection",
        "isolation_forest",
    ): outlier_detection.by_isolation_forest,
    (
        "data_preprocessing",
        "outlier_detection",
        "local_outlier_factor",
    ): outlier_detection.by_local_outlier_factor,
    (
        "data_preprocessing",
        "transformation",
        "log_transformation",
    ): transformation.by_log,
    (
        "data_preprocessing",
        "normalisation",
        "z_score",
    ): normalisation.by_z_score,
    (
        "data_preprocessing",
        "normalisation",
        "totalsum",
    ): normalisation.by_totalsum,
    (
        "data_preprocessing",
        "normalisation",
        "median",
    ): normalisation.by_median,
    (
        "data_preprocessing",
        "normalisation",
        "ref_protein",
    ): normalisation.by_reference_protein,
    (
        "data_preprocessing",
        "imputation",
        "knn",
    ): imputation.by_knn,
    (
        "data_preprocessing",
        "imputation",
        "simple_imputation_per_protein",
    ): imputation.by_simple_imputer,
    (
        "data_preprocessing",
        "imputation",
        "min_value_per_sample",
    ): imputation.by_min_per_sample,
    (
        "data_preprocessing",
        "imputation",
        "min_value_per_protein",
    ): imputation.by_min_per_protein,
    (
        "data_preprocessing",
        "imputation",
        "min_value_per_dataset",
    ): imputation.by_min_per_dataset,
    (
        "data_analysis",
        "differential_expression",
        "anova",
    ): differential_expression.anova,
    (
        "data_analysis",
        "differential_expression",
        "t_test",
    ): differential_expression.t_test,
}

# reversed mapping of method callable and location
location_map = {v: k for k, v in method_map.items()}

"""
In this data structure, a plot for a given method is associated with a 
location. The location is determined by the section, step, and method keys 
found in the workflow_meta file that correspond to the method.
"""
plot_map = {
    (
        "data_preprocessing",
        "filter_proteins",
        "low_frequency_filter",
    ): filter_proteins.by_low_frequency_plot,
    (
        "data_preprocessing",
        "filter_samples",
        "protein_intensity_sum_filter",
    ): filter_samples.by_protein_intensity_sum_plot,
    (
        "data_preprocessing",
        "filter_samples",
        "protein_count_filter",
    ): filter_samples.by_protein_count_plot,
    (
        "data_preprocessing",
        "normalisation",
        "z_score",
    ): normalisation.by_z_score_plot,
    (
        "data_preprocessing",
        "normalisation",
        "median",
    ): normalisation.by_median_plot,
    (
        "data_preprocessing",
        "normalisation",
        "totalsum",
    ): normalisation.by_totalsum_plot,
    (
        "data_preprocessing",
        "normalisation",
        "ref_protein",
    ): normalisation.by_reference_protein_plot,
    (
        "data_preprocessing",
        "transformation",
        "log_transformation",
    ): transformation.by_log_plot,
    (
        "data_preprocessing",
        "imputation",
        "knn",
    ): imputation.by_knn_plot,
    (
        "data_preprocessing",
        "imputation",
        "simple_imputation_per_protein",
    ): imputation.by_simple_imputer_plot,
    (
        "data_preprocessing",
        "imputation",
        "min_value_per_sample",
    ): imputation.by_min_per_sample_plot,
    (
        "data_preprocessing",
        "imputation",
        "min_value_per_protein",
    ): imputation.by_min_per_protein_plot,
    (
        "data_preprocessing",
        "imputation",
        "min_value_per_dataset",
    ): imputation.by_min_per_dataset_plot,
    (
        "data_preprocessing",
        "outlier_detection",
        "pca",
    ): outlier_detection.by_pca_plot,
    (
        "data_preprocessing",
        "outlier_detection",
        "local_outlier_factor",
    ): outlier_detection.by_local_outlier_factor_plot,
    (
        "data_preprocessing",
        "outlier_detection",
        "isolation_forest",
    ): outlier_detection.by_isolation_forest_plot,
    (
        "data_analysis",
        "plot",
        "volcano",
    ): plots.create_volcano_plot,
}