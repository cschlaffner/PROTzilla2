from enum import Enum

from .base import MethodForm
from .custom_fields import (
    CustomChoiceField,
    CustomCharField,
    CustomBooleanField
)
from protzilla.run_v2 import Run


class ColorChoices(Enum):
    standard = "standard"
    protan = "protan"
    deutan = "deutan"
    tritan = "tritan"
    monochromatic = "monochromatic"
    high_contrast = "high_contrast"
    custom = "custom"


class ColorForm(MethodForm):
    is_dynamic = True
    colors = CustomChoiceField(
        choices=ColorChoices,
        label="Color",
        initial=ColorChoices.standard,
    )
    custom_colors = CustomCharField(
        disabled=True,
        label="Custom Colors",
        initial="select " + ColorChoices.custom.value + " to enable",
    )

    def fill_form(self, run: Run) -> None:
        colors = self.data.get("colors", self.fields["colors"])
        if colors == ColorChoices.custom.value:  # for some reason ColorChoices.custom doesn't work
            self.fields["custom_colors"] = CustomCharField(
                disabled=False,
                label="Custom Colors",
                initial="#4A536A, #CE5A5A",
            )


class ReadingForm(MethodForm):
    enhanced_reading = CustomBooleanField(
        label="Enhanced Reading",
        initial=False,
    )
