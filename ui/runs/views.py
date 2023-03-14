import sys

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")
from protzilla.constants.paths import PROJECT_PATH
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


def make_parameter_input(key, param_dict):
    print(param_dict)
    if param_dict["type"] == "numeric":
        return render_to_string(
            "runs/field_number.html",
            context=dict(
                **param_dict,
                disabled=False,
                key=key,
                default=param_dict["default-value"],
            ),
        )
    elif param_dict["type"] == "categorical":
        return render_to_string(
            "runs/field_select.html",
            context=dict(
                **param_dict,
                disabled=False,
                key=key,
                default=param_dict["default-value"],
            ),
        )
    else:
        param_type = param_dict["type"]
        ValueError(f"cannot match parameter type {param_type}")


def detail(request, run_name):
    if run_name not in active_runs:
        active_runs[run_name] = Run.continue_existing(run_name)
    run = active_runs[run_name]
    section, step, method = run.current_workflow_location()

    parameters = run.workflow_meta["sections"][section][step][method]["parameters"]
    fields = []
    for key, param_dict in parameters.items():
        fields.append(make_parameter_input(key, param_dict))
    displayed_history = []
    for step in run.history.steps:
        displayed_history.append(step.method)
    return render(
        request,
        "runs/details.html",
        context=dict(
            run_name=run_name,
            displayed_history=displayed_history,
            fields=fields,
            show_next=run.result_df is not None,
            show_back=bool(len(run.history.steps) > 1),
        ),
    )


def create(request):
    run_name = request.POST["run_name"]
    run = Run.create(request.POST["run_name"], request.POST["workflow_config_name"])
    # to skip importing
    run.perform_calculation_from_location(
        "importing",
        "ms-data-import",
        "max-quant-data-import",
        dict(
            file=str(
                PROJECT_PATH / "tests/proteinGroups_small_cut.txt",
            ),
            intensity_name="Intensity",
        ),
    )
    run.next_step()
    run.step_index = 0  # needed because importing is left out of workflow
    active_runs[run_name] = run
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def continue_(request):
    run_name = request.POST["run_name"]
    active_runs[run_name] = Run.continue_existing(run_name)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def next_(request, run_name):
    run = active_runs[run_name]
    run.next_step()
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def back(request, run_name):
    run = active_runs[run_name]
    run.back_step()
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def calculate(request, run_name):
    arguments = dict(request.POST)
    del arguments["csrfmiddlewaretoken"]
    parameters = {}
    for k, v in arguments.items():
        if len(v) == 1:
            parameters[k] = v[0]
        else:
            parameters[k] = v
    run = active_runs[run_name]
    run.perform_calculation_from_location(*run.current_workflow_location(), parameters)

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))
