"""This file contains the constants that are re-used many times across PROTzilla, to avoid repetition and to streamline
refactoring-."""
from enum import StrEnum


class FragmentationType(StrEnum):
    """The different types of mass spectrometry fragmentation that are supported."""

    HCD = "HCD"
    CID = "CID"


class DataKeys(StrEnum):
    """Commonly used column names and keys in the dataframes."""

    PEPTIDE_SEQUENCE = "peptide_sequences"
    PRECURSOR_CHARGE = "precursor_charges"
    PRECURSOR_MZ = "precursor_m/z"
    MZ = "m/z"
    COLLISION_ENERGY = "collision_energies"
    FRAGMENTATION_TYPE = "fragmentation_types"
    # These are used for the peaks
    INTENSITY = "intensity"
    FRAGMENT_TYPE = "fragment_type"
    FRAGMENT_CHARGE = "fragment_charge"
    INSTRUMENT_TYPE = "instrument_types"
