import sys

from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")
from protzilla import workflow_helper
from protzilla.run import Run

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


def get_current_fields(run, section, step, method):
    parameters = run.workflow_meta[section][step][method]["parameters"]
    current_fields = []

    for key, param_dict in parameters.items():
        # todo use workflow default
        # todo 59 - restructure current_parameters
        param_dict = param_dict.copy()  # to not change workflow_meta
        if run.current_parameters is not None:
            param_dict["default"] = run.current_parameters[key]
        # move into make_parameter_input?
        if param_dict["type"] == "named_output":
            param_dict["steps"] = [name for name in run.history.step_names if name]
            if param_dict["default"]:
                selected = param_dict["default"][0]
            else:
                selected = param_dict["steps"][0] if param_dict["steps"] else None
            param_dict["outputs"] = run.history.output_keys_of_named_step(selected)

        if "fill" in param_dict:
            if param_dict["fill"] == "metadata_columns":
                # Sample not needed for anova and t-test
                param_dict["categories"] = run.metadata.columns[
                    run.metadata.columns != "Sample"
                ].unique()
            elif param_dict["fill"] == "metadata_column_data":
                # per default fill with second column data since it is selected in dropdown
                param_dict["categories"] = run.metadata.iloc[:, 1].unique()

        if "fill_dynamic" in param_dict:
            param_dict["class"] = "dynamic_trigger"

        current_fields.append(make_parameter_input(key, param_dict, disabled=False))
    return current_fields


def make_plot_fields(run, section, step, method):
    plots = run.workflow_meta[section][step][method].get("graphs", [])
    plot_fields = []
    for plot in plots:
        for key, param_dict in plot.items():
            if run.current_plot_parameters is not None:
                param_dict["default"] = run.current_plot_parameters[key]
            plot_fields.append(make_parameter_input(key, param_dict, disabled=False))
    return plot_fields


def detail(request, run_name):
    if run_name not in active_runs:
        active_runs[run_name] = Run.continue_existing(run_name)
    run = active_runs[run_name]
    section, step, method = run.current_run_location()
    current_fields = get_current_fields(run, section, step, method)
    method_dropdown = render_to_string(
        "runs/field_select.html",
        context=dict(
            disabled=False,
            key="chosen_method",
            name=f"{step.replace('_', ' ').title()} Method:",
            default=method,
            categories=run.workflow_meta[section][step].keys(),
        ),
    )
    allow_next = run.result_df is not None
    name_field = render_to_string(
        "runs/field_text.html",
        context=dict(disabled=not allow_next, key="name", name="Name:"),
    )
    plot_fields = make_plot_fields(run, section, step, method)
    displayed_history = []
    for i, history_step in enumerate(run.history.steps):
        fields = []
        parameters = run.workflow_meta[history_step.section][history_step.step][
            history_step.method
        ]["parameters"]
        if history_step.section == "importing":
            name = f"{history_step.section}/{history_step.step}/{history_step.method}: {history_step.parameters['file_path'].split('/')[-1]}"
            df_head = (
                history_step.dataframe.head()
                if history_step.step == "ms_data_import"
                else run.metadata.head()
            )
            fields = [df_head.to_string()]
        else:
            for key, param_dict in parameters.items():
                param_dict["default"] = history_step.parameters[key]
                if param_dict["type"] == "named_output":
                    param_dict["steps"] = [param_dict["default"][0]]
                    param_dict["outputs"] = [param_dict["default"][1]]
                fields.append(make_parameter_input(key, param_dict, disabled=True))
            name = f"{history_step.section}/{history_step.step}/{history_step.method}"
        displayed_history.append(
            dict(
                location=name,
                fields=fields,
                plots=[p.to_html() for p in history_step.plots],
                name=run.history.step_names[i],
                index=i,
            )
        )

    workflow_steps = workflow_helper.get_all_steps(run.workflow_config)
    highlighted_workflow_steps = [
        {"name": step, "highlighted": False} for step in workflow_steps
    ]
    highlighted_workflow_steps[run.step_index]["highlighted"] = True
    return render(
        request,
        "runs/details.html",
        context=dict(
            run_name=run_name,
            location=f"{run.section}/{run.step}",
            displayed_history=displayed_history,
            method_dropdown=method_dropdown,
            fields=current_fields,
            plot_fields=plot_fields,
            name_field=name_field,
            current_plots=[plot.to_html() for plot in run.plots],
            # TODO add not able to plot when no plot method
            show_next=allow_next,
            show_back=bool(run.history.steps),
            show_plot_button=run.result_df is not None,
            sidebar_dropdown=make_add_step_dropdown(run, section),
            workflow_steps=highlighted_workflow_steps,
        ),
    )


def change_method(request, run_name):
    try:
        if run_name not in active_runs:
            active_runs[run_name] = Run.continue_existing(run_name)
        run = active_runs[run_name]
    except FileNotFoundError as e:
        print(str(e))
        response = JsonResponse({"error": f"Run '{run_name}' was not found"})
        response.status_code = 404  # not found
        return response
    run.method = request.POST["method"]
    run.current_parameters = None
    run.current_plot_parameters = None
    current_fields = get_current_fields(run, run.section, run.step, run.method)
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


def change_field(request, run_name):
    try:
        if run_name not in active_runs:
            active_runs[run_name] = Run.continue_existing(run_name)
        run = active_runs[run_name]
    except FileNotFoundError as e:
        print(str(e))
        response = JsonResponse({"error": f"Run '{run_name}' was not found"})
        response.status_code = 404  # not found
        return response

    id = request.POST["id"]
    selected = request.POST["selected"]
    parameters = run.workflow_meta[run.section][run.step][run.method]["parameters"]
    fields_to_fill = parameters[id]["fill_dynamic"]

    fields = {}
    for key in fields_to_fill:
        param_dict = parameters[key]
        if param_dict["fill"] == "metadata_column_data":
            param_dict["categories"] = run.metadata[selected].unique()
            fields[key] = make_parameter_input(key, param_dict, disabled=False)

    return JsonResponse(fields, safe=False)


def create(request):
    run_name = request.POST["run_name"]
    run = Run.create(
        run_name,
        request.POST["workflow_config_name"],
        df_mode="disk_memory",
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
    step = post["step_to_be_added"][0]

    if step == "":
        return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))

    run.insert_as_next_step(step)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def calculate(request, run_name):
    run = active_runs[run_name]
    section, step, method = run.current_run_location()
    parameters = parameters_from_post(request.POST)
    del parameters["chosen_method"]

    for k, v in dict(request.FILES).items():
        # assumption: only one file uploaded
        parameters[k] = v[0].temporary_file_path()
    run.perform_calculation_from_location(section, step, method, parameters)

    result = run.current_out
    if "messages" in result:
        for message in result["messages"]:
            trace = f"<br> Trace: {message['trace']}" if "trace" in message else ""
            messages.add_message(
                request, message["level"], f"{message['msg']}{trace}", message["level"]
            )

    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def plot(request, run_name):
    run = active_runs[run_name]
    section, step, method = run.current_workflow_location()
    parameters = parameters_from_post(request.POST)
    run.create_plot_from_location(section, step, method, parameters)
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def add_name(request, run_name):
    run = active_runs[run_name]
    run.history.name_step(int(request.POST["index"]), request.POST["name"])
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def parameters_from_post(post):
    d = dict(post)
    del d["csrfmiddlewaretoken"]
    parameters = {}
    for k, v in d.items():
        if len(v) > 1:
            # only used for named_output parameters and multiselect fields
            parameters[k] = v
        else:
            parameters[k] = convert_str_if_possible(v[0])
    return parameters


def convert_str_if_possible(s):
    try:
        f = float(s)
    except ValueError:
        return s
    return int(f) if int(f) == f else f


def outputs_of_step(request, run_name):
    run = active_runs[run_name]
    step_name = request.POST["step_name"]
    return JsonResponse(run.history.output_keys_of_named_step(step_name), safe=False)
