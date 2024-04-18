from enum import Enum

from protzilla.run_v2 import Run
from .base import MethodForm
from .custom_fields import CustomFloatField, CustomChoiceField


class ImputationMinPerProteinForm(MethodForm):
    shrinking_value = CustomFloatField(label="Shrinking value")

    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)


class ImputationGraphTypes(Enum):
    Boxplot = "Boxplot"
    Histogram = "Histogram"


class GroupBy(Enum):
    NoGrouping = "None"
    Sample = "Sample"
    ProteinID = "Protein ID"


class VisualTrasformations(Enum):
    linear = "linear"
    Log10 = "log10"


class GraphTypesImputedValues(Enum):
    Bar = "Bar chart"
    Pie = "Pie chart"


class ImputationMinPerProteinPlotForm(MethodForm):
    graph_type = CustomChoiceField(choices=ImputationGraphTypes, label="Graph type")

    group_by = CustomChoiceField(choices=GroupBy, label="Group by")

    visual_transformation = CustomChoiceField(
        VisualTrasformations, label="Visual transformation"
    )

    graph_type_quantities = CustomChoiceField(
        GraphTypesImputedValues, label="Graph type - quantity of imputed values"
    )
