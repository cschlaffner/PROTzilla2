from django.template.loader import render_to_string


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
    elif param_dict["type"] == "metadata_df":
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
            name="add step:\n",
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
            if run.current_plot_parameters is not None:
                param_dict["default"] = run.current_plot_parameters[key]
            plot_fields.append(make_parameter_input(key, param_dict, disabled=False))
    return plot_fields
