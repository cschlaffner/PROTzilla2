import io
import tempfile
import traceback
import zipfile
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render
from django.urls import reverse

from protzilla.run import Run, get_available_run_names
from protzilla.run_helper import log_messages
from protzilla.stepfactory import StepFactory
from protzilla.steps import Step
from protzilla.utilities.utilities import (
    check_is_path,
    format_trace,
    get_memory_usage,
    name_to_title,
)
from protzilla.workflow import get_available_workflow_names
from ui.runs.fields import (
    make_displayed_history,
    make_method_dropdown,
    make_name_field,
    make_sidebar,
)
from ui.runs.views_helper import display_message, display_messages, parameters_from_post

from .form_mapping import (
    get_empty_plot_form_by_method,
    get_filled_form_by_method,
    get_filled_form_by_request,
)

active_runs: dict[str, Run] = {}


def detail(request: HttpRequest, run_name: str):
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
        active_runs[run_name] = Run(run_name)
    run: Run = active_runs[run_name]

    # section, step, method = run.current_run_location()
    # end_of_run = not step

    if request.POST:
        method_form = get_filled_form_by_request(
            request, run
        )  # TODO maybe not do this as it is done after the calculation
        if method_form.is_valid():
            method_form.submit(run)
        plot_form = get_empty_plot_form_by_method(run.current_step, run)
        # in case the fill_form now would change it
        method_form.fill_form(run)
    else:
        method_form = get_filled_form_by_method(run.current_step, run)
        plot_form = get_empty_plot_form_by_method(run.current_step, run)

    description = run.current_step.method_description

    log_messages(run.current_step.messages)
    display_messages(run.current_messages, request)
    run.current_messages.clear()

    current_plots = []
    for plot in run.current_plots:
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

    show_table = (
        not run.current_outputs.is_empty
        and any(isinstance(v, pd.DataFrame) for _, v in run.current_outputs)
        or any(check_is_path(v) for _, v in run.current_outputs)
    )

    show_protein_graph = (
        run.current_outputs
        and "graph_path" in run.current_outputs
        and run.current_outputs["graph_path"] is not None
        and Path(run.current_outputs["graph_path"]).exists()
    )

    display_output_form = (
        run.steps.current_step.display_output is not None
        and not run.current_step.display_output.is_empty()
    )
    display_output_text = next(iter(run.current_step.display_output.display_output.values()), None)

    return render(
        request,
        "runs/details.html",
        context=dict(
            run_name=run_name,
            section=run.current_step.section,
            step=run.current_step,
            display_name=f"{name_to_title(run.current_step.operation)} - {run.current_step.display_name}",
            displayed_history=make_displayed_history(
                run
            ),  # TODO: make NewRun compatible
            method_dropdown=make_method_dropdown(
                run.run_name,
                run.current_step.section,
                run.current_step.operation,
                type(run.current_step).__name__,
            ),
            name_field=make_name_field(
                run.current_step.finished, run, False
            ),  # TODO end_of_run
            current_plots=current_plots,
            results_exist=run.current_step.finished,
            show_back=run.steps.current_step_index > 0,
            show_plot_button=run.current_step.finished,
            # TODO include plot exists and plot parameters match current plot or remove this and replace with results exist
            sidebar=make_sidebar(request, run),
            last_step=run.steps.current_step_index == len(run.steps.all_steps) - 1,
            end_of_run=False,  # TODO?
            show_table=show_table,
            used_memory=get_memory_usage(),
            show_protein_graph=show_protein_graph,
            description=description,
            method_form=method_form,
            is_form_dynamic=method_form.is_dynamic,
            plot_form=plot_form,
            display_output=display_output_form,
            display_output_result=display_output_text,
        ),
    )


def index(request: HttpRequest, index_error: bool = False):
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
            "available_workflows": get_available_workflow_names(),
            "available_runs": get_available_run_names(),
        },
    )


def create(request: HttpRequest):
    """
    Creates a new run. The user is then redirected to the detail page of the run.

    :param request: the request object
    :type request: HttpRequest

    :return: the rendered details page of the new run
    :rtype: HttpResponse
    """
    run_name = request.POST["run_name"]
    try:
        run = Run(
            run_name,
            request.POST["workflow_config_name"],
            df_mode=request.POST["df_mode"],
        )
    except Exception as e:
        display_message(
            {
                "level": 40,
                "msg": "Something went wrong creating a new run.",
                "trace": format_trace(traceback.format_exception(e)),
            },
            request,
        )
        traceback.print_exc()
        return HttpResponseRedirect(reverse("runs:index"))

    active_runs[run_name] = run
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def continue_(request: HttpRequest):
    """
    Continues an existing run. The user is redirected to the detail page of the run and
    can resume working on the run.

    :param request: the request object
    :type request: HttpRequest

    :return: the rendered details page of the run
    :rtype: HttpResponse
    """
    run_name = request.POST["run_name"]
    active_runs[run_name] = Run(run_name)

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
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]
    name = request.POST.get("name", None)
    if name:
        run.steps.name_current_step_instance(name)
    run.step_next()

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
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]
    run.step_previous()
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
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]
    parameters = parameters_from_post(request.POST)

    if run.current_step.display_name == "plot":
        del parameters["chosen_method"]
        run.step_calculate(parameters)
    else:
        run.current_step.plot(parameters)

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def tables(request, run_name, index, key=None):
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]

    # TODO this will change with the update to df_mode
    # use current output when applicable (not yet in history)
    if index < len(run.steps.previous_steps):
        outputs = run.steps.previous_steps[index].output
        section = run.steps.previous_steps[index].section
        step = run.steps.previous_steps[index].operation
        method = run.steps.previous_steps[index].display_name
    else:
        outputs = run.current_outputs
        section = run.current_step.section
        step = run.current_step.operation
        method = run.current_step.display_name

    options = []
    for k, value in outputs:
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
            clean_ids="clean-ids" if "clean-ids" in request.GET else "",
        ),
    )


def add(request: HttpRequest, run_name: str):
    """
    Adds a new method to the run. The method is added as the next step.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: the rendered detail page of the run, new method visible in sidebar
    :rtype: HttpResponse
    """
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]
    method = dict(request.POST)["method"][0]

    step = StepFactory.create_step(method, run.steps)
    run.step_add(step)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def export_workflow(request: HttpRequest, run_name: str):
    """
    Exports the workflow of the run as a JSON file.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: the rendered detail page of the run
    :rtype: HttpResponse
    """
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]
    requested_workflow_name = request.POST["name"]
    run._workflow_export(requested_workflow_name)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def download_plots(request: HttpRequest, run_name: str):
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
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]
    format_ = request.GET["format"]
    index = run.steps.current_step_index
    section = run.current_step.section
    operation = run.current_step.operation
    exported = run.current_plots.export(format_=format_)
    if len(exported) == 1:
        filename = f"{index}-{section}-{operation}.{format_}"
        return FileResponse(exported[0], filename=filename, as_attachment=True)

    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_filename = f.name
    with zipfile.ZipFile(temp_filename, "w") as zf:
        for i, plot in enumerate(exported):
            filename = f"{index}-{section}-{operation}-{i}.{format_}"
            zf.writestr(filename, plot.getvalue())
    return FileResponse(
        open(temp_filename, "rb"),
        filename=f"{index}-{section}-{operation}.zip",
        as_attachment=True,
    )


def delete_step(request: HttpRequest, run_name: str):
    """
    Deletes a step/method from the run.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: the rendered detail page of the run, deleted method no longer visible in sidebar
    :rtype: HttpResponse
    """
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]

    post = dict(request.POST)
    index = int(post["index"][0])
    section = post["section"][0]

    run.step_remove(step_index=index, section=section)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def navigate(request, run_name: str):
    """
    Navigates to a specific step/method of the run.

    :param request: the request object
    :param run_name: the name of the run

    :return: the rendered detail page of the run with the specified step/method
    """
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]

    post = dict(request.POST)
    index = int(post["index"][0])
    section_name = post["section_name"][
        0
    ]  # TODO can this be done without the section_name, like with the delete_step method?

    run.step_goto(index, section_name)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def tables_content(request, run_name, index, key):
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]
    # TODO this will change with df_mode implementation
    if index < len(run.steps.previous_steps):
        outputs = run.steps.previous_steps[index].output[key]
    else:
        outputs = run.current_outputs[key]
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

    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]
    chosen_method = request.POST["chosen_method"]
    run.step_change_method(chosen_method)

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def protein_graph(request, run_name, index: int):
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]

    outputs = run.current_outputs

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


def fill_form(request: HttpRequest, run_name: str):
    """
    Fills the form of the current step with the correct values.

    :param request: the request object
    :type request: HttpRequest
    :param run_name: the name of the run
    :type run_name: str

    :return: the filled form
    :rtype: HttpResponse
    """
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]
    method_form = get_filled_form_by_request(request, run)
    form_html = ""
    for field in method_form:
        form_html += f"<div>{field.label_tag()} {field}</div>"

    return HttpResponse(form_html)


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
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]
    run.name_step(int(request.POST["index"]), request.POST["name"])
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def download_table(request, run_name, index, key):
    if run_name not in active_runs:
        active_runs[run_name] = Run(run_name)
    run = active_runs[run_name]

    instance_id = run.steps.all_steps[index].instance_identifier
    buffer = io.StringIO()
    df: pd.DataFrame = run.steps.get_step_output(
        Step, key, instance_id, include_current_step=True
    )
    df.to_csv(buffer)

    buffer.seek(0)
    csv_bytes = buffer.getvalue()

    return FileResponse(csv_bytes, content_type="text/csv")
