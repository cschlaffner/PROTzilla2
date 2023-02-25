from ..data_preprocessing import filter_proteins, filter_samples


method_map = {
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
}
