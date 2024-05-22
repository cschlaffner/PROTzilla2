"""
Module for generating the html for the fields of the run detail page.
"""
import sys
from pathlib import Path

import pandas
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")
import ui.runs.form_mapping as form_map
from protzilla.run_v2 import Run
from protzilla.utilities import name_to_title
from ui.runs.views_helper import get_displayed_steps


def make_sidebar(request, run: Run) -> str:
    """
    Renders the sidebar of the run detail page.

    :param request: The current http request
    :param run: The current run object
    :param run_name: The name of the current run

    :return: The html for the sidebar
    """
    csrf_token = request.META["CSRF_COOKIE"]
    template = "runs/sidebar.html"
    return render_to_string(
        template,
        context=dict(
            csrf_token=csrf_token,
            workflow_steps=get_displayed_steps(run.steps),
            run_name=run.run_name,
        ),
    )


def make_method_dropdown(
    run_name: str, section: str, operation: str, display_name: str
) -> str:
    """
    Generates the html for the method dropdown of the current step.

    :param run: The current run object
    :param section: The current section
    :param operation: The current step
    :param display_name: The current method

    :return: The html for the method dropdown
    """
    hierarchical_dict = form_map.generate_hierarchical_dict()

    methods = hierarchical_dict[section][operation].values()
    method_names = [method.display_name for method in methods]

    methods = [method.__name__ for method in methods]
    return render_to_string(
        "runs/method_dropdown.html",
        context=dict(
            key="chosen_method",
            name=f"{name_to_title(operation)} Method:",
            default=display_name,
            categories=list(zip(methods, method_names)),
            run_name=run_name,
        ),
    )


def make_displayed_history(run: Run) -> str:
    """
    Generates the html for the displayed history that is displayed at the
    top of the current run.

    :param run: The current run object

    :return: The html for the displayed history
    """
    displayed_history = []

    for i, step in enumerate(run.steps.previous_steps):
        name = f"{step.display_name}: {step.instance_identifier}"
        section_heading = (
            name_to_title(step.section)
            if run.steps.all_steps[i - 1].section != step.section
            else None
        )

        form = form_map.get_filled_form_by_method(step, run, in_history=True)

        plots = []
        for plot in step.plots:
            if isinstance(plot, bytes):
                # Base64 encoded image
                plots.append(
                    '<div class="row d-flex justify-content-center mb-4"><img src="data:image/png;base64, {}"></div>'.format(
                        plot.decode("utf-8")
                    )
                )
            elif isinstance(plot, dict):
                if "plot_base64" in plot:
                    plots.append(
                        '<div class="row d-flex justify-content-center mb-4"><img id="{}" src="data:image/png;base64, {}"></div>'.format(
                            plot["key"], plot["plot_base64"].decode("utf-8")
                        )
                    )
                else:
                    plots.append(None)
            else:
                plots.append(plot.to_html(include_plotlyjs=False, full_html=False))

        has_df = any(
            isinstance(v, pandas.DataFrame) for _, v in step.output
        )  # TODO check if it is a str that has a path, if so it probably is a df and can be shown via table
        table_url = reverse("runs:tables_nokey", args=(run.run_name, i))

        has_protein_graph = (
            "graph_path" in step.output
            and step.output["graph_path"] is not None
            and Path(step.output["graph_path"]).exists()
        )
        protein_graph_url = reverse("runs:protein_graph", args=(run.run_name, i))

        displayed_history.append(
            dict(
                display_name=name,
                form=form,
                plots=plots,
                section_heading=section_heading,
                name=step.display_name,
                index=i,
                table_link=table_url if has_df else "",
                protein_graph_link=protein_graph_url if has_protein_graph else "",
            )
        )
    return displayed_history


def make_name_field(
    allow_next: bool, run: Run, end_of_run: bool, form: str = "runs_next"
) -> str:
    """
    Generates the html for the field that allows to name the output of the
    current method.

    :param allow_next: Whether the next button should be enabled
    :param form: The form that the field belongs to
    :param run: The current run object
    :param end_of_run: Whether the current step is the last step of the run

    :return: The html for the name field
    """

    current_instance_identifier = run.current_step.instance_identifier
    return render_to_string(
        "runs/field_name_output_text.html",
        context=dict(
            disabled=not allow_next,
            key="name",
            name="Name:",
            form=form,
            default=current_instance_identifier,
        ),
    )
