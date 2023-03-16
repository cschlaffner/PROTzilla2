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


def make_parameter_input(key, param_dict, disabled, default=None):
    if param_dict["type"] == "numeric":
        template = "runs/field_number.html"
    elif param_dict["type"] == "categorical":
        template = "runs/field_select.html"
    elif param_dict["type"] == "file":
        template = "runs/field_file.html"
    else:
        raise ValueError(f"cannot match parameter type {param_dict['type']}")
    if default is None:
        default = param_dict.get("default-value")

    return render_to_string(
        template,
        context=dict(
            **param_dict,
            disabled=disabled,
            key=key,
            default=default,
        ),
    )


def detail(request, run_name):
    if run_name not in active_runs:
        active_runs[run_name] = Run.continue_existing(run_name)

    run = active_runs[run_name]
    section, step, method = run.current_workflow_location()

    parameters = run.workflow_meta["sections"][section][step][method]["parameters"]
    current_fields = []
    for key, param_dict in parameters.items():
        # todo use workflow default
        if run.current_parameters:
            default = run.current_parameters[key]
        else:
            default = None
        current_fields.append(
            make_parameter_input(key, param_dict, disabled=False, default=default)
        )
    displayed_history = []
    for step in run.history.steps:
        fields = []
        if step.section != "importing":
            parameters = run.workflow_meta["sections"][step.section][step.step][
                step.method
            ]["parameters"]
            for key, param_dict in parameters.items():
                fields.append(
                    make_parameter_input(
                        key, param_dict, disabled=True, default=step.parameters[key]
                    )
                )
        displayed_history.append(
            dict(name=f"{step.section}/{step.step}/{step.method}", fields=fields)
        )
    return render(
        request,
        "runs/details.html",
        context=dict(
            run_name=run_name,
            info_str=str(run.current_workflow_location()),
            displayed_history=displayed_history,
            fields=current_fields,
            show_next=run.result_df is not None,
            show_back=bool(len(run.history.steps) > 1),
        ),
    )


def create(request):
    run_name = request.POST["run_name"]
    run = Run.create(
        run_name,
        request.POST["workflow_config_name"],
        df_mode="disk_memory",
    )
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
    post = dict(request.POST)
    del post["csrfmiddlewaretoken"]
    parameters = {}
    for k, v in post.items():
        if len(v) == 1:
            parameters[k] = v[0]
        else:
            parameters[k] = v
    for k, v in dict(request.FILES).items():
        # assumption: only one file uploaded
        parameters[k] = v[0].temporary_file_path()
    run = active_runs[run_name]
    run.perform_calculation_from_location(*run.current_workflow_location(), parameters)

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))
