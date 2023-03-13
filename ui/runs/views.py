import sys

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")
from protzilla.constants.constants import PATH_TO_PROJECT
from protzilla.importing.main_data_import import max_quant_import
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
    section, step, method = run.workflow_location()
    print(run.step_index, section, step, method)

    parameters = run.workflow_meta["sections"][section][step][method]["parameters"]
    fields = []
    for key, param_dict in parameters.items():
        fields.append(make_parameter_input(key, param_dict))

    return render(
        request,
        "runs/details.html",
        context=dict(
            run_name=run_name,
            fields=fields,
            show_next=run.result_df is not None,
            show_back=bool(len(run.history.steps) > 1),
        ),
    )
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
    run = Run.create(request.POST["run_name"], request.POST["workflow_config_name"])
    # to skip importing
    run.calculate_and_next(
        max_quant_import,
        file=PATH_TO_PROJECT / "tests/proteinGroups_small_cut.txt",
        intensity_name="Intensity",
    )
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
    arguments = {k: v[0] if len(v) == 1 else v for k, v in arguments.items()}
    run = active_runs[run_name]
    print(arguments)
    run.perform_calculation(lambda df, **kwargs: (df, {}), {})
    # TODO use selected method
    # run.perform_calculation_from_location(
    #     "data_preprocessing", "filter_proteins", "by_low_frequency", arguments
    # )

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))
