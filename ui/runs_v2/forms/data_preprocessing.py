from enum import Enum

from protzilla.run_v2 import Run

from .base import MethodForm
from .custom_fields import CustomNumberInput, CustomChoiceField, CustomFloatField
from django.forms import FloatField


# we left out the graphs things, didnt know how :(
class EmptyEnum(Enum):
    pass


class StrategyType(Enum):
    PERPROTEIN = "perProtein"
    PERDATASET = "perDataset"


class ImputationMinPerProteinForm(MethodForm):
    shrinking_value = CustomNumberInput(label="Shrinking value")

    def submit(self, run: Run):
        self.cleaned_data["shrinking_value"] = float(
            self.cleaned_data["shrinking_value"]
        )
        run.step_calculate(self.cleaned_data)


class FilterProteinsBySamplesMissingForm(MethodForm):
    percentage = CustomFloatField(label="Percentage of minimum non-missing samples per protein")


class FilterByProteinsCountForm(MethodForm):
    deviation_threshold = CustomNumberInput(label="Number of standard deviations from the median:")

    def submit(self, run: Run):
        self.cleaned_data["deviation_threshold"] = float(
            self.cleaned_data["deviation_threshold"]
        )
        run.step_calculate(self.cleaned_data)


class ImputationByKNNForms(MethodForm):
    number_of_neighbours = CustomNumberInput(label="Number of neighbours")

    def submit(self, run: Run):
        self.cleaned_data["number_of_neighbours"] = float(
            self.cleaned_data["number_of_neighbours"]
        )
        run.step_calculate(self.cleaned_data)


class ImputationByNormalDistributionSamplingForm(MethodForm):
    strategy = CustomChoiceField(choices=StrategyType, label="Strategy")
    down_shift = CustomNumberInput(label="Downshift")
    scaling_factor = CustomNumberInput(label="Scaling factor")

    def submit(self, run: Run):
        self.cleaned_data["down_shift"] = float(
            self.cleaned_data["down_shift"]
        )
        self.cleaned_data["scaling_factor"] = float(
            self.cleaned_data["scaling_factor"]
        )
        run.step_calculate(self.cleaned_data)


class FilterPeptidesByPEPThresholdForm(MethodForm):
    threshold = CustomNumberInput(label="Threshold value for PEP")
    peptide_df = CustomChoiceField(choices=EmptyEnum, label="peptide_df")

    def submit(self, run: Run):
        self.cleaned_data["threshold"] = float(
            self.cleaned_data["threshold"]
        )
        run.step_calculate(self.cleaned_data)
