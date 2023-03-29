import sys

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR


sys.path.append(f"{BASE_DIR}/..")
from protzilla import workflow_helper

import protzilla.workflow_helper
from protzilla.run import Run
from protzilla.utilities.dynamic_parameters_provider import input_data_name
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


def make_parameter_input(key, param_dict, disabled):
    if param_dict["type"] == "numeric":
        template = "runs/field_number.html"
        if "step" not in param_dict:
            param_dict["step"] = "any"
    elif param_dict["type"] == "categorical":
        template = "runs/field_select.html"
    elif param_dict["type"] == "file":
        template = "runs/field_file.html"
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


def make_name_input(key, default, disabled):
    template = "runs/field_name.html"
    return render_to_string(
        template,
        context=dict(key=key, default=default, disabled=disabled),
    )


def make_input_data_dropdown(key, run, disabled):
    categories = input_data_name(run)
    template = "runs/field_select.html"
    return render_to_string(
        template,
        context=dict(
            key=key, categories=categories, name="Select input data", disabled=disabled
        ),
    )


def get_current_fields(run, section, step, method):
    parameters = run.workflow_meta[section][step][method]["parameters"]
    current_fields = []
    current_fields.append(
        make_name_input(
            "step_name",
            run.workflow_meta[section][step][method]["name"],
            disabled=False,
        )
    )
    if section == "data_analysis":
        current_fields.append(
            make_input_data_dropdown("input_data_name", run, disabled=False)
        )
    for key, param_dict in parameters.items():
        # todo use workflow default
        # todo 59 - restructure current_parameters
        if run.current_parameters is not None:
            param_dict["default"] = run.current_parameters.get(
                key, param_dict["default"]
            )

        current_fields.append(make_parameter_input(key, param_dict, disabled=False))
    return current_fields


def detail(request, run_name):
    if run_name not in active_runs:
        active_runs[run_name] = Run.continue_existing(run_name)
    run = active_runs[run_name]
    section, step, method = run.current_run_location()
    current_fields = get_current_fields(run, section, step, method)
    method_dropdown_id = f"{step}_method"

    current_fields.insert(
        0,
        render_to_string(
            "runs/field_select.html",
            context=dict(
                disabled=False,
                key=method_dropdown_id,
                name=f"{step.replace('_', ' ').title()} Method:",
                default=method,
                categories=run.workflow_meta[section][step].keys(),
            ),
        ),
    )

    displayed_history = []
    for history_step in run.history.steps:
        fields = []
        parameters = run.workflow_meta[history_step.section][history_step.step][
            history_step.method
        ]["parameters"]
        if history_step.section == "importing":
            name = f"{history_step.section}/{history_step.step}/{history_step.method}: {history_step.parameters['file_path'].split('/')[-1]}"
            df_head = (
                history_step.dataframe.head()
                if history_step.step == "ms_data_import"
                else run.metadata.head()
            )
            fields = [df_head.to_string()]
        else:
            fields.append(make_name_input("step_name", history_step.step_name, disabled=True))
            if history_step.section == "data_analysis":
                fields.append(
                    make_input_data_dropdown("input_data_name", run, disabled=True)
                )
            for key, param_dict in parameters.items():
                fields.append(
                    make_parameter_input(
                        key,
                        param_dict,
                        disabled=True,
                    )
                )
            name = f"{history_step.section}/{history_step.step}/{history_step.method}"
        displayed_history.append(dict(name=name, fields=fields))

    workflow_steps = workflow_helper.get_all_steps(run.workflow_config)
    highlighted_workflow_steps = [
        {"name": step, "highlighted": False} for step in workflow_steps
    ]
    highlighted_workflow_steps[run.step_index]["highlighted"] = True
    return render(
        request,
        "runs/details.html",
        context=dict(
            run_name=run_name,
            location=f"{run.section}/{run.step}",
            displayed_history=displayed_history,
            fields=current_fields,
            method_dropdown_id=method_dropdown_id,
            show_next=run.result_df is not None,
            show_back=bool(len(run.history.steps) > 1),
            sidebar_dropdown=make_add_step_dropdown(run, section),
            workflow_steps=highlighted_workflow_steps,
        ),
    )


def change_method(request, run_name):
    try:
        if run_name not in active_runs:
            active_runs[run_name] = Run.continue_existing(run_name)
        run = active_runs[run_name]
    except FileNotFoundError as e:
        print(str(e))
        response = JsonResponse({"error": f"Run '{run_name}' was not found"})
        response.status_code = 404  # not found
        return response
    run.method = request.POST["method"]
    current_fields = get_current_fields(run, run.section, run.step, run.method)
    html = render_to_string(
        "runs/fields.html",
        context=dict(fields=current_fields),
    )
    return JsonResponse(html, safe=False)


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
    section, step, method = run.current_run_location()
    post = dict(request.POST)
    del post["csrfmiddlewaretoken"]

    if section == "importing" or section == "data_preprocessing":
        run.prepare_calculation(post["step_name"][0])
    elif section == "data_analysis":
        run.prepare_calculation(post["step_name"][0], post["input_data_name"][0])
        del post["input_data_name"]

    del post["step_name"]
    del post[f"{step}_method"]

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
