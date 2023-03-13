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
}



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
}
