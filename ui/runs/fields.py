import sys
from pathlib import Path

import pandas
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")
from protzilla.run_helper import get_parameters
from protzilla.workflow_helper import get_workflow_default_param_value, is_last_step_in_section
from ui.runs.views_helper import get_displayed_steps


def make_current_fields(run, section, step, method):
    """
    Wrapper method that generates the fields for the current method
    based on the data in the workflow_meta.json file.

    :param run: The current run object
    :type run: Run
    :param section: The current section
    :type section: str
    :param step: The current step
    :type step: str
    :param method: The current method
    :type method: str

    :return: A list of fields for the current method
    :rtype: list
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


def make_parameter_input(key, param_dict, all_parameters_dict, disabled):
    """
    Generates the html for a single parameter input field. The
    type of the input field is determined by the type of the parameter as specified
    in the workflow_meta.json.
    May be called recursively by make_dynamic_fields if the parameter is a dynamic parameter.

    :param key: The name of the parameter, matches the key in the workflow_meta.json
    :type key: str
    :param param_dict: The dictionary containing all meta information about the parameter
        e.g. type, default value
    :type param_dict: dict
    :param all_parameters_dict: The dictionary containing all parameters for the current method
        with corresponding meta information
    :type all_parameters_dict: dict
    :param disabled: Should the input field be disabled
    :type disabled: bool

    :return: The html for the input field
    :rtype: str
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


def make_dynamic_fields(param_dict, selected_category, all_parameters_dict, disabled):
    """
    Generates the html for the dynamic fields of a "categorical_dynamic" type parameter.
    This is used to dynamically add fields based on the selected_category.

    :param param_dict: The dictionary containing all meta information about the parameter
        e.g. type, default value
    :type param_dict: dict
    :param selected_category: The currently selected category of the field described by param_dict
    :type selected_category: str
    :param all_parameters_dict: The dictionary containing all parameters for the current method
        with corresponding meta information
    :type all_parameters_dict: dict
    :param disabled: Should the fields be disabled
    :type disabled: bool
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


def make_sidebar(request, run, run_name):
    """
    Renders the sidebar of the run detail page.

    :param request: The current request
    :type request: HttpRequest
    :param run: The current run object
    :type run: Run
    :param run_name: The name of the current run
    :type run_name: str

    :return: The html for the sidebar
    :rtype: str
    """
    csrf_token = request.META["CSRF_COOKIE"]
    template = "runs/sidebar.html"
    return render_to_string(
        template,
        context=dict(
            csrf_token=csrf_token,
            workflow_steps=get_displayed_steps(
                run.workflow_config, run.workflow_meta, run.step_index
            ),
            run_name=run_name,
        ),
    )


def make_plot_fields(run, section, step, method):
    """
    Generates the html for the plot fields of the current method.
    This is only used when a plot is a part of a step and not its own step
    as is the case for the data preprocessing section.

    :param run: The current run object
    :type run: Run
    :param section: The current section
    :type section: str
    :param step: The current step
    :type step: str
    :param method: The current method
    :type method: str

    :return: The html for the plot fields
    :rtype: str
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


def make_method_dropdown(run, section, step, method):
    """
    Generates the html for the method dropdown of the current step.

    :param run: The current run object
    :type run: Run
    :param section: The current section
    :type section: str
    :param step: The current step
    :type step: str
    :param method: The current method
    :type method: str

    :return: The html for the method dropdown
    :rtype: str
    """
    if not step:
        return ""
    methods = run.workflow_meta[section][step].keys()
    method_names = [run.workflow_meta[section][step][key]["name"] for key in methods]

    return render_to_string(
        "runs/field_select_with_label.html",
        context=dict(
            disabled=False,
            key="chosen_method",
            name=f"{step.replace('_', ' ').title()} Method:",
            default=method,
            categories=list(zip(methods, method_names)),
        ),
    )


def make_displayed_history(run):
    """
    Generates the html for the displayed history that is displayed at the
    top of the current run.

    :param run: The current run object
    :type run: Run

    :return: The html for the displayed history
    :rtype: str
    """
    displayed_history = []
    for i, history_step in enumerate(run.history.steps):
        fields = []
        # should parameters be copied, so workflow_meta won't change?
        parameters = run.workflow_meta[history_step.section][history_step.step][
            history_step.method
        ]["parameters"]
        name = f"{history_step.step.replace('_', ' ').title()}: {history_step.method.replace('_', ' ').title()}"
        section_heading = (
            history_step.section.replace("_", " ").title()
            if run.history.steps[i - 1].section != history_step.section
            else None
        )
        if history_step.section == "importing":
            fields = [""]
        else:
            for key, param_dict in parameters.items():
                if "dynamic" in param_dict:
                    continue
                if key == "proteins_of_interest" and key not in history_step.parameters:
                    history_step.parameters[key] = ["", ""]
                param_dict["default"] = (
                    history_step.parameters[key]
                    if key in history_step.parameters
                    else None
                )
                if param_dict["type"] == "named_output":
                    param_dict["steps"] = [param_dict["default"][0]]
                    param_dict["outputs"] = [param_dict["default"][1]]
                fields.append(
                    make_parameter_input(key, param_dict, parameters, disabled=True)
                )

        plots = []
        for plot in history_step.plots:
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
            isinstance(v, pandas.DataFrame) for v in history_step.outputs.values()
        )
        table_url = reverse("runs:tables_nokey", args=(run.run_name, i))

        has_protein_graph = (
            "graph_path" in history_step.outputs
            and history_step.outputs["graph_path"] is not None
            and Path(history_step.outputs["graph_path"]).exists()
        )
        protein_graph_url = reverse("runs:protein_graph", args=(run.run_name, i))

        displayed_history.append(
            dict(
                display_name=name,
                fields=fields,
                plots=plots,
                section_heading=section_heading,
                name=run.history.step_names[i],
                index=i,
                table_link=table_url if has_df else "",
                protein_graph_link=protein_graph_url if has_protein_graph else "",
            )
        )
    return displayed_history


def make_name_field(allow_next, form, run, end_of_run):
    """
    Generates the html for the field that allows to name the output of the
    current method.

    :param allow_next: Whether the next button should be enabled
    :type allow_next: bool
    :param form: The form that the field belongs to
    :type form: Form
    :param run: The current run object
    :type run: Run
    :param end_of_run: Whether the current step is the last step of the run
    :type end_of_run: bool

    :return: The html for the name field
    :rtype: str
    """
    if end_of_run:
        return ""

    output_name = ""
    if is_last_step_in_section(
        run.workflow_config,
        run.section,
        run.step_index_in_current_section()
    ):
        if 'output_name' in run.workflow_meta[run.section]:
            output_name = run.workflow_meta[run.section]["output_name"]

    workflow_output_name = get_workflow_default_param_value(
        run.workflow_config,
        *run.current_run_location(),
        run.step_index_in_current_section(),
        "output_name",
    )
    if workflow_output_name:
        output_name = workflow_output_name

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
