from enum import Enum

from protzilla.run_v2 import Run

from .base import MethodForm
from .custom_fields import CustomNumberInput, CustomChoiceField, CustomFloatField
from django.forms import FloatField


class EmptyEnum(Enum):
    pass


class SimpleImputerStrategyType(Enum):
    MEAN = "mean"
    MEDIAN = "median"
    MOST_FREQUENT = "most_frequent"


class ImputationByNormalDistributionSamplingStrategyType(Enum):
    PERPROTEIN = "perProtein"
    PERDATASET = "perDataset"


class ImputationMinPerProteinForm(MethodForm):
    shrinking_value = CustomFloatField(label="Shrinking value")
    shrinking_value = CustomFloatField(label="Shrinking value")


class FilterProteinsBySamplesMissingForm(MethodForm):
    percentage = CustomFloatField(label="Percentage of minimum non-missing samples per protein")


class FilterByProteinsCountForm(MethodForm):
    deviation_threshold = CustomFloatField(label="Number of standard deviations from the median:")


class SimpleImputationPerProteinForm(MethodForm):
    strategy = CustomChoiceField(choices=SimpleImputerStrategyType, label="Strategy")


class ImputationByKNNForms(MethodForm):
    number_of_neighbours = CustomFloatField(label="Number of neighbours")


class ImputationByNormalDistributionSamplingForm(MethodForm):
    strategy = CustomChoiceField(choices=ImputationByNormalDistributionSamplingStrategyType, label="Strategy")
    down_shift = CustomFloatField(label="Downshift")
    scaling_factor = CustomFloatField(label="Scaling factor")


class FilterPeptidesByPEPThresholdForm(MethodForm):
    threshold = CustomFloatField(label="Threshold value for PEP")
    peptide_df = CustomChoiceField(choices=EmptyEnum, label="peptide_df")
