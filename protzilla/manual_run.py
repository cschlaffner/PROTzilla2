from protzilla.data_analysis.differential_expression_anova import anova
from protzilla.data_analysis.differential_expression_t_test import t_test
from protzilla.data_preprocessing.filter_proteins import by_low_frequency
from protzilla.data_preprocessing.filter_samples import by_protein_intensity_sum, by_protein_count
from protzilla.data_preprocessing.imputation import by_knn, by_simple_imputer, by_min_per_sample, by_min_per_protein, \
    by_min_per_dataset
from protzilla.data_preprocessing.normalisation import by_median, by_z_score, by_totalsum
from protzilla.data_preprocessing.outlier_detection import by_local_outlier_factor, by_pca, by_isolation_forest
from protzilla.data_preprocessing.transformation import by_log
from protzilla.debug_info import DebugInfo
from protzilla.importing.metadata_import import metadata_import_method
from protzilla.importing.ms_data_import import max_quant_import


def all_steps():
    DebugInfo().run_name = "test2"

    DebugInfo().measure_start("max_quant_import")
    df, _ = max_quant_import(
        "",
        intensity_name="iBAQ",
        file_path="C:\\Users\\Dell\\Documents\\Übungen\\BP\\ExampleData\\MaxQuant_BA39_INSOLUBLE\\proteinGroups.txt",
    )
    DebugInfo().measure_end("max_quant_import")
    DebugInfo().measure_memory("max_quant_import")

    DebugInfo().measure_start("metadata_import_method")
    df, metadata = metadata_import_method(
        df,
        feature_orientation="Columns (samples in rows, features in columns)",
        file_path="C:\\Users\\Dell\\Documents\\Übungen\\BP\\ExampleData\\MaxQuant_BA39_INSOLUBLE\\meta.csv",
    )
    metadata = metadata["metadata"]
    DebugInfo().measure_end("metadata_import_method")
    DebugInfo().measure_memory("metadata_import_method")

    DebugInfo().measure_start("by_low_frequency")
    df, _ = by_low_frequency(df, threshold=0.2)
    DebugInfo().measure_end("by_low_frequency")
    DebugInfo().measure_memory("by_low_frequency")

    DebugInfo().measure_start("by_protein_intensity_sum")
    df, _ = by_protein_intensity_sum(df, threshold=2)
    DebugInfo().measure_end("by_protein_intensity_sum")
    DebugInfo().measure_memory("by_protein_intensity_sum")

    DebugInfo().measure_start("by_knn")
    df, _ = by_knn(df, number_of_neighbours=10)
    DebugInfo().measure_end("by_knn")
    DebugInfo().measure_memory("by_knn")

    DebugInfo().measure_start("by_local_outlier_factor")
    df, _ = by_local_outlier_factor(df, number_of_neighbors=3)
    DebugInfo().measure_end("by_local_outlier_factor")
    DebugInfo().measure_memory("by_local_outlier_factor")

    DebugInfo().measure_start("by_log")
    df, _ = by_log(df, log_base="log2")
    DebugInfo().measure_end("by_log")
    DebugInfo().measure_memory("by_log")

    DebugInfo().measure_start("by_median")
    df, _ = by_median(df, percentile=0.4)
    DebugInfo().measure_end("by_median")
    DebugInfo().measure_memory("by_median")

    DebugInfo().measure_start("anova")
    anova_out = anova(
        df,
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
        grouping="Group",
        selected_groups=["AD", "CTR"],
        metadata_df=metadata,
    )
    DebugInfo().measure_end("anova")
    DebugInfo().measure_memory("anova")

    DebugInfo().save_print_elements()
    print(df)
    print(anova_out)


def all_methods():
    df, _ = max_quant_import(
        "",
        intensity_name="iBAQ",
        file_path="C:\\Users\\Dell\\Documents\\Übungen\\BP\\ExampleData\\MaxQuant_BA39_INSOLUBLE\\proteinGroups.txt",
    )
    df, metadata = metadata_import_method(
        df,
        feature_orientation="Columns (samples in rows, features in columns)",
        file_path="C:\\Users\\Dell\\Documents\\Übungen\\BP\\ExampleData\\MaxQuant_BA39_INSOLUBLE\\meta.csv",
    )
    metadata = metadata["metadata"]

    DebugInfo().measure_start("by_low_frequency")
    df, _ = by_low_frequency(df, threshold=0.2)
    DebugInfo().measure_end("by_low_frequency")
    DebugInfo().measure_memory("by_low_frequency")

    DebugInfo().measure_start("by_protein_intensity_sum")
    by_protein_intensity_sum(df, threshold=2)
    DebugInfo().measure_end("by_protein_intensity_sum")
    DebugInfo().measure_memory("by_protein_intensity_sum")

    DebugInfo().measure_start("by_protein_count")
    df, _ = by_protein_count(df, threshold=2)
    DebugInfo().measure_end("by_protein_count")
    DebugInfo().measure_memory("by_protein_count")

    DebugInfo().measure_start("by_min_per_dataset")
    df, _ = by_min_per_dataset(df, shrinking_value=1)
    DebugInfo().measure_end("by_min_per_dataset")
    DebugInfo().measure_memory("by_min_per_dataset")

    DebugInfo().measure_start("by_min_per_protein")
    by_min_per_protein(df, shrinking_value=1)
    DebugInfo().measure_end("by_min_per_protein")
    DebugInfo().measure_memory("by_min_per_protein")

    DebugInfo().measure_start("by_min_per_sample")
    by_min_per_sample(df, shrinking_value=1)
    DebugInfo().measure_end("by_min_per_sample")
    DebugInfo().measure_memory("by_min_per_sample")

    DebugInfo().measure_start("by_simple_imputer")
    by_simple_imputer(df, strategy="mean")
    DebugInfo().measure_end("by_simple_imputer")
    DebugInfo().measure_memory("by_simple_imputer")

    DebugInfo().measure_start("by_knn")
    by_knn(df, number_of_neighbours=10)
    DebugInfo().measure_end("by_knn")
    DebugInfo().measure_memory("by_knn")

    DebugInfo().measure_start("by_pca")
    df, _ = by_pca(df, threshold=2, number_of_components=3)
    DebugInfo().measure_end("by_pca")
    DebugInfo().measure_memory("by_pca")

    DebugInfo().measure_start("by_isolation_forest")
    by_isolation_forest(df, n_estimators=100)
    DebugInfo().measure_end("by_isolation_forest")
    DebugInfo().measure_memory("by_isolation_forest")

    DebugInfo().measure_start("by_local_outlier_factor")
    by_local_outlier_factor(df, number_of_neighbors=3)
    DebugInfo().measure_end("by_local_outlier_factor")
    DebugInfo().measure_memory("by_local_outlier_factor")

    DebugInfo().measure_start("by_log")
    df, _ = by_log(df, log_base="log2")
    DebugInfo().measure_end("by_log")
    DebugInfo().measure_memory("by_log")

    DebugInfo().measure_start("by_z_score")
    df, _ = by_z_score(df)
    DebugInfo().measure_end("by_z_score")
    DebugInfo().measure_memory("by_z_score")

    DebugInfo().measure_start("by_totalsum")
    by_totalsum(df)
    DebugInfo().measure_end("by_totalsum")
    DebugInfo().measure_memory("by_totalsum")

    DebugInfo().measure_start("by_median")
    by_median(df, percentile=0.4)
    DebugInfo().measure_end("by_median")
    DebugInfo().measure_memory("by_median")

    DebugInfo().measure_start("anova")
    anova(df, multiple_testing_correction_method="Benjamini-Hochberg", alpha=0.05, grouping="Group",
          selected_groups=['AD', 'CTR'], metadata_df=metadata)
    DebugInfo().measure_end("anova")
    DebugInfo().measure_memory("anova")

    DebugInfo().measure_start("t_test")
    t_test(df, multiple_testing_correction_method="Benjamini-Hochberg", alpha=0.05, fc_threshold=0,
           grouping="Group", group1="AD", group2="CTR", metadata_df=metadata)
    DebugInfo().measure_end("t_test")
    DebugInfo().measure_memory("t_test")


if __name__ == "__main__":
    all_methods()
