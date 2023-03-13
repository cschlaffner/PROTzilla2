from ..importing import main_data_import
from ..data_preprocessing import filter_proteins, filter_samples, normalisation

"""
In this data structure, a method is associated with a location. The location is
determined by the section, step, and method keys found in the workflow_meta 
file that correspond to the method.
"""
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
}
