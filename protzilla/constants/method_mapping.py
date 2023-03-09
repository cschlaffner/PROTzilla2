from ..importing import main_data_import
from ..data_preprocessing import filter_proteins, filter_samples, normalisation


method_map = {
    (
        "importing",
        "main-data-import",
        "ms-data-import",
    ): main_data_import.max_quant_import,
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
    ): filter_proteins.by_low_frequency_plot,
    (
        "data_preprocessing",
        "normalisation",
        "median",
    ): normalisation.by_median,
}