from .. import data_preprocessing


method_map = {
    (
        "data_preprocessing",
        "filter_proteins",
        "by_low_frequency",
    ): data_preprocessing.filter_proteins.by_low_frequency,
    (
        "data_preprocessing",
        "filter_samples",
        "by_protein_intensity_sum",
    ): data_preprocessing.filter_samples.by_protein_intensity_sum,
}
