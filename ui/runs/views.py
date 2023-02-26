# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

import sys
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")
from protzilla.run_manager import RunManager

run_manager = RunManager()


def index(request):
    return render(
        request,
        "runs/index.html",
        context={"run_name_prefill": f"hello{123:03d}"},
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
