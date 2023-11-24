from ..data_analysis import (
    classification,
    clustering,
    differential_expression,
    dimension_reduction,
    model_evaluation,
    model_evaluation_plots,
    plots,
    protein_graphs,
)
from ..data_integration import database_integration, di_plots, enrichment_analysis
from ..data_preprocessing import (
    filter_proteins,
    filter_samples,
    imputation,
    normalisation,
    outlier_detection,
    peptide_filter,
    transformation,
)
from ..importing import metadata_import, ms_data_import, peptide_import

# In this data structure, a method is associated with a location. The location is
# determined by the section, step, and method keys found in the workflow_meta
# file that correspond to the method.
method_map = {
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
        "importing",
        "metadata_import",
        "metadata_column_assignment",
    ): metadata_import.metadata_column_assignment,
    ("importing", "peptide_import", "peptide_import"): peptide_import.peptide_import,
    (
        "data_preprocessing",
        "filter_proteins",
        "samples_missing_filter",
    ): filter_proteins.by_samples_missing,
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
        "filter_samples",
        "proteins_missing_filter",
    ): filter_samples.by_proteins_missing,
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
        "data_preprocessing",
        "imputation",
        "normal_distribution_sampling",
    ): imputation.by_normal_distribution_sampling,
    (
        "data_preprocessing",
        "filter_peptides",
        "pep_filter",
    ): peptide_filter.by_pep_value,
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
    (
        "data_analysis",
        "differential_expression",
        "linear_model",
    ): differential_expression.linear_model,
    (
        "data_analysis",
        "clustering",
        "k_means",
    ): clustering.k_means,
    (
        "data_analysis",
        "clustering",
        "expectation_maximisation",
    ): clustering.expectation_maximisation,
    (
        "data_analysis",
        "clustering",
        "hierarchical_agglomerative_clustering",
    ): clustering.hierarchical_agglomerative_clustering,
    (
        "data_analysis",
        "classification",
        "random_forest",
    ): classification.random_forest,
    (
        "data_analysis",
        "classification",
        "svm",
    ): classification.svm,
    (
        "data_analysis",
        "model_evaluation",
        "evaluate_classification_model",
    ): model_evaluation.evaluate_classification_model,
    (
        "data_analysis",
        "dimension_reduction",
        "t_sne",
    ): dimension_reduction.t_sne,
    (
        "data_analysis",
        "dimension_reduction",
        "umap",
    ): dimension_reduction.umap,
    (
        "data_analysis",
        "protein_graphs",
        "peptides_to_isoform",
    ): protein_graphs.peptides_to_isoform,
    (
        "data_analysis",
        "protein_graphs",
        "variation_graph",
    ): protein_graphs.variation_graph,
    (
        "data_integration",
        "enrichment_analysis",
        "GO_analysis_with_STRING",
    ): enrichment_analysis.GO_analysis_with_STRING,
    (
        "data_integration",
        "enrichment_analysis",
        "GO_analysis_with_Enrichr",
    ): enrichment_analysis.GO_analysis_with_Enrichr,
    (
        "data_integration",
        "enrichment_analysis",
        "GO_analysis_offline",
    ): enrichment_analysis.GO_analysis_offline,
    (
        "data_integration",
        "enrichment_analysis",
        "gsea",
    ): enrichment_analysis.gsea,
    (
        "data_integration",
        "enrichment_analysis",
        "gsea_preranked",
    ): enrichment_analysis.gsea_preranked,
    (
        "data_integration",
        "database_integration",
        "uniprot",
    ): database_integration.add_uniprot_data,
    (
        "data_integration",
        "database_integration",
        "gene_mapping",
    ): database_integration.gene_mapping,
}

# reversed mapping of method callable and location
location_map = {v: k for k, v in method_map.items()}


# In this data structure, a plot for a given method is associated with a
# location. The location is determined by the section, step, and method keys
# found in the workflow_meta file that correspond to the method.
plot_map = {
    (
        "data_preprocessing",
        "filter_proteins",
        "samples_missing_filter",
    ): filter_proteins.by_samples_missing_plot,
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
        "filter_samples",
        "proteins_missing_filter",
    ): filter_samples.by_proteins_missing_plot,
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
        "imputation",
        "normal_distribution_sampling",
    ): imputation.by_normal_distribution_sampling_plot,
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
        "data_preprocessing",
        "filter_peptides",
        "pep_filter",
    ): peptide_filter.by_pep_value_plot,
    (
        "data_analysis",
        "plot",
        "scatter_plot",
    ): plots.scatter_plot,
    (
        "data_analysis",
        "plot",
        "volcano",
    ): plots.create_volcano_plot,
    (
        "data_analysis",
        "plot",
        "clustergram",
    ): plots.clustergram_plot,
    (
        "data_analysis",
        "plot",
        "precision_recall_curve",
    ): model_evaluation_plots.precision_recall_curve_plot,
    (
        "data_analysis",
        "plot",
        "roc_curve",
    ): model_evaluation_plots.roc_curve_plot,
    (
        "data_integration",
        "plot",
        "GO_enrichment_bar_plot",
    ): di_plots.GO_enrichment_bar_plot,
    (
        "data_integration",
        "plot",
        "GO_enrichment_dot_plot",
    ): di_plots.GO_enrichment_dot_plot,
    (
        "data_integration",
        "plot",
        "gsea_dot_plot",
    ): di_plots.gsea_dot_plot,
    (
        "data_integration",
        "plot",
        "gsea_enrichment_plot",
    ): di_plots.gsea_enrichment_plot,
}
