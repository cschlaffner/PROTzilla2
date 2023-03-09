from ..data_preprocessing import filter_proteins, filter_samples, normalisation


method_map = {
    (
        "data-preprocessing",
        "filter-proteins",
        "low-frequency-filter",
    ): filter_proteins.by_low_frequency,
    (
        "data-preprocessing",
        "filter-proteins",
        "protein-intensity-sum-filter",
    ): filter_samples.by_protein_intensity_sum,
}

# reverse_map = {v: k for k, v in method_map.items()}


plot_map = {
    (
        "data-preprocessing",
        "filter-proteins",
        "low-frequency-filter",
        "graph-type"
    ): filter_proteins.by_low_frequency_plot,
    (
        "data_preprocessing",
        "normalisation",
        "median",
    ): normalisation.by_median,
}