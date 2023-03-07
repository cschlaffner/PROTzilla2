import sys

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from main.settings import BASE_DIR
from runs.forms import MSImportForm

sys.path.append(f"{BASE_DIR}/..")
from protzilla.run import Run
from protzilla.workflow_manager import WorkflowManager

workflow_manager = WorkflowManager()
active_runs = {}


def index(request):
    return render(
        request,
        "runs/index.html",
        context={
            "run_name_prefill": f"hello{123:03d}",
            "available_workflows": workflow_manager.available_workflows,
            "available_runs": Run.available_runs(),
        },
    )


def detail(request, run_name):
    if run_name not in active_runs:
        return HttpResponse(f"404: {run_name} not currently active")
    form = MSImportForm()  # A empty, unbound form
    return render(
        request,
        "runs/import.html",
        context={"form": form},
    )


def create(request):
    # TODO handle already existing, ask if overwrite
    run_name = request.POST["run_name"]
    active_runs[run_name] = Run.create(
        request.POST["run_name"], request.POST["workflow_config_name"]
    )
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def continue_(request):
    run_name = request.POST["run_name"]
    active_runs[run_name] = Run.continue_existing(run_name)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


# run1.get_next_item_in_workflow() -> (section, step, method)


def ms_import(request):
    # Handle file upload
    if request.method == "POST":
        form = MSImportForm(request.POST, request.FILES)
        if form.is_valid():
            print(request.FILES["docfile"])

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse("myapp.views.list"))
    else:
        form = MSImportForm()  # A empty, unbound form

    # Render list page with the documents and the form
    return render(
        request,
        "runs/import.html",
        context={"form": form},
    )
