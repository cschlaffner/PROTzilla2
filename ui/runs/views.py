# Create your views here.
import sys

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

print(sys.path)
sys.path.append(f"{BASE_DIR}/..")
print(sys.path)
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
                        default=run.preset_args["parameters"][key]
                        if not run.current_args
                        else run.current_args[key],
                    ),
                )
            # why if else in default?
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

    method_names = [n.replace("-", " ").title() for n in run.step_dict.keys()]
    methods_dict = zip(run.step_dict.keys(), method_names, method_divs)

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
            show_next= show_next,
            method_divs=method_divs,
            show_back = show_back,
        ),
    )


def create(request):
    run_name = request.POST["run_name"]
    if run_name in run_manager.available_runs:
        run_manager.continue_run(run_name)
    else:
        run_manager.create_run(run_name, request.POST["workflow_config_name"])
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def next(request, run_name):
    run_name = request.POST["run_name"]
    run = run_manager.runs[run_name]
    run.next_step()
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def back(request, run_name):
    run = run_manager.runs[run_name]
    run.back_step()
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def calculate(request, run_name):
    # TODO: check correctness and add calculate here
    arguments = dict(request.POST)
    del arguments["csrfmiddlewaretoken"]
    arguments = {k: v[0] if len(v) == 1 else v for k, v in arguments.items()}
    print("arguments")
    print(arguments)

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))
