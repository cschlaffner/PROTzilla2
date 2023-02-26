# Create your views here.
import os
import sys

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ui.main.settings import BASE_DIR

print("base", BASE_DIR)
print("pre:", os.getcwd())
sys.path.append(f"{BASE_DIR}")
print("post", os.getcwd())
from protzilla.run_manager import RunManager
from protzilla.workflow_manager import WorkflowManager

run_manager = RunManager()
workflow_manager = WorkflowManager()


def index(request):
    return render(
        request,
        "runs/index.html",
        context={
            "run_name_prefill": f"hello{123:03d}",
            "available_workflows": workflow_manager.available_workflows,
            "available_runs": run_manager.available_runs,
        },
    )


def detail(request, run_name):
    return HttpResponse(f"viewing details of {run_name}")


def create(request):
    run_name = request.POST["run_name"]
    if run_name in run_manager.available_runs:
        run_manager.continue_run(run_name)
    else:
        run_manager.create_run(run_name, request.POST["workflow_config_name"])
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))
