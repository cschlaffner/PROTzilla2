from enum import Enum

from .base import MethodForm
from .custom_fields import (
    CustomChoiceField,
)


class ColorChoices(Enum):
    standard = "standard"
    protan = "protan"
    deutan = "deutan"
    tritan = "tritan"
    monochromatic = "monochromatic"


class ColorForm(MethodForm):
    colors = CustomChoiceField(
        choices=ColorChoices,
        label="Color",
        initial=ColorChoices.standard,
    )
