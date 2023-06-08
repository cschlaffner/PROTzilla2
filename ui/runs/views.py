import sys
import tempfile
import traceback
import zipfile

import networkx as nx
import numpy as np
import pandas as pd
from django.contrib import messages
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")

from protzilla.run import Run
from protzilla.run_helper import get_parameters
from protzilla.utilities.memory import get_memory_usage
from ui.runs.fields import (
    make_current_fields,
    make_displayed_history,
    make_dynamic_fields,
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

    current_plots = []
    for plot in run.plots:
        if isinstance(plot, bytes):
            # Base64 encoded image
            current_plots.append(
                '<div class="row d-flex justify-content-center mb-4"><img src="data:image/png;base64, {}"></div>'.format(
                    plot.decode("utf-8")
                )
            )
        elif isinstance(plot, dict):
            if "plot_base64" in plot:
                current_plots.append(
                    '<div class="row d-flex justify-content-center mb-4"><img id="{}" src="data:image/png;base64, {}"></div>'.format(
                        plot["key"], plot["plot_base64"].decode("utf-8")
                    )
                )
            else:
                current_plots.append(None)
        else:
            current_plots.append(plot.to_html(include_plotlyjs=False, full_html=False))

    show_table = run.current_out and any(
        isinstance(v, pd.DataFrame) for v in run.current_out.values()
    )
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
            current_plots=current_plots,
            show_next=allow_next,
            show_back=bool(run.history.steps),
            show_plot_button=run.result_df is not None,
            sidebar=make_sidebar(request, run, run_name),
            end_of_run=end_of_run,
            show_table=show_table,
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
    section, step, _ = run.current_workflow_location()
    run.update_workflow_config([], update_params=False)

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


def change_dynamic_fields(request, run_name):
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

    dynamic_trigger_value = request.POST["selected_input"]
    dynamic_trigger_key = request.POST["key"]
    all_parameters_dict = get_parameters(run, run.section, run.step, run.method)
    dynamic_trigger_param_dict = all_parameters_dict[dynamic_trigger_key]
    dynamic_fields = make_dynamic_fields(
        dynamic_trigger_param_dict, dynamic_trigger_value, all_parameters_dict, False
    )
    parameters = render_to_string(
        "runs/fields.html",
        context=dict(fields=dynamic_fields),
    )
    return JsonResponse(
        dict(
            parameters=parameters,
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

        elif param_dict["fill"] == "enrichment_categories":
            named_output = selected[0]
            output_item = selected[1]

            # TODO: this is a bit hacky, but it works for now
            # should be refactored when we rework the named input handling
            # KeyError is expected here because named_output trigger change_field
            # twice to make sure that the categories are updated after the named_output has updated
            try:
                protein_itr = run.history.output_of_named_step(
                    named_output, output_item
                )
            except KeyError:
                protein_itr = None

            if (
                not isinstance(protein_itr, pd.DataFrame)
                or not "Gene_set" in protein_itr.columns
            ):
                param_dict["categories"] = []
            else:
                param_dict["categories"] = protein_itr["Gene_set"].unique().tolist()

        fields[key] = make_parameter_input(key, param_dict, parameters, disabled=False)

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
        if isinstance(p, dict) and "messages" in p:
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


def tables(request, run_name, index, key=None):
    if run_name not in active_runs:
        active_runs[run_name] = Run.continue_existing(run_name)
    run = active_runs[run_name]

    # use current output when applicable (not yet in history)
    if index < len(run.history.steps):
        outputs = run.history.steps[index].outputs
    else:
        outputs = run.current_out

    options = []
    for k, value in outputs.items():
        if isinstance(value, pd.DataFrame) and k != key:
            options.append(k)

    if key is None and options:
        # choose an option if url without key is used
        return HttpResponseRedirect(
            reverse("runs:tables", args=(run_name, index, options[0]))
        )

    return render(
        request,
        "runs/tables.html",
        context=dict(
            run_name=run_name,
            index=index,
            # put key as first option to make selected
            options=[(opt, opt) for opt in [key] + options],
            key=key,
        ),
    )


def tables_content(request, run_name, index, key):
    run = active_runs[run_name]
    if index < len(run.history.steps):
        outputs = run.history.steps[index].outputs[key]
    else:
        outputs = run.current_out[key]
    out = outputs.replace(np.nan, None)
    return JsonResponse(
        dict(columns=out.to_dict("split")["columns"], data=out.to_dict("split")["data"])
    )


def protein_plot(request, run_name):
    run = active_runs[run_name]
    section, step, method = run.current_run_location()
    # post_data = dict(request.POST)
    parameters = dict(request.POST)

    # print(request.__dict__)

    # param_dict = run.workflow_meta[section][step][method]["parameters"]
    # post_data, parameters = parameters_for_plot(post_data, param_dict)

    # parameters.update(parameters_from_post(post_data))

    print("parameters")
    print(parameters)
    call_params = run.exchange_named_outputs_with_data(parameters)
    import pprint

    pprint.pprint(call_params)

    graphml_file = call_params["graph_file_path"]
    # graphml_file = "/Users/anton/Documents/code/PROTzilla2/tests/test_data/exported_graphs/QXXXXX-s3.graphml"

    graph = nx.read_graphml(graphml_file)
    node_labels = nx.get_node_attributes(graph, "aminoacid")
    print(node_labels)

    pprint.pprint(graph.__dict__)

    nodes = [
        {
            "data": {
                "id": node,
                "label": graph.nodes[node].get("aminoacid", "####### BAAAAD #######"),
                "match": graph.nodes[node].get("match", "false"),
            }
        }
        for node in graph.nodes()
    ]
    edges = [{"data": {"source": u, "target": v}} for u, v in graph.edges()]
    elements = nodes + edges
    context = {"elements": elements}

    return render(request, "runs/protein_graph.html", context)
