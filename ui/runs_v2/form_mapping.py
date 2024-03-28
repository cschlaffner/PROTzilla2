from django.http import HttpRequest

from protzilla.run import Run

from .forms.base import MethodForm
from .forms.importing import MaxQuantImportForm, MetadataImportForm

form_map = {
    "max_quant_import": MaxQuantImportForm,
    "metadata_import_method": MetadataImportForm,
}


def get_empty_form_by_method(method: str, run: Run) -> MethodForm:
    form_class = form_map.get(method)
    if form_class:
        return form_class(run=run)
    else:
        raise ValueError(f"No form has been provided for {method} method.")


def get_filled_form_by_request(request: HttpRequest, run: Run) -> MethodForm:
    method = request.POST["chosen_method"]
    form_class = form_map.get(method)
    if form_class:
        return form_class(run=run, data=request.POST, files=request.FILES)
    else:
        raise ValueError(f"No form has been provided for {method} method.")
