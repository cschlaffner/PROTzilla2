import sys

from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")
from protzilla.run import Run
from ui.runs.fields import (
    make_add_step_dropdown,
    make_current_fields,
    make_displayed_history,
    make_highlighted_workflow_steps,
    make_method_dropdown,
    make_name_field,
    make_parameter_input,
    make_plot_fields,
)
from ui.runs.views_helper import parameters_from_post

active_runs = {}


def index(request):
    return render(
        request,
        "runs/index.html",
        context={
            "run_name_prefill": f"hello{123:03d}",
            "available_workflows": Run.available_workflows(),
            "available_runs": Run.available_runs(),
        },
    )


def detail(request, run_name):
    if run_name not in active_runs:
        active_runs[run_name] = Run.continue_existing(run_name)
    run = active_runs[run_name]
    section, step, method = run.current_run_location()
    allow_next = run.result_df is not None
    return render(
        request,
        "runs/details.html",
        context=dict(
            run_name=run_name,
            location=f"{run.section}/{run.step}",
            displayed_history=make_displayed_history(run),
            method_dropdown=make_method_dropdown(run, section, step, method),
            fields=make_current_fields(run, section, step, method),
            plot_fields=make_plot_fields(run, section, step, method),
            name_field=make_name_field(allow_next),
            current_plots=[plot.to_html() for plot in run.plots],
            show_next=run.result_df is not None,
            show_back=bool(run.history.steps),
            show_plot_button=run.result_df is not None,
            sidebar_dropdown=make_add_step_dropdown(run, section),
            workflow_steps=make_highlighted_workflow_steps(run),
        ),
    )


def change_method(request, run_name):
    # can this be extracted into a seperate method? (duplicate in change_field, detail)
    try:
        if run_name not in active_runs:
            active_runs[run_name] = Run.continue_existing(run_name)
        run = active_runs[run_name]
    except FileNotFoundError:
        traceback.print_exc()
        response = JsonResponse({"error": f"Run '{run_name}' was not found"})
        response.status_code = 404  # not found
        return response

    run.method = request.POST["method"]
    run.current_parameters = None
    run.current_plot_parameters = None
    parameters = run.workflow_meta[run.section][run.step][run.method]["parameters"]
    current_fields = make_current_fields(run, run.section, run.step, run.method)
    plot_fields = make_plot_fields(run, run.section, run.step, run.method)
    return JsonResponse(
        dict(
            parameters=render_to_string(
                "runs/fields.html",
                context=dict(fields=current_fields),
            ),
            plot_parameters=render_to_string(
                "runs/fields.html",
                context=dict(fields=plot_fields),
            ),
        ),
        safe=False,
    )


def change_field(request, run_name):
    # can this be extracted into a seperate method? (duplicate in change_method, detail)
    # e.g. "try_reactivate_run"
    try:
        if run_name not in active_runs:
            active_runs[run_name] = Run.continue_existing(run_name)
        run = active_runs[run_name]
    except FileNotFoundError as e:
        print(str(e))
        response = JsonResponse({"error": f"Run '{run_name}' was not found"})
        response.status_code = 404  # not found
        return response

    post_id = request.POST["id"]
    selected = request.POST["selected"]
    parameters = run.workflow_meta[run.section][run.step][run.method]["parameters"]
    fields_to_fill = parameters[post_id]["fill_dynamic"]

    fields = {}
    for key in fields_to_fill:
        param_dict = parameters[key]
        if param_dict["fill"] == "metadata_column_data":
            param_dict["categories"] = run.metadata[selected].unique()
            fields[key] = make_parameter_input(key, param_dict, disabled=False)

    return JsonResponse(fields, safe=False)


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
    run.next_step(request.POST["name"])
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def back(request, run_name):
    run = active_runs[run_name]
    run.back_step()
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def add(request, run_name):
    run = active_runs[run_name]

    post = dict(request.POST)
    del post["csrfmiddlewaretoken"]
    step = post["step_to_be_added"][0]

    if step == "":
        return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))

    run.insert_as_next_step(step)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def calculate(request, run_name):
    run = active_runs[run_name]
    section, step, method = run.current_run_location()
    parameters = parameters_from_post(request.POST)
    del parameters["chosen_method"]

    for k, v in dict(request.FILES).items():
        # assumption: only one file uploaded
        parameters[k] = v[0].temporary_file_path()
    run.perform_calculation_from_location(section, step, method, parameters)

    result = run.current_out
    if "messages" in result:
        for message in result["messages"]:
            trace = f"<br> Trace: {message['trace']}" if "trace" in message else ""
            messages.add_message(
                request, message["level"], f"{message['msg']}{trace}", message["level"]
            )

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def plot(request, run_name):
    run = active_runs[run_name]
    section, step, method = run.current_run_location()
    parameters = parameters_from_post(request.POST)
    run.create_plot_from_location(section, step, method, parameters)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def add_name(request, run_name):
    run = active_runs[run_name]
    run.history.name_step(int(request.POST["index"]), request.POST["name"])
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def outputs_of_step(request, run_name):
    run = active_runs[run_name]
    step_name = request.POST["step_name"]
    return JsonResponse(run.history.output_keys_of_named_step(step_name), safe=False)
