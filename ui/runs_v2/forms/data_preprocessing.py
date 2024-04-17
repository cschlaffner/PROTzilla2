from enum import Enum

from protzilla.run_v2 import Run

from .base import MethodForm
from .custom_fields import CustomNumberInput, CustomChoiceField, CustomFloatField
from django.forms import FloatField


class EmptyEnum(Enum):
    pass


class StrategyType(Enum):
    PERPROTEIN = "perProtein"
    PERDATASET = "perDataset"
from .custom_fields import CustomFloatField


class ImputationMinPerProteinForm(MethodForm):
    shrinking_value = CustomFloatField(label="Shrinking value")
    shrinking_value = CustomFloatField(label="Shrinking value")


class FilterProteinsBySamplesMissingForm(MethodForm):
    percentage = CustomFloatField(label="Percentage of minimum non-missing samples per protein")


class FilterByProteinsCountForm(MethodForm):
    deviation_threshold = CustomFloatField(label="Number of standard deviations from the median:")


class ImputationByKNNForms(MethodForm):
    number_of_neighbours = CustomFloatField(label="Number of neighbours")


    def submit(self, run: Run):
        self.cleaned_data["shrinking_value"] = float(
            self.cleaned_data["shrinking_value"]
        )
        run.step_calculate(self.cleaned_data)
