from ..data_preprocessing import filter_proteins, filter_samples
from ..importing import main_data_import

method_map = {
    (
        "importing",
        "ms-data-import",
        "max-quant-data-import",
    ): main_data_import.max_quant_import,
    (
        "importing",
        "ms-data-import",
        "ms-fragger-data-import",
    ): main_data_import.ms_fragger_import,
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
