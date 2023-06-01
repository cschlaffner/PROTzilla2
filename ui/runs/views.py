import sys
import tempfile
import traceback
import zipfile

import pandas as pd
from django.contrib import messages
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")

from protzilla.run import Run
from protzilla.utilities.memory import get_memory_usage
from ui.runs.fields import (
    make_current_fields,
    make_displayed_history,
    make_method_dropdown,
    make_name_field,
    make_parameter_input,
    make_plot_fields,
    make_sidebar,
)
from ui.runs.utilities.alert import build_trace_alert
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
    allow_next = run.calculated_method is not None or (run.step == "plot" and run.plots)
    end_of_run = not step
    return render(
        request,
        "runs/details.html",
        context=dict(
            run_name=run_name,
            section=section,
            step=step,
            display_name=f"{run.step.replace('_', ' ').title()}",
            displayed_history=make_displayed_history(run),
            method_dropdown=make_method_dropdown(run, section, step, method),
            fields=make_current_fields(run, section, step, method),
            plot_fields=make_plot_fields(run, section, step, method),
            name_field=make_name_field(allow_next, "runs_next", run, end_of_run),
            current_plots=[
                plot.to_html(include_plotlyjs=False, full_html=False)
                for plot in run.plots
                if not isinstance(plot, dict)
            ],
            show_next=allow_next,
            show_back=bool(run.history.steps),
            show_plot_button=run.result_df is not None,
            sidebar=make_sidebar(request, run, run_name),
            end_of_run=end_of_run,
            used_memory=get_memory_usage(),
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

    selected = request.POST.getlist("selected[]")
    post_id = request.POST["id"]
    if len(selected) > 1:
        # remove last 4 characters from post_id to get the original id
        # because multiple selected items are in id_div
        post_id = post_id[:-4]

    parameters = run.workflow_meta[run.section][run.step][run.method]["parameters"]
    fields_to_fill = parameters[post_id]["fill_dynamic"]

    fields = {}
    for key in fields_to_fill:
        param_dict = parameters[key]

        if param_dict["fill"] == "metadata_column_data":
            param_dict["categories"] = run.metadata[selected].unique()
        elif param_dict["fill"] == "protein_ids":
            named_output = selected[0]
            output_item = selected[1]
            # KeyError is expected when named_output triggers the fill
            try:
                protein_itr = run.history.output_of_named_step(
                    named_output, output_item
                )
            except KeyError:
                protein_itr = None
            if isinstance(protein_itr, pd.DataFrame):
                param_dict["categories"] = protein_itr["Protein ID"].unique()
            elif isinstance(protein_itr, pd.Series):
                param_dict["categories"] = protein_itr.unique()
            elif isinstance(protein_itr, list):
                param_dict["categories"] = protein_itr
            else:
                param_dict["categories"] = []
                print(
                    f"Warning: expected protein_itr to be a DataFrame, Series or list, but got {type(protein_itr)}. Proceeding with empty list."
                )

        fields[key] = make_parameter_input(key, param_dict, disabled=False)

    return JsonResponse(fields, safe=False)


def create(request):
    run_name = request.POST["run_name"]
    run = Run.create(
        run_name,
        request.POST["workflow_config_name"],
        df_mode=request.POST["df_mode"],
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
    step = post["step"][0]
    section = post["section_name"][0]
    method = post["method"][0]

    run.insert_at_next_position(step, section, method)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def delete_step(request, run_name):
    run = active_runs[run_name]

    post = dict(request.POST)
    del post["csrfmiddlewaretoken"]
    index = int(post["index"][0])
    section = post["section_name"][0]
    run.delete_step(section, index)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def export_workflow(request, run_name):
    run = active_runs[run_name]
    post = dict(request.POST)
    del post["csrfmiddlewaretoken"]
    print("run_name")
    print(run_name)
    name = post["name"][0]
    run.export_workflow(name)

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def calculate(request, run_name):
    run = active_runs[run_name]
    parameters = parameters_from_post(request.POST)
    del parameters["chosen_method"]

    for k, v in dict(request.FILES).items():
        # assumption: only one file uploaded
        parameters[k] = v[0].temporary_file_path()
    run.perform_current_calculation_step(parameters)

    result = run.current_out
    if "messages" in result:
        for message in result["messages"]:
            trace = build_trace_alert(message["trace"]) if "trace" in message else ""

            # map error level to bootstrap css class
            lvl_to_css_class = {
                40: "alert-danger",
                30: "alert-warning",
                20: "alert-info",
            }
            messages.add_message(
                request,
                message["level"],
                f"{message['msg']} {trace}",
                lvl_to_css_class[message["level"]],
            )

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def plot(request, run_name):
    run = active_runs[run_name]
    section, step, method = run.current_run_location()
    parameters = parameters_from_post(request.POST)

    if run.step == "plot":
        del parameters["chosen_method"]

    run.create_plot_from_current_location(parameters)

    for index, p in enumerate(run.plots):
        if isinstance(p, dict):
            for message in run.plots[index]["messages"]:
                trace = (
                    build_trace_alert(message["trace"]) if "trace" in message else ""
                )

                # map error level to bootstrap css class
                lvl_to_css_class = {
                    40: "alert-danger",
                    30: "alert-warning",
                    20: "alert-info",
                }
                messages.add_message(
                    request,
                    message["level"],
                    f"{message['msg']} {trace}",
                    lvl_to_css_class[message["level"]],
                )

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def add_name(request, run_name):
    run = active_runs[run_name]
    run.name_step(int(request.POST["index"]), request.POST["name"])
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def results_exist(request, run_name):
    run = active_runs[run_name]
    return JsonResponse(dict(results_exist=run.result_df is not None))


def all_button_parameters(request, run_name):
    run = active_runs[run_name]
    d = dict()
    d["current_plot_parameters"] = run.current_plot_parameters.get(run.method, {})
    d["plotted_for_parameters"] = (
        run.plotted_for_parameters if run.plotted_for_parameters is not None else dict()
    )

    if run.current_parameters is None or run.result_df is None:
        d["current_parameters"] = dict()
        d["chosen_method"] = dict()
    else:
        d["current_parameters"] = run.current_parameters[run.method]
        d["chosen_method"] = run.method

    return JsonResponse(d)


def outputs_of_step(request, run_name):
    run = active_runs[run_name]
    step_name = request.POST["step_name"]
    return JsonResponse(run.history.output_keys_of_named_step(step_name), safe=False)


def download_plots(request, run_name):
    run = active_runs[run_name]
    format_ = request.GET["format"]
    exported = run.export_plots(format_=format_)
    if len(exported) == 1:
        filename = f"{run.step_index}-{run.section}-{run.step}-{run.method}.{format_}"
        return FileResponse(exported[0], filename=filename, as_attachment=True)

    f = tempfile.NamedTemporaryFile()
    with zipfile.ZipFile(f, "w") as zf:
        for i, plot in enumerate(exported):
            filename = (
                f"{run.step_index}-{run.section}-{run.step}-{run.method}-{i}.{format_}"
            )
            zf.writestr(filename, plot.getvalue())
    return FileResponse(
        open(f.name, "rb"),
        filename=f"{run.step_index}-{run.section}-{run.step}-{run.method}-{format_}.zip",
        as_attachment=True,
    )
