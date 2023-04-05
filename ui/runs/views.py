import sys

from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from main.settings import BASE_DIR

sys.path.append(f"{BASE_DIR}/..")
from protzilla.run import Run
from protzilla.workflow_manager import WorkflowManager

workflow_manager = WorkflowManager()
active_runs = {}


def index(request):
    return render(
        request,
        "runs/index.html",
        context={
            "run_name_prefill": f"hello{123:03d}",
            "available_workflows": workflow_manager.available_workflows,
            "available_runs": Run.available_runs(),
        },
    )


def make_parameter_input(key, param_dict, disabled):
    if param_dict["type"] == "numeric":
        template = "runs/field_number.html"
        if "step" not in param_dict:
            param_dict["step"] = "any"
    elif param_dict["type"] == "categorical":
        template = "runs/field_select.html"
    elif param_dict["type"] == "file":
        template = "runs/field_file.html"
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


def get_current_fields(run, section, step, method):
    parameters = run.workflow_meta[section][step][method]["parameters"]
    current_fields = []
    for key, param_dict in parameters.items():
        # todo use workflow default
        # todo 59 - restructure current_parameters
        if run.current_parameters is not None:
            param_dict["default"] = run.current_parameters.get(
                key, param_dict["default"]
            )

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
    plot_fields = make_plot_fields(run, section, step, method)
    displayed_history = []
    for history_step in run.history.steps:
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
                fields.append(make_parameter_input(key, param_dict, disabled=True))
            name = f"{history_step.section}/{history_step.step}/{history_step.method}"
        displayed_history.append(
            dict(
                name=name,
                fields=fields,
                plots=[p.to_html() for p in history_step.plots],
            )
        )

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
            current_plots=[plot.to_html() for plot in run.plots],
            # TODO add not able to plot when no plot method
            show_next=run.result_df is not None,
            show_back=bool(run.history.steps),
            show_plot_button=run.result_df is not None,
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
    run.next_step()
    return HttpResponseRedirect(reverse("runs:detail", args=(run_name,)))


def back(request, run_name):
    run = active_runs[run_name]
    run.back_step()
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


def parameters_from_post(post):
    d = dict(post)
    del d["csrfmiddlewaretoken"]
    parameters = {}
    for k, v in d.items():
        if len(v) > 1:
            raise ValueError(f"parameter {k} was used as a form key twice, values: {v}")
        parameters[k] = convert_str_if_possible(v[0])
    return parameters


def current_parameters(request, run_name):
    run = active_runs[run_name]
    if run.current_parameters is None or run.result_df is None:
        return JsonResponse(dict())
    d = run.current_parameters
    d["chosen_method"] = run.method
    return JsonResponse(d)


def current_plot_parameters(request, run_name):
    run = active_runs[run_name]
    if run.current_plot_parameters is None:
        return JsonResponse(dict())
    return JsonResponse(run.current_plot_parameters)


def results_exist(request, run_name):
    run = active_runs[run_name]
    d = dict(results_exist=run.result_df is not None)
    return JsonResponse(d)


def plotted_for_parameters(request, run_name):
    run = active_runs[run_name]
    if run.plotted_for_parameters is None:
        return JsonResponse(dict())
    return JsonResponse(run.plotted_for_parameters)


def convert_str_if_possible(s):
    try:
        f = float(s)
    except ValueError:
        return s
    return int(f) if int(f) == f else f
