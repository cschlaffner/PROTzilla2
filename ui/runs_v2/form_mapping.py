from django.http import HttpRequest

from protzilla.run import Run
from protzilla.steps import MaxQuantImport, MetadataImport

from .forms.base import MethodForm
from .forms.importing import MaxQuantImportForm, MetadataImportForm

form_map = {
    "MaxQuantImport": MaxQuantImportForm,
    "MetadataImportMethod": MetadataImportForm,
}


# TODO port to new below in file
def get_empty_form_by_method(step, run: Run) -> MethodForm:
    map = Mappings()
    form_class = map.get_form_class_by_step(step)
    if form_class:
        return form_class(run=run)
    else:
        raise ValueError(f"No form has been provided for {method} method.")


def get_filled_form_by_request(request: HttpRequest, run: Run) -> MethodForm:
    map = Mappings()
    method = request.POST["chosen_method"]
    form_class = map.get_form_class_by_step(method)
    if form_class:
        return form_class(run=run, data=request.POST, files=request.FILES)
    else:
        raise ValueError(f"No form has been provided for {method} method.")


class Mappings:
    def __init__(self):
        self.forward_mapping = {
            MaxQuantImport: MaxQuantImportForm,
            MetadataImport: MetadataImportForm,
        }
        self.reverse_mapping = {v: k for k, v in self.forward_mapping.items()}

    def generate_hierarchical_dict(self):
        # Initialize an empty dictionary
        hierarchical_dict = {}

        # List of all Step subclasses
        step_classes = self.forward_mapping.keys()

        # Iterate over each Step subclass
        for step_class in step_classes:
            # Create a nested dictionary with keys being the section, step, and method
            # and the value being the class itself
            if step_class.section not in hierarchical_dict:
                hierarchical_dict[step_class.section] = {}
            if step_class.step not in hierarchical_dict[step_class.section]:
                hierarchical_dict[step_class.section][step_class.step] = {}
            hierarchical_dict[step_class.section][step_class.step][
                step_class.method
            ] = step_class

        return hierarchical_dict

    def get_form_class_by_step(self, step):
        form_class = self.forward_mapping.get(type(step))
        if form_class:
            return form_class
        else:
            raise ValueError(
                f"No form has been provided for {type(step).__name__} step."
            )

    def get_step_class_by_form(self, form):
        step_class = self.reverse_mapping.get(type(form))
        if step_class:
            return step_class
        else:
            raise ValueError(
                f"No step has been provided for {type(form).__name__} form."
            )
