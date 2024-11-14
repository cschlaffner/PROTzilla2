from enum import StrEnum

from protzilla.constants.ms_constants import DataKeys
from ui.runs.forms.fill_helper import enclose_links_in_html


def format_citation(model_name):
    model_info = PredictionModelMetadata[model_name]
    citation_string = (
        f"{model_name}</b>:<br>"
        f'{enclose_links_in_html(model_info.get("citation", ""))}<br>'
        f'{enclose_links_in_html(model_info.get("doi", ""))}<br>'
        f'{enclose_links_in_html(model_info["github_url"]) if model_info.get("github_url") else ""}<br>'
    )
    return citation_string


def calculate_peptide_mass(peptide_mz: float, charge: int) -> float:
    proton_mass = 1.007276466812
    return (peptide_mz * charge) - (proton_mass * charge)


class GenericTextKeys(StrEnum):
    """These are the column names that are used in the generic text format"""

    PEPTIDE_SEQUENCE = "StrippedSequence"
    PRECURSOR_CHARGE = "PrecursorCharge"
    PEPTIDE_MZ = "PrecursorMz"
    MZ = "FragmentMz"
    INTENSITY = "RelativeFragmentIntensity"
    FRAGMENT_TYPE = "FragmentType"
    FRAGMENT_NUMBER = "FragmentNumber"
    FRAGMENT_CHARGE = "FragmentCharge"


class GenericTextSeparator(StrEnum):
    """These are the column separators that are used in the generic text format"""

    COMMA = ";"
    SEMICOLON = ","
    TAB = "\t"


CSV_COLUMNS = [
    GenericTextKeys.PEPTIDE_SEQUENCE,
    GenericTextKeys.PEPTIDE_MZ,
    GenericTextKeys.PRECURSOR_CHARGE,
    GenericTextKeys.MZ,
    GenericTextKeys.INTENSITY,
    GenericTextKeys.FRAGMENT_TYPE,
    GenericTextKeys.FRAGMENT_NUMBER,
]


class OutputKeys(StrEnum):
    """These are the keys that are that are returned from the API"""

    MZ_VALUES = "mz"
    INTENSITY_VALUES = "intensities"
    ANNOTATIONS = "annotation"
    FRAGMENT_TYPE = "fragment_type"
    FRAGMENT_CHARGE = "fragment_charge"


class PredictionModels(StrEnum):
    """The different spectrum prediction models that are supported."""

    PROSITINTENSITYHCD = "PrositIntensityHCD"
    PROSITINTENSITYCID = "PrositIntensityCID"
    PROSITINTENSITYTIMSTOF = "PrositIntensityTimsTOF"
    PROSITINTENSITYTMT = "PrositIntensityTMT"
    UNISPEC = "UniSpec"


PredictionModelMetadata = {
    PredictionModels.PROSITINTENSITYHCD: {
        "url": "https://koina.wilhelmlab.org/v2/models/Prosit_2020_intensity_HCD/infer",
        "citation": "Wilhelm, M., Zolg, D.P., Graber, M. et al.  Nat Commun 12, 3346 (2021).",
        "doi": "https://doi.org/10.1038/s41467-021-23713-9",
        "github_url": "https://github.com/kusterlab/prosit",
        "required_keys": [
            DataKeys.PEPTIDE_SEQUENCE,
            DataKeys.PRECURSOR_CHARGE,
            DataKeys.COLLISION_ENERGY,
        ],
    },
    PredictionModels.PROSITINTENSITYCID: {
        "url": "https://koina.wilhelmlab.org/v2/models/Prosit_2020_intensity_CID/infer",
        "citation": "Wilhelm, M., Zolg, D.P., Graber, M. et al. Nat Commun 12, 3346 (2021).",
        "doi": "https://doi.org/10.1038/s41467-021-23713-9",
        "github_url": "https://github.com/kusterlab/prosit",
        "required_keys": [
            DataKeys.PEPTIDE_SEQUENCE,
            DataKeys.PRECURSOR_CHARGE,
        ],
    },  # mean 0.306 median 0.382
    PredictionModels.PROSITINTENSITYTIMSTOF: {
        "url": "https://koina.wilhelmlab.org/v2/models/Prosit_2023_intensity_timsTOF/infer",
        "citation": "C., Gabriel, W., Laukens, K. et al. Nat Commun 15, 3956 (2024).",
        "doi": "https://doi.org/10.1038/s41467-024-48322-0",
        "github_url": None,
        "required_keys": [
            DataKeys.PEPTIDE_SEQUENCE,
            DataKeys.PRECURSOR_CHARGE,
            DataKeys.COLLISION_ENERGY,
        ],
    },
    PredictionModels.PROSITINTENSITYTMT: {
        "url": "https://koina.wilhelmlab.org/v2/models/Prosit_2020_intensity_TMT/infer",
        "citation": " Wassim Gabriel, Matthew The, Daniel P. Zolg, Florian P. Bayer, et al. Analytical Chemistry 2022 94 (20), 7181-7190.",
        "doi": "https://doi.org/10.1021/acs.analchem.1c05435",
        "github_url": "https://github.com/kusterlab/prosit",
        "required_keys": [
            DataKeys.PEPTIDE_SEQUENCE,
            DataKeys.PRECURSOR_CHARGE,
            DataKeys.COLLISION_ENERGY,
            DataKeys.FRAGMENTATION_TYPE,
        ],
        "preprocess_args": {"filter_ptms": False},
    },
}
formatted_citation_dict = {
    model_name: format_citation(model_name) for model_name in PredictionModelMetadata
}


class OutputFormats(StrEnum):
    """The different output formats for the spectrum predictions that are supported."""

    CSV_TSV = "csv/tsv"
    MSP = "msp"
    MGF = "mgf"


class OutputsPredictFunction(StrEnum):
    """The dictionary keys of the outputs of the predict function."""

    PREDICTED_SPECTRA = "predicted_spectra"
    PREDICTED_SPECTRA_METADATA = "predicted_spectra_metadata"
    PREDICTED_SPECTRA_PEAKS = "predicted_spectra_peaks"
