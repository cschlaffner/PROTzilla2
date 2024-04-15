from django.http import HttpRequest

import protzilla.methods.data_analysis as data_analysis
import protzilla.methods.data_preprocessing as data_preprocessing
import protzilla.methods.importing as importing
import ui.runs_v2.forms.data_analysis as data_analysis_forms
import ui.runs_v2.forms.data_preprocessing as data_preprocessing_forms
import ui.runs_v2.forms.importing as importing_forms
from protzilla.run_v2 import Run
from protzilla.steps import Step
from .forms.base import MethodForm

_forward_mapping = {
    importing.MaxQuantImport: importing_forms.MaxQuantImportForm,
    importing.MetadataImport: importing_forms.MetadataImportForm,
    data_preprocessing.ImputationMinPerProtein: data_preprocessing_forms.ImputationMinPerProteinForm,
    data_analysis.DifferentialExpression_TTest: data_analysis_forms.DifferentialExpression_TTestForm,
}


_reverse_mapping = {v: k for k, v in _forward_mapping.items()}


def generate_hierarchical_dict() -> dict[str, dict[str, dict[str, type[Step]]]]:
    # Initialize an empty dictionary
    hierarchical_dict = {}

    # List of all Step subclasses
    step_classes = _forward_mapping.keys()

    # Iterate over each Step subclass
    for step_class in step_classes:
        # Create a nested dictionary with keys being the section, step, and method
        # and the value being the class itself
        if step_class.section not in hierarchical_dict:
            hierarchical_dict[step_class.section] = {}
        if step_class.step not in hierarchical_dict[step_class.section]:
            hierarchical_dict[step_class.section][step_class.step] = {}
        hierarchical_dict[step_class.section][step_class.step][
            step_class.method_id
        ] = step_class

    return hierarchical_dict


def _get_form_class_by_step(step: Step) -> type[MethodForm]:
    form_class = _forward_mapping.get(type(step))
    if form_class:
        return form_class
    else:
        raise ValueError(f"No form has been provided for {type(step).__name__} step.")


def _get_step_class_by_form(form: MethodForm) -> type[Step]:
    step_class = _reverse_mapping.get(type(form))
    if step_class:
        return step_class
    else:
        raise ValueError(f"No step has been provided for {type(form).__name__} form.")


def get_empty_form_by_method(step: Step, run: Run) -> MethodForm:
    return _get_form_class_by_step(step)(run=run)


def get_filled_form_by_request(request: HttpRequest, run: Run) -> MethodForm:
    form_class = _get_form_class_by_step(run.steps.current_step)
    return form_class(run=run, data=request.POST, files=request.FILES)


def get_all_methods() -> list[type[Step]]:
    return list(_forward_mapping.keys())
