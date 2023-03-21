import sys

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")
from protzilla.run import Run
from protzilla.utilities.dynamic_parameters_provider import input_df
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


def make_parameter_input(key, param_dict, run, disabled):
    if param_dict["type"] == "numeric":
        template = "runs/field_number.html"
        if "step" not in param_dict:
            param_dict["step"] = "any"
    elif param_dict["type"] == "categorical":
        template = "runs/field_select.html"
    elif param_dict["type"] == "file":
        template = "runs/field_file.html"
    elif param_dict["type"] == "dynamic-categorical":
        param_dict["categories"] = input_df(run)
        template = "runs/field_select.html"
    else:
        raise ValueError(f"cannot match parameter type {param_dict['type']}")

    return render_to_string(
        template,
        context=dict(
            **param_dict,
            disabled=disabled,
            key=key,
        ),
    )


def make_add_step_dropdown(run, section):
    template = "runs/field_select.html"

    steps = list(run.workflow_meta[section].keys())
    print(steps)
    steps.insert(0, "")

    return render_to_string(
        template,
        context=dict(
            name="add step:\n",
            type="categorical",
            categories=steps,
            key="add steps",
        ),
    )


def detail(request, run_name):
    if run_name not in active_runs:
        active_runs[run_name] = Run.continue_existing(run_name)
    run = active_runs[run_name]
    section, step, method = run.current_workflow_location()

    parameters = run.workflow_meta[section][step][method]["parameters"]
    current_fields = []
    for key, param_dict in parameters.items():
        # todo use workflow default
        if run.current_parameters:
            param_dict["default"] = run.current_parameters[key]
        current_fields.append(
            make_parameter_input(key, param_dict, run, disabled=False)
        )
    displayed_history = []
    for step in run.history.steps:
        fields = []
        if step.section == "importing":
            name = f"{step.section}/{step.step}/{step.method}: {step.parameters['file'].split('/')[-1]}"
        else:
            parameters = run.workflow_meta[step.section][step.step][step.method][
                "parameters"
            ]
            for key, param_dict in parameters.items():
                param_dict["default"] = step.parameters[key]
                fields.append(make_parameter_input(key, param_dict, run, disabled=True))
            name = f"{step.section}/{step.step}/{step.method}"
        displayed_history.append(dict(name=name, fields=fields))
    return render(
        request,
        "runs/details.html",
        context=dict(
            run_name=run_name,
            location=str(run.current_workflow_location()),
            displayed_history=displayed_history,
            fields=current_fields,
            show_next=run.result_df is not None,
            show_back=bool(len(run.history.steps) > 1),
            sidebar_dropdown=make_add_step_dropdown(run, section),
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


def add(request, run_name):
    run = active_runs[run_name]

    post = dict(request.POST)
    del post["csrfmiddlewaretoken"]
    step = post["add steps"][0]

    if step == "":
        return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))

    run.insert_as_next_step(step)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def calculate(request, run_name):
    run = active_runs[run_name]
    section, step, method = run.current_workflow_location()
    post = dict(request.POST)
    del post["csrfmiddlewaretoken"]
    parameters = {}
    for k, v in post.items():
        # assumption: only one value for parameter
        param_dict = run.workflow_meta[section][step][method]["parameters"][k]
        if param_dict["type"] == "numeric" and param_dict["step"] == 1:
            parameters[k] = int(v[0])
        elif param_dict["type"] == "numeric":
            parameters[k] = float(v[0])
        else:
            parameters[k] = v[0]

    for k, v in dict(request.FILES).items():
        # assumption: only one file uploaded
        parameters[k] = v[0].temporary_file_path()
    run.perform_calculation_from_location(section, step, method, parameters)

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))
