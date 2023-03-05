from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

import sys

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

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
    # TODO load run into active runs when if it hasn't been loaded but is called?
    run = active_runs[run_name]

    # add fields, plots, etc. from show history here

    # current step: method dropdown,
    # hidden divs for each not selected method,
    # visible div for selected method

    method_divs = []

    print("preset args", run.preset_args)

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
                        default=run.preset_args["parameters"][key]
                        if not run.current_args
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
                        default=run.preset_args["parameters"][key]
                        if not run.current_args
                        else run.current_args[key],
                    ),
                )
            else:
                param_type = param_dict["type"]
                ValueError(f"cannot match parameter type {param_type}")
            fields.append(f)
        method_divs.append(dict(fields=fields))

    # WHAT I DID: removed too many layers of lists involved in the current method_divs
    # copied quite a lot from prototype to get to a point of it not breaking
    # added next and calculate view functions and buttons
    # NEXT STEPS - TODO:
    #   * connect frontend to calculating
    #   * check functionality of next back buttons etc (hat to stop coding while this was in progress)
    #   * clean up existing code (after ensuring basic funtionality)

    print("step_dict", run.step_dict)

    print("method_keys", run.step_dict.keys())
    print("method_divs", method_divs)

    method_names = [n.replace("-", " ").title() for n in run.step_dict.keys()]
    methods_dict = zip(run.step_dict.keys(), method_names, method_divs)

    print("methods_dict", methods_dict)
    for key, name, fields in methods_dict:
        print("Key:", key)
        print("Name:", name)
        print("fields:", fields)

    step_methods = render_to_string(
        "runs/field_select_method.html",
        context=dict(
            step=run.step,
            step_name=run.step.replace("-", " ").title(),
            step_dict=run.step_dict,
            disabled=False,
            default=run.preset_args["method"]
            if not run.current_args
            else run.current_args,
            methods_dict=methods_dict,
            method_field=method_divs[0],
        ),
    )

    print("step_methods", step_methods)
    # TODO: check whether this is the correct df
    # check this logic: is history args = preset_args?
    show_next = run.result_df is not None
    show_back = bool(run.preset_args)
    return render(
        request,
        "runs/details.html",
        context=dict(
            run_name=run_name,
            step_methods=step_methods,
            show_next=show_next,
            method_divs=method_divs,
            show_back=show_back,
        ),
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


def next(request, run_name):
    run_name = request.POST["run_name"]
    run = active_runs[run_name]
    run.next_step()
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def back(request, run_name):
    run = active_runs[run_name]
    run.back_step()
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def calculate(request, run_name):
    # TODO: check correctness and add calculate here
    arguments = dict(request.POST)
    del arguments["csrfmiddlewaretoken"]
    arguments = {k: v[0] if len(v) == 1 else v for k, v in arguments.items()}
    print(arguments)

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))
