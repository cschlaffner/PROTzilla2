from pathlib import Path

import pandas as pd
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from protzilla.run_helper import log_messages
from protzilla.run_v2 import Run, get_available_run_names
from protzilla.utilities.utilities import get_memory_usage, name_to_title
from protzilla.workflow import get_available_workflow_names
from ui.runs_v2.fields import make_displayed_history, make_method_dropdown, make_sidebar
from ui.runs_v2.views_helper import display_messages

from .form_mapping import get_empty_form_by_method, get_filled_form_by_request

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
        method_form = get_filled_form_by_request(request, run)
        if method_form.is_valid():
            method_form.submit(run)
    else:
        method_form = get_empty_form_by_method(run.steps.current_step, run)

    description = run.steps.current_step.method_description

    log_messages(run.steps.current_step.messages)
    display_messages(run.current_messages, request)

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

    show_table = not run.current_outputs.is_empty and any(
        isinstance(v, pd.DataFrame) for _, v in run.current_outputs
    )

    show_protein_graph = (
        run.current_outputs
        and "graph_path" in run.current_outputs
        and run.current_outputs["graph_path"] is not None
        and Path(run.current_outputs["graph_path"]).exists()
    )

    return render(
        request,
        "runs_v2/details.html",
        context=dict(
            run_name=run_name,
            section=run.steps.current_step.section,
            step=run.steps.current_step,
            display_name=f"{name_to_title(run.steps.current_step.section)} - {name_to_title(run.steps.current_step.step)}",
            displayed_history=make_displayed_history(
                run
            ),  # TODO: make NewRun compatible
            method_dropdown=make_method_dropdown(
                run,
                run.steps.current_step.section,
                run.steps.current_step.step,
                run.steps.current_step.method,
            ),
            name_field="",
            current_plots=current_plots,
            results_exist=not run.steps.current_step.output.is_empty,
            show_back=run.steps.current_step_index > 0,
            show_plot_button=not run.steps.current_step.output.is_empty,
            sidebar=make_sidebar(request, run),
            last_step=run.steps.current_step_index == len(run.steps.all_steps) - 1,
            end_of_run=False,  # TODO?
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
            "available_workflows": get_available_workflow_names(),
            "available_runs": get_available_run_names(),
        },
    )


# TODO: make NewRun compatible
def create(request: HttpRequest):
    """
    Creates a new run. The user is then redirected to the detail page of the run.

    :param request: the request object
    :type request: HttpRequest

    :return: the rendered details page of the new run
    :rtype: HttpResponse
    """
    run_name = request.POST["run_name"]
    run = Run(
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
    active_runs[run_name] = Run(run_name)

    return HttpResponseRedirect(reverse("runs_v2:detail", args=(run_name,)))


# this function is no longer used, as the Output instance of a step has a utility method not_empty
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
    run.step_next()
    return HttpResponseRedirect(reverse("runs_v2:detail", args=(run_name,)))


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
    run.step_previous()
    return HttpResponseRedirect(reverse("runs_v2:detail", args=(run_name,)))


# TODO port
def tables(request, run_name, index, key=None):
    return ""
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
