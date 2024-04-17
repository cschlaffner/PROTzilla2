from protzilla.run_v2 import Run

from .base import MethodForm
from .custom_fields import CustomFloatField


class ImputationMinPerProteinForm(MethodForm):
    shrinking_value = CustomFloatField(label="Shrinking value")

    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)
