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
import ui.runs_v2.form_mapping as form_map
from protzilla.run_v2 import Run
from protzilla.utilities import name_to_title
from protzilla.workflow import get_workflow_default_param_value, is_last_step_in_section
from ui.runs_v2.views_helper import get_displayed_steps


def make_current_fields(run: Run, section: str, step: str, method: str) -> list:
    """
    Wrapper method that generates the fields for the current method
    based on the data in the workflow_meta.json file.

    :param run: The current run object
    :param section: The current section
    :param step: The current step
    :param method: The current method

    :return: A list of fields for the current method
    """
    if not step:
        return []
    parameters = get_parameters(run, section, step, method)
    current_fields = []
    for key, param_dict in parameters.items():
        if "dynamic" in param_dict:
            continue
        current_fields.append(
            make_parameter_input(key, param_dict, parameters, disabled=False)
        )

    return current_fields


def make_parameter_input(
    key: str, param_dict: dict, all_parameters_dict: dict, disabled: bool
) -> str:
    """
    Generates the html for a single parameter input field. The
    type of the input field is determined by the type of the parameter as specified
    in the workflow_meta.json.
    May be called recursively by make_dynamic_fields if the parameter is a dynamic parameter.

    :param key: The name of the parameter, matches the key in the workflow_meta.json
    :param param_dict: The dictionary containing all meta information about the parameter e.g. type, default value
    :param all_parameters_dict: The dictionary containing all parameters for the current method with corresponding meta information
    :param disabled: Should the input field be disabled
    :return: The html for the input field
    """
    if param_dict["type"] == "numeric":
        param_dict["multiple"] = param_dict.get("multiple", False)
        template = "runs/field_number.html"
        if "step" not in param_dict:
            param_dict["step"] = "any"
    elif param_dict["type"] == "categorical":
        param_dict["multiple"] = param_dict.get("multiple", False)
        template = "runs/field_select.html"
    elif param_dict["type"] == "categorical_dynamic":
        template = "runs/field_select_dynamic.html"
        selected_category = param_dict["default"]
        dynamic_fields = make_dynamic_fields(
            param_dict, selected_category, all_parameters_dict, disabled
        )
        param_dict["dynamic_fields"] = dynamic_fields
    elif param_dict["type"] == "file":
        template = "runs/field_file.html"
    elif param_dict["type"] == "named_output":
        template = "runs/field_named.html"
    elif param_dict["type"] == "empty":
        template = "runs/field_empty.html"
    elif param_dict["type"] == "text":
        template = "runs/field_text.html"
    elif param_dict["type"] == "boolean":
        template = "runs/field_checkbox.html"
    elif param_dict["type"] == "multi_named_output":
        template = "runs/field_multi_named.html"
        param_dict["mapping_keys"] = list(param_dict["mapping"].keys())
    elif param_dict["type"] == "named_output_v2":
        template = "runs/named_output_v2.html"
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


def make_dynamic_fields(
    param_dict: dict, selected_category: str, all_parameters_dict: dict, disabled: bool
) -> list:
    """
    Generates the html for the dynamic fields of a "categorical_dynamic" type parameter.
    This is used to dynamically add fields based on the selected_category.

    :param param_dict: The dictionary containing all meta information about the parameter
        e.g. type, default value
    :param selected_category: The currently selected category of the field described by param_dict
    :param all_parameters_dict: The dictionary containing all parameters for the current method
        with corresponding meta information
    :param disabled: Should the fields be disabled
    :return: The html for the dynamic fields
    """
    dynamic_fields = []
    if selected_category in param_dict["dynamic_parameters"]:
        dynamic_parameters_list = param_dict["dynamic_parameters"][selected_category]
        for field_key in dynamic_parameters_list:
            field_dict = all_parameters_dict[field_key]
            dynamic_fields.append(
                make_parameter_input(
                    field_key, field_dict, all_parameters_dict, disabled
                )
            )
    return dynamic_fields


def make_sidebar(request, run: Run) -> str:
    """
    Renders the sidebar of the run detail page.

    :param request: The current http request
    :param run: The current run object
    :param run_name: The name of the current run

    :return: The html for the sidebar
    """
    csrf_token = request.META["CSRF_COOKIE"]
    template = "runs_v2/sidebar.html"
    return render_to_string(
        template,
        context=dict(
            csrf_token=csrf_token,
            workflow_steps=get_displayed_steps(run.steps),
            run_name=run.run_name,
        ),
    )


def make_plot_fields(run: Run, section: str, step: str, method: str) -> str:
    """
    Generates the html for the plot fields of the current method.
    This is only used when a plot is a part of a step and not its own step
    as is the case for the data preprocessing section.

    :param run: The current run object
    :param section: The current section
    :param step: The current step
    :param method: The current method

    :return: The html for the plot fields
    """
    if not step:
        return
    plots = run.workflow_meta[section][step][method].get("graphs", [])
    plot_fields = []
    for plot in plots:
        for key, param_dict in plot.items():
            if method in run.current_plot_parameters:
                param_dict["default"] = run.current_plot_parameters[method][key]
            plot_fields.append(
                make_parameter_input(key, param_dict, plot, disabled=False)
            )
    return plot_fields


def make_method_dropdown(
    run_name: str, section: str, step_name: str, step_id: str
) -> str:
    """
    Generates the html for the method dropdown of the current step.

    :param run: The current run object
    :param section: The current section
    :param step: The current step
    :param method: The current method

    :return: The html for the method dropdown
    """
    hierarchical_dict = form_map.generate_hierarchical_dict()
    methods = hierarchical_dict[section][step_name].values()
    method_names = [method.name for method in methods]

    methods = [method.__name__ for method in methods]
    return render_to_string(
        "runs_v2/method_dropdown.html",
        context=dict(
            key="chosen_method",
            name=f"{name_to_title(step_name)} Method:",
            default=step_id,
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
        name = f"{name_to_title(step.step)}: {step.name}"
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
        table_url = reverse("runs_v2:tables_nokey", args=(run.run_name, i))

        has_protein_graph = (
            "graph_path" in step.output
            and step.output["graph_path"] is not None
            and Path(step.output["graph_path"]).exists()
        )
        protein_graph_url = reverse("runs_v2:protein_graph", args=(run.run_name, i))

        displayed_history.append(
            dict(
                display_name=name,
                form=form,
                plots=plots,
                section_heading=section_heading,
                name=step.name,
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
    if end_of_run:
        return ""

    output_name = get_workflow_default_param_value(
        run.workflow_config,
        *run.current_run_location(),
        run.step_index_in_current_section(),
        "output_name",
    )

    if is_last_step_in_section(
        run.workflow_config, run.section, run.step_index_in_current_section()
    ):
        if not output_name and "output_name" in run.workflow_meta[run.section]:
            output_name = run.workflow_meta[run.section]["output_name"]
    else:
        if (
            "output_name" in run.workflow_meta[run.section]
            and output_name == run.workflow_meta[run.section]["output_name"]
        ):
            output_name = ""

    if not output_name:
        output_name = ""

    return render_to_string(
        "runs/field_name_output_text.html",
        context=dict(
            disabled=not allow_next,
            key="name",
            name="Name:",
            form=form,
            default=output_name,
        ),
    )
