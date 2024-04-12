from .base import MethodForm
from .custom_fields import CustomNumberInput


class ImputationMinPerProteinForm(MethodForm):
    shrinking_value = CustomNumberInput(label="Shrinking value")
