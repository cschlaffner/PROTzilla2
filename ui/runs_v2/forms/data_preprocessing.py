from protzilla.run_v2 import Run

from .base import MethodForm
from .custom_fields import CustomNumberInput


class ImputationMinPerProteinForm(MethodForm):
    shrinking_value = CustomNumberInput(label="Shrinking value")

    def submit(self, run: Run):
        self.cleaned_data["shrinking_value"] = float(
            self.cleaned_data["shrinking_value"]
        )
        run.step_calculate(self.cleaned_data)
