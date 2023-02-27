# Create your views here.
import sys

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")
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
    # TODO load run into active runs when if it hasn't been loaded but is called?
    run = run_manager.active_runs[run_name]

    # add fields, plots, etc. from show history here

    # current step: method dropdown,
    # hidden divs for each not selected method,
    # visible div for selected method

    method_divs = []

    for method in run.step_dict.keys():
        parameters = run.workflow_meta["sections"][run.section][run.step][method][
            "parameters"
        ]
        fields = []
        for key, param_dict in parameters.items():
            if param_dict["type"] == "numeric":
                f = render_to_string(
                    "runs/field_number.html",
                    context=dict(
                        **param_dict,
                        disabled=False,
                        key=key,
                        default=run.preset_args[key]
                        if run.current_args is None
                        else run.current_args[key],
                    ),
                )
            if param_dict["type"] == "categorical":
                f = render_to_string(
                    "runs/field_select.html",
                    context=dict(
                        **param_dict,
                        disabled=False,
                        key=key,
                        default=run.presets[key]
                        if run.current_args is None
                        else run.current_args[key],
                    ),
                )
            else:
                param_type = param_dict["type"]
                ValueError(f"cannot match parameter type {param_type}")
            fields.append(f)
        method_divs.append(fields)

    print("step_dict", run.step_dict)

    step_methods = render_to_string(
        "runs/field_select_method.html",
        context=dict(
            step=run.step,
            step_name=run.step.replace("-", " ").title(),
            methods=run.step_dict.keys(),
            step_dict=run.step_dict,
            disabled=False,
            default=run.preset_args["method"]
            if not run.selected_args
            else run.selected_args,
            method_divs=method_divs,
        ),
    )

    return render(
        request,
        "runs/details.html",
        context=dict(run_name=run_name, step_methods=step_methods),
    )


def create(request):
    run_name = request.POST["run_name"]
    if run_name in run_manager.available_runs:
        run_manager.continue_run(run_name)
    else:
        run_manager.create_run(run_name, request.POST["workflow_config_name"])
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))
