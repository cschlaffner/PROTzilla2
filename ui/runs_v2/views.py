from pathlib import Path

import pandas as pd
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from protzilla.run import Run
from protzilla.run_helper import log_messages
from protzilla.utilities.utilities import get_memory_usage, name_to_title
from protzilla.workflow_helper import is_last_step
from ui.runs.fields import (
    make_displayed_history,
    make_method_dropdown,
    make_name_field,
    make_sidebar,
)
from ui.runs.views_helper import display_messages

from .form_mapping import get_empty_form_by_method, get_filled_form_by_request

active_runs = {}


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
        active_runs[run_name] = Run.continue_existing(run_name)
    run = active_runs[run_name]
    section, step, method = run.current_run_location()
    end_of_run = not step

    last_step = is_last_step(run.workflow_config, run.step_index)

    if request.POST:
        method_form = get_filled_form_by_request(request, run)
        if method_form.is_valid():
            method_form.submit(run)
    else:
        method_form = get_empty_form_by_method(method, run)

    description = method_form.description

    log_messages(run.current_messages)
    display_messages(run.current_messages, request)
    run.current_messages = []

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
        "runs_v2/details.html",
        context=dict(
            run_name=run_name,
            section=section,
            step=step,
            display_name=f"{name_to_title(run.step)}",
            displayed_history=make_displayed_history(run),
            method_dropdown=make_method_dropdown(run, section, step, method),
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
            method_form=method_form,
            plot_form=None,
        ),
    )


def index(request: HttpRequest):
    """
    Renders the main index page of the PROTzilla application.

    :param request: the request object
    :type request: HttpRequest

    :return: the rendered index page
    :rtype: HttpResponse
    """
    return render(
        request,
        "runs_v2/index.html",
        context={
            "available_workflows": Run.available_workflows(),
            "available_runs": Run.available_runs(),
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
    run = Run.create(
        run_name,
        request.POST["workflow_config_name"],
        df_mode=request.POST["df_mode"],
    )
    active_runs[run_name] = run
    return HttpResponseRedirect(reverse("runs_v2:detail", args=(run_name,)))


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
    active_runs[run_name] = Run.continue_existing(run_name)

    return HttpResponseRedirect(reverse("runs_v2:detail", args=(run_name,)))


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
