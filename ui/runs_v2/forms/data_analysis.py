from enum import Enum

from protzilla.run_v2 import Run
from .base import MethodForm
from .custom_fields import CustomChoiceField, CustomNumberInput


class TTestType(Enum):
    welchs_t_test = "Welch's t-Test"
    students_t_test = "Student's t-Test"


class AnalysisLevel(Enum):
    protein = "Protein"


class MultipelTestingCorrectionMethod(Enum):
    benjamini_hochberg = ("Benjamini-Hochberg",)
    bonferroni = "Bonferroni"


class LogBase(Enum):
    none = ("None",)
    log2 = ("log2",)
    log10 = "log10"


class DifferentialExpression_TTestForm(MethodForm):
    ttest_type = CustomChoiceField(choices=TTestType, label="T-test type")

    # intensity_df = CustomChoiceField(
    #    choices=AnalysisLevel, label="Intensitys"
    # )

    multiple_testing_correction = CustomChoiceField(
        choices=MultipelTestingCorrectionMethod, label="Multiple testing correction"
    )

    alpha = CustomNumberInput(label="Alpha")

    log_base = CustomChoiceField(choices=LogBase, label="Log base")

    grouping = "Put a usefull default here"

    group1 = "Put a usefull default here"

    group2 = "Put a usefull default here"

    def submit(self, run: Run):
        run.step_calculate(self.cleaned_data)
