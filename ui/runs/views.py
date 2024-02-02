import sys
import tempfile
import traceback
import zipfile
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from django.http import (
    FileResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")

from protzilla.constants.protzilla_logging import logger
from protzilla.data_integration.database_query import uniprot_columns
from protzilla.run import Run
from protzilla.run_helper import get_parameters
from protzilla.utilities import (
    clean_uniprot_id,
    get_memory_usage,
    name_to_title,
    unique_justseen,
)
from protzilla.workflow_helper import is_last_step
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
from ui.runs.views_helper import display_message, parameters_from_post

active_runs = {}


def index(request):
    """
    Renders the main index page of the PROTzilla application.

    :param request: the request object
    :type request: HttpRequest

    :return: the rendered index page
    :rtype: HttpResponse
    """
    return render(
        request,
        "runs/index.html",
        context={
            "available_workflows": Run.available_workflows(),
            "available_runs": Run.available_runs(),
        },
    )


def detail(request, run_name):
    """
    Renders the details page of a specific run.
    For rendering a context dict is created that contains all the dynamic information
    that is needed to display the page. This wraps other methods that provide subparts
    for the page e.g. make_displayed_history() to show the history.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: the rendered details page
    :rtype: HttpResponse
    """
    if run_name not in active_runs:
        active_runs[run_name] = Run.continue_existing(run_name)
    run = active_runs[run_name]
    section, step, method = run.current_run_location()
    end_of_run = not step
    last_step = is_last_step(run.workflow_config, run.step_index)
    description = run.workflow_meta[section][step][method]["description"]

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

    show_protein_graph = (
        run.current_out
        and "graph_path" in run.current_out
        and run.current_out["graph_path"] is not None
        and Path(run.current_out["graph_path"]).exists()
    )

    return render(
        request,
        "runs/details.html",
        context=dict(
            run_name=run_name,
            section=section,
            step=step,
            display_name=f"{name_to_title(run.step)}",
            displayed_history=make_displayed_history(run),
            method_dropdown=make_method_dropdown(run, section, step, method),
            fields=make_current_fields(run, section, step, method),
            plot_fields=make_plot_fields(run, section, step, method),
            name_field=make_name_field(results_exist(run), run, end_of_run),
            current_plots=current_plots,
            results_exist=results_exist(run),
            show_back=bool(run.history.steps),
            show_plot_button=run.result_df is not None,
            sidebar=make_sidebar(request, run, run_name),
            last_step=last_step,
            end_of_run=end_of_run,
            show_table=show_table,
            used_memory=get_memory_usage(),
            show_protein_graph=show_protein_graph,
            description=description,
        ),
    )


def change_method(request, run_name):
    """
    Changes the method during a step of a run.
    This is called when the user selects a new method in the first dropdown of a step.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: a JSON response object containing the new fields for the selected method
    :rtype: JsonResponse
    """
    # TODO 92 extract into a separate method like try_reactivate_run
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
    """
    Renders fields that depend on the value of another field e.g. a dropdown, the value
    being the dynamic_trigger_value below. The field is specified by its key and part of
    the request.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: a JSON response object containing the new fields depending on the value of
        the dynamic trigger
    :rtype: JsonResponse
    """

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
    return JsonResponse(dict(parameters=parameters), safe=False)


def change_field(request, run_name):
    """
    Changes the value of one or multiple fields during a method of a run depending on a
    selected value in another field. The field that triggers this method is identified by
    the post_id variable.
    In contrast to change_dynamic_fields, this method changes the value of the field itself
    instead of rendering new fields.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: a JSON response object containing the updated fields depending on the value of the
        dynamic trigger field
    :rtype: JsonResponse
    """
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
    if "fill_dynamic" in parameters[post_id]:
        fields_to_fill = parameters[post_id]["fill_dynamic"]
    else:
        fields_to_fill = [
            k for k in parameters.keys() if parameters[k]["type"] == "named_output_v2"
        ]

    fields = {}
    for key in fields_to_fill:
        param_dict = parameters[key]

        if "fill" in param_dict:
            if param_dict["fill"] == "metadata_column_data":
                param_dict["categories"] = run.metadata[selected[0]].unique().tolist()
            elif param_dict["fill"] == "uniprot_fields":
                param_dict["categories"] = uniprot_columns(selected[0]) + ["Links"]
            elif param_dict["fill"] == "protein_ids":
                if len(selected) == 1:
                    named_output = run.current_out_sources[selected[0]]
                    output_item = selected[0]
                else:
                    named_output = selected[0]
                    output_item = selected[1]
                # KeyError is expected when named_output triggers the fill
                try:
                    protein_iterable = run.history.output_of_named_step(
                        named_output, output_item
                    )
                except KeyError:
                    protein_iterable = None
                if isinstance(protein_iterable, pd.DataFrame):
                    param_dict["categories"] = protein_iterable["Protein ID"].unique()
                elif isinstance(protein_iterable, pd.Series):
                    param_dict["categories"] = protein_iterable.unique()
                elif isinstance(protein_iterable, list):
                    param_dict["categories"] = protein_iterable
                else:
                    param_dict["categories"] = []
                    print(
                        f"Warning: expected protein_iterable to be a DataFrame, Series or list, but got {type(protein_iterable)}. Proceeding with empty list."
                    )

            elif param_dict["fill"] == "protein_df_columns":
                named_output = selected[0]
                output_item = selected[1]
                # KeyError is expected when named_output triggers the fill
                try:
                    protein_iterable = run.history.output_of_named_step(
                        named_output, output_item
                    )
                except KeyError:
                    protein_iterable = None
                if isinstance(protein_iterable, pd.DataFrame):
                    categories = []
                    for column in protein_iterable.columns:
                        if column not in ["Protein ID", "Sample"]:
                            categories.append(column)
                    param_dict["categories"] = categories
                elif isinstance(protein_iterable, pd.Series):
                    param_dict["categories"] = protein_iterable.index
                else:
                    param_dict["categories"] = []
                    logger.warning(
                        f"Warning: expected protein_iterable to be a DataFrame or Series, but got {type(protein_iterable)}. Proceeding with empty list."
                    )

            elif param_dict["fill"] == "enrichment_categories":
                named_output = selected[0]
                output_item = selected[1]

                # TODO: this is a bit hacky, but it works for now
                # should be refactored when we rework the named input handling
                # KeyError is expected here because named_output trigger change_field
                # twice to make sure that the categories are updated after the named_output has updated
                try:
                    protein_iterable = run.history.output_of_named_step(
                        named_output, output_item
                    )
                except KeyError:
                    protein_iterable = None

                if (
                    not isinstance(protein_iterable, pd.DataFrame)
                    or not "Gene_set" in protein_iterable.columns
                ):
                    param_dict["categories"] = []
                else:
                    param_dict["categories"] = (
                        protein_iterable["Gene_set"].unique().tolist()
                    )
            elif param_dict["fill"] == "gsea_enrichment_categories":
                named_output = selected[0]
                output_item = selected[1]

                try:
                    protein_iterable = run.history.output_of_named_step(
                        named_output, output_item
                    )
                except KeyError:
                    protein_iterable = None

                if (
                    not isinstance(protein_iterable, pd.DataFrame)
                    or not "NES" in protein_iterable.columns
                ):
                    param_dict["categories"] = []
                else:
                    # gene_set_libraries are all prefixes for Term column in gsea output
                    # if no prefix is found, a single gmt file was used
                    gene_set_libraries = set()
                    for term in protein_iterable["Term"].unique():
                        if "__" in term:
                            gene_set_lib = term.split("__")[0]
                            gene_set_libraries.add(gene_set_lib)
                        else:
                            gene_set_libraries.add("all")
                    param_dict["categories"] = list(gene_set_libraries)

        elif "select_from" in param_dict:
            param_dict["outputs"] = run.history.output_keys_of_named_step(selected[0])

            for out_key in param_dict["outputs"]:
                run.current_out_sources[out_key] = selected[0]

        fields[key] = make_parameter_input(key, param_dict, parameters, disabled=False)

    return JsonResponse(fields, safe=False)


def create(request):
    """
    Creates a new run. The user is then redirected to the detail page of the run.

    :param request: the request object
    :type request: HttpRequest

    :return: the rendered details page of the new run
    :rtype: HttpResponse
    """
    run_name = request.POST["run_name"]
    run = Run.create(
        run_name,
        request.POST["workflow_config_name"],
        df_mode=request.POST["df_mode"],
    )
    active_runs[run_name] = run
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def continue_(request):
    """
    Continues an existing run. The user is redirected to the detail page of the run and
    can resume working on the run.

    :param request: the request object
    :type request: HttpRequest

    :return: the rendered details page of the run
    :rtype: HttpResponse
    """
    run_name = request.POST["run_name"]
    active_runs[run_name] = Run.continue_existing(run_name)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def next_(request, run_name):
    """
    Skips to and renders the next step/method of the run.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: the rendered detail page of the run with the next step/method
    :rtype: HttpResponse
    """
    run = active_runs[run_name]

    run.next_step(request.POST["name"])
    for message in run.current_messages:
        display_message(message, request)

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def back(request, run_name):
    """
    Goes back to and renders the previous step/method of the run.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: the rendered detail page of the run with the previous step/method
    :rtype: HttpResponse
    """
    run = active_runs[run_name]
    run.back_step()
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def add(request, run_name):
    """
    Adds a new method to the run. The method is added as the next step.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: the rendered detail page of the run, new method visible in sidebar
    :rtype: HttpResponse
    """
    run = active_runs[run_name]

    post = dict(request.POST)
    del post["csrfmiddlewaretoken"]
    step = post["step"][0]
    section = post["section_name"][0]
    method = post["method"][0]

    run.insert_at_next_position(step, section, method)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def delete_step(request, run_name):
    """
    Deletes a step/method from the run.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: the rendered detail page of the run, deleted method no longer visible in sidebar
    :rtype: HttpResponse
    """
    run = active_runs[run_name]

    post = dict(request.POST)
    del post["csrfmiddlewaretoken"]
    index = int(post["index"][0])
    section = post["section_name"][0]
    run.delete_step(section, index)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def export_workflow(request, run_name):
    """
    Exports the workflow of the run as a JSON file so that it can be reused and shared.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: the rendered detail page of the run
    :rtype: HttpResponse
    """
    run = active_runs[run_name]
    post = dict(request.POST)
    del post["csrfmiddlewaretoken"]
    print("run_name")
    print(run_name)
    name = post["name"][0]
    run.export_workflow(name)

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def calculate(request, run_name):
    """
    Performs the current methods calculation during the run. Django messages are used to
    display additional information, warnings and errors to the user.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: the rendered detail page of the run
    :rtype: HttpResponse
    """
    run = active_runs[run_name]
    parameters = parameters_from_post(request.POST)
    del parameters["chosen_method"]

    for k, v in dict(request.FILES).items():
        # assumption: only one file uploaded
        parameters[k] = v[0].temporary_file_path()
    run.perform_current_calculation_step(parameters)

    for message in run.current_messages:
        display_message(message, request)

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def plot(request, run_name):
    """
    Creates a plot from the current step/method of the run.
    This is only called by the plot button in the data preprocessing section aka when a plot is
    simultaneously a step on its own.
    Django messages are used to display additional information, warnings and errors to the user.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: the rendered detail page of the run, now with the plot
    :rtype: HttpResponse
    """
    run = active_runs[run_name]
    section, step, method = run.current_run_location()
    parameters = parameters_from_post(request.POST)

    if run.step == "plot":
        del parameters["chosen_method"]

    run.create_plot_from_current_location(parameters)

    for index, message in enumerate(run.current_messages):
        if isinstance(message, dict):
            display_message(message, request)

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def add_name(request, run_name):
    """
    Adds a name to the results of a calculated method of the run. The name can be used
    to identify the result and use them later.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: the rendered detail page of the run
    :rtype: HttpResponse
    """
    run = active_runs[run_name]
    run.name_step(int(request.POST["index"]), request.POST["name"])
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def results_exist(run: Run) -> bool:
    """
    Checks if the last step has produced valid results.

    :param run: the run to check

    :return: True if the results are valid, False otherwise
    """
    if run.section == "importing":
        return run.result_df is not None or (run.step == "plot" and run.plots)
    if run.section == "data_preprocessing":
        return run.result_df is not None or (run.step == "plot" and run.plots)
    if run.section == "data_analysis" or run.section == "data_integration":
        return run.calculated_method is not None or (run.step == "plot" and run.plots)
    return True


def results_exist_json(request, run_name):
    """
    Checks if the results of the run exist. This is used to determine if the Next button
    should be enabled or not.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: a JSON response with a boolean value
    :rtype: JsonResponse
    """
    run = active_runs[run_name]
    return JsonResponse(dict(results_exist=results_exist(run)))


def all_button_parameters(request, run_name):
    """
    Returns all parameters that are needed to render the buttons as enabled or disabled
    in the run detail page.
    See ui/runs/templates/runs/form_buttons.html for detailed documentation.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: a JSON response with the parameters
    :rtype: JsonResponse
    """
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
    """
    Returns the output keys of a named step of the run. This is used to determine which
    parameters can be used as input for future steps.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: a JSON response with the output keys
    :rtype: JsonResponse
    """
    run = active_runs[run_name]
    step_name = request.POST["step_name"]
    return JsonResponse(run.history.output_keys_of_named_step(step_name), safe=False)


def download_plots(request, run_name):
    """
    Downloads all plots of the current method in the run. If multiple plots are created,
    they are zipped together. The format of the plots is specified in the request.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: a FileResponse with the plots
    :rtype: FileResponse
    """
    run = active_runs[run_name]
    format_ = request.GET["format"]
    exported = run.export_plots(format_=format_)
    if len(exported) == 1:
        filename = f"{run.step_index}-{run.section}-{run.step}-{run.method}.{format_}"
        return FileResponse(exported[0], filename=filename, as_attachment=True)

    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_filename = f.name
    with zipfile.ZipFile(temp_filename, "w") as zf:
        for i, plot in enumerate(exported):
            filename = (
                f"{run.step_index}-{run.section}-{run.step}-{run.method}-{i}.{format_}"
            )
            zf.writestr(filename, plot.getvalue())
    return FileResponse(
        open(temp_filename, "rb"),
        filename=f"{run.step_index}-{run.section}-{run.step}-{run.method}-{format_}.zip",
        as_attachment=True,
    )


def tables(request, run_name, index, key=None):
    if run_name not in active_runs:
        active_runs[run_name] = Run.continue_existing(run_name)
    run = active_runs[run_name]

    # use current output when applicable (not yet in history)
    if index < len(run.history.steps):
        history_step = run.history.steps[index]
        outputs = history_step.outputs
        section = history_step.section
        step = history_step.step
        method = history_step.method
        name = run.history.step_names[index]
    else:
        outputs = run.current_out
        section = run.section
        step = run.step
        method = run.method
        name = None

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
            section=section,
            step=step,
            method=method,
            name=name,
            clean_ids="clean-ids" if "clean-ids" in request.GET else "",
        ),
    )


def tables_content(request, run_name, index, key):
    run = active_runs[run_name]
    if index < len(run.history.steps):
        outputs = run.history.steps[index].outputs[key]
    else:
        outputs = run.current_out[key]
    out = outputs.replace(np.nan, None)

    if "clean-ids" in request.GET:
        for column in out.columns:
            if "protein" in column.lower():
                out[column] = out[column].map(
                    lambda group: ";".join(
                        unique_justseen(map(clean_uniprot_id, group.split(";")))
                    )
                )
    return JsonResponse(
        dict(columns=out.to_dict("split")["columns"], data=out.to_dict("split")["data"])
    )


def protein_graph(request, run_name, index: int):
    run = active_runs[run_name]

    if index < len(run.history.steps):
        outputs = run.history.steps[index].outputs
    else:
        outputs = run.current_out

    if "graph_path" not in outputs:
        return HttpResponseBadRequest(
            f"No Graph Path found in output of step with index {index}"
        )

    graph_path = outputs["graph_path"]
    peptide_matches = outputs.get("peptide_matches", [])
    peptide_mismatches = outputs.get("peptide_mismatches", [])
    protein_id = outputs.get("protein_id", "")

    if not Path(graph_path).exists():
        return HttpResponseBadRequest(f"Graph file {graph_path} does not exist")

    graph = nx.read_graphml(graph_path)

    max_peptides = 0
    min_peptides = 0
    nodes = []

    # count number of peptides for each node, set max_peptides and min_peptides
    for node in graph.nodes():
        peptides = graph.nodes[node].get("peptides", "")
        if peptides != "":
            peptides = peptides.split(";")
            if len(peptides) > max_peptides:
                max_peptides = len(peptides)
            elif len(peptides) < min_peptides:
                min_peptides = len(peptides)
        nodes.append(
            {
                "data": {
                    "id": node,
                    "label": graph.nodes[node].get(
                        "aminoacid", "####### ERROR #######"
                    ),
                    "match": graph.nodes[node].get("match", "false"),
                    "peptides": graph.nodes[node].get("peptides", ""),
                    "peptides_count": len(peptides),
                }
            }
        )

    edges = [{"data": {"source": u, "target": v}} for u, v in graph.edges()]
    elements = nodes + edges

    return render(
        request,
        "runs/protein_graph.html",
        context={
            "elements": elements,
            "peptide_matches": peptide_matches,
            "peptide_mismatches": peptide_mismatches,
            "protein_id": protein_id,
            "filtered_blocks": outputs.get("filtered_blocks", []),
            "max_peptides": max_peptides,
            "min_peptides": min_peptides,
            "run_name": run_name,
            "used_memory": get_memory_usage(),
        },
    )
