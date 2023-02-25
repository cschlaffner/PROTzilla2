# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

import sys
from main.settings import BASE_DIR
sys.path.append(f"{BASE_DIR}/..")
from protzilla.run_manager import RunManager

run_manager = RunManager()


def index(request):
    return HttpResponse("Hello, world. You're at the runs index.")


def detail(request, run_name):
    return HttpResponse(f"viewing details of {run_name}")


def create(request):
    run_name = request.POST["run_name"]
    if run_name in run_manager.available_runs:
        run_manager.continue_run(run_name)
    else:
        run_manager.create_run(run_name, request.POST["workflow_config_name"])
    return HttpResponseRedirect(reverse("detail", args=(run_name,)))
