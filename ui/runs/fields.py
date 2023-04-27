import sys

from django.template.loader import render_to_string
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")
from protzilla.run_helper import get_parameters
from protzilla.workflow_helper import get_all_steps


def make_current_fields(run, section, step, method):
    parameters = get_parameters(run, section, step, method)
    current_fields = []
    for key, param_dict in parameters.items():
        current_fields.append(make_parameter_input(key, param_dict, disabled=False))

    return current_fields


def make_parameter_input(key, param_dict, disabled):
    if param_dict["type"] == "numeric":
        template = "runs/field_number.html"
        if "step" not in param_dict:
            param_dict["step"] = "any"
    elif param_dict["type"] == "categorical":
        param_dict["multiple"] = param_dict.get("multiple", False)
        template = "runs/field_select.html"
    elif param_dict["type"] == "file":
        template = "runs/field_file.html"
    elif param_dict["type"] == "named_output":
        template = "runs/field_named.html"
    elif param_dict["type"] == "metadata_df" or param_dict["type"] == "peptide_df":
        template = "runs/field_empty.html"
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


def make_add_step_dropdown(run, section):
    template = "runs/field_select.html"

    steps = list(run.workflow_meta[section].keys())
    steps.insert(0, "")

    return render_to_string(
        template,
        context=dict(
            name="add step:",
            type="categorical",
            categories=steps,
            key="step_to_be_added",
        ),
    )


def make_plot_fields(run, section, step, method):
    plots = run.workflow_meta[section][step][method].get("graphs", [])
    plot_fields = []
    for plot in plots:
        for key, param_dict in plot.items():
            if method in run.current_plot_parameters:
                param_dict["default"] = run.current_plot_parameters[method][key]
            plot_fields.append(make_parameter_input(key, param_dict, disabled=False))
    return plot_fields


def make_method_dropdown(run, section, step, method):
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
                param_dict["default"] = history_step.parameters[key]
                if param_dict["type"] == "named_output":
                    param_dict["steps"] = [param_dict["default"][0]]
                    param_dict["outputs"] = [param_dict["default"][1]]
                fields.append(make_parameter_input(key, param_dict, disabled=True))
        displayed_history.append(
            dict(
                display_name=name,
                fields=fields,
                plots=[p.to_html() for p in history_step.plots],
                section_heading=section_heading,
                name=run.history.step_names[i],
                index=i,
            )
        )
    return displayed_history


def make_name_field(allow_next, form):
    return render_to_string(
        "runs/field_text.html",
        context=dict(disabled=not allow_next, key="name", name="Name:", form=form),
    )


def make_highlighted_workflow_steps(run):
    workflow_steps = get_all_steps(run.workflow_config)
    highlighted_workflow_steps = [
        {"name": step, "highlighted": False} for step in workflow_steps
    ]
    highlighted_workflow_steps[run.step_index]["highlighted"] = True
    return highlighted_workflow_steps
