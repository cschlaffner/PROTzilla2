from protzilla.run_v2 import Run

from .base import MethodForm
from .custom_fields import CustomNumberInput

#we left out the graphs things, didnt know how :(
class ImputationMinPerProteinForm(MethodForm):
    shrinking_value = CustomNumberInput(label="Shrinking value")

    def submit(self, run: Run):
        self.cleaned_data["shrinking_value"] = float(
            self.cleaned_data["shrinking_value"]
        )
        run.step_calculate(self.cleaned_data)

class FilterProteinsBySamplesMissingForm(MethodForm):
    percentage = CustomNumberInput(label="Percentage of minimum non-missing samples per protein")

    def submit(self, run:Run):
        self.cleaned_data["percentage"] = float(
            self.cleaned_data["percentage"]
        )
        run.step_calculate(self.cleaned_data)


class FilterByProteinsCountForm(MethodForm):
    deviation_threshold = CustomNumberInput(label="Number of standard deviations from the median:")

    def submit(self, run:Run):
        self.cleaned_data["deviation_threshold"] = float(
            self.cleaned_data["deviation_threshold"]
        )
        run.step_calculate(self.cleaned_data)


