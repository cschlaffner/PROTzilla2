import sys

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR, STATIC_URL

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


def make_parameter_input(key, param_dict, disabled, default=None):
    if param_dict["type"] == "numeric":
        template = "runs/field_number.html"
    elif param_dict["type"] == "categorical":
        template = "runs/field_select.html"
    else:
        ValueError(f"cannot match parameter type {param_dict['type']}")
    if default is None:
        default = param_dict["default-value"]

    return render_to_string(
        template,
        context=dict(
            **param_dict,
            disabled=disabled,
            key=key,
            default=default,
        ),
    )

def get_current_fields(run, section, step, method):
    parameters = run.workflow_meta["sections"][section][step][method]["parameters"]
    current_fields = []

    for key, param_dict in parameters.items():
        if run.current_parameters:
            default = run.current_parameters[key]
        else:
            default = None
        current_fields.append(
            make_parameter_input(key, param_dict, disabled=False, default=default)
        )
    return current_fields

def detail(request, run_name):
    if run_name not in active_runs:
        run = Run.continue_existing(run_name)
        run.step_index = len(run.history.steps) - 1
        active_runs[run_name] = run

    run = active_runs[run_name]
    section, step, method = run.current_workflow_location()
    
    current_fields = get_current_fields(run, section, step, method)
    method_dropdown_id = f"{step.replace('-', '_')}_method"

    current_fields.insert(0,
            render_to_string(
            "runs/field_select.html",
            context=dict(
                disabled=False,
                key=method_dropdown_id,
                name=f"{step.replace('-', '_').capitalize()} Method:",
                default=method,
                categories=run.workflow_meta["sections"][section][step].keys(),
            ),
            )
    )

    displayed_history = []
    for history_step in run.history.steps:
        fields = []
        if history_step.section != "importing":
            parameters = run.workflow_meta["sections"][history_step.section][history_step.step][
                history_step.method
            ]["parameters"]
            for key, param_dict in parameters.items():
                fields.append(
                    make_parameter_input(
                        key, param_dict, disabled=True, default=history_step.parameters[key]
                    )
                )
        displayed_history.append(
            dict(name=f"{history_step.section}/{history_step.step}/{history_step.method}", fields=fields)
        )
    return render(
        request,
        "runs/details.html",
        context=dict(
            run_name=run_name,
            info_str=str(run.current_workflow_location()),
            displayed_history=displayed_history,
            fields=current_fields,
            method_dropdown_id=method_dropdown_id,
            method_details_id=f"{step.replace('-', '_')}_details",
            show_next=run.result_df is not None,
            show_back=bool(len(run.history.steps) > 1),
            static_url=STATIC_URL,
        ),
    )

def change_method(request, run_name):
    try:
        run = active_runs[run_name]
    except:
        response = JsonResponse({"error": "Run was not found"})
        response.status_code = 500 # internal server error 
        return response
    section, step, _ = run.current_workflow_location()
    current_fields = get_current_fields(run, section, step, request.POST["method"])

    html = render_to_string(
                "runs/fields.html",
                context=dict(
                    fields=current_fields
                ),
            )
    return JsonResponse(html, safe=False)


def create(request):
    run_name = request.POST["run_name"]
    run = Run.create(
        request.POST["run_name"],
        request.POST["workflow_config_name"],
        df_mode="disk_memory",
    )
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
    run = Run.continue_existing(run_name)
    run.step_index = len(run.history.steps) - 1
    # this should be moved to Run.continue_existing but cant yet because
    # importing does not exist yet
    active_runs[run_name] = run
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
