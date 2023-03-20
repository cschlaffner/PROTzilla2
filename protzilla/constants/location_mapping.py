from ..data_preprocessing import (
    filter_proteins,
    filter_samples,
    imputation,
    normalisation,
    transformation,
)
from ..importing import ms_data_import

"""
In this data structure, a method is associated with a location. The location is
determined by the section, step, and method keys found in the workflow_meta 
file that correspond to the method.
"""
method_map = {
    (
        "importing",
        "ms-data-import",
        "max-quant-data-import",
    ): ms_data_import.max_quant_import,
    (
        "data_preprocessing",
        "filter_proteins",
        "by_low_frequency",
    ): filter_proteins.by_low_frequency,
    (
        "data_preprocessing",
        "filter_samples",
        "by_protein_intensity_sum",
    ): filter_samples.by_protein_intensity_sum,
    (
        "data_preprocessing",
        "normalisation",
        "z-score",
    ): normalisation.by_z_score,
    (
        "data_preprocessing",
        "normalisation",
        "median",
    ): normalisation.by_median,
    (
        "data_preprocessing",
        "normalisation",
        "totalsum",
    ): normalisation.by_totalsum,
    (
        "data_preprocessing",
        "normalisation",
        "ref-protein",
    ): normalisation.by_reference_protein,
    (
        "data_preprocessing",
        "transformation",
        "log-transformation",
    ): transformation.by_log,
    (
        "data_preprocessing",
        "imputation",
        "knn",
    ): imputation.by_knn,
    (
        "data_preprocessing",
        "imputation",
        "simple-imputation-per-protein",
    ): imputation.by_simple_imputer,
    (
        "data_preprocessing",
        "imputation",
        "min-value-per-sample",
    ): imputation.by_min_per_sample,
    (
        "data_preprocessing",
        "imputation",
        "min-value-per-protein",
    ): imputation.by_min_per_protein,
    (
        "data_preprocessing",
        "imputation",
        "min-value-per-dataset",
    ): imputation.by_min_per_dataset,
}

"""
In this data structure, a plot for a given method is associated with a 
location. The location is determined by the section, step, and method keys 
found in the workflow_meta file that correspond to the method.
"""
plot_map = {
    (
        "data-preprocessing",
        "filter-proteins",
        "low-frequency-filter",
    ): filter_proteins.by_low_frequency_plot,
    (
        "data_preprocessing",
        "normalisation",
        "z-score",
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
        "ref-protein",
    ): normalisation.by_reference_protein_plot,
    (
        "data_preprocessing",
        "transformation",
        "log-transformation",
    ): transformation.by_log_plot,
    (
        "data_preprocessing",
        "imputation",
        "knn",
    ): imputation.by_knn_plot,
    (
        "data_preprocessing",
        "imputation",
        "simple-imputation-per-protein",
    ): imputation.by_simple_imputer_plot,
    (
        "data_preprocessing",
        "imputation",
        "min-value-per-sample",
    ): imputation.by_min_per_sample_plot,
    (
        "data_preprocessing",
        "imputation",
        "min-value-per-protein",
    ): imputation.by_min_per_protein_plot,
    (
        "data_preprocessing",
        "imputation",
        "min-value-per-dataset",
    ): imputation.by_min_per_dataset_plot,
}
