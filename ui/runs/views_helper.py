import re

from django.contrib import messages
import numpy as np

import ui.runs.form_mapping as form_map
from protzilla.steps import StepManager
from protzilla.utilities import name_to_title
from ui.runs.utilities.alert import build_trace_alert


def get_displayed_steps(
    steps: StepManager,
) -> list[dict]:  # TODO i think this broke with the new naming scheme, should be redone
    possible_steps = form_map.generate_hierarchical_dict()
    displayed_steps = []
    index_global = 0
    for section in possible_steps:
        workflow_steps = []

        for index_in_section, step in enumerate(steps.all_steps_in_section(section)):
            workflow_steps.append(
                {
                    "id": step.operation,
                    "name": name_to_title(step.operation),
                    "index": index_in_section,
                    "index_global": index_global,
                    "section": step.section,
                    "method_name": step.display_name,
                    "selected": step == steps.current_step,
                    "finished": index_global < steps.current_step_index,
                    "calculation_icon_path": "img/" + step.calculation_status + "_icon.svg"
                }
            )

            index_global += 1

        possible_steps_in_section = []
        for operations in possible_steps[section]:
            methods = []
            for method, step_instance in possible_steps[section][operations].items():
                methods.append(
                    {
                        "id": method,
                        "name": step_instance.display_name,
                        "description": step_instance.method_description,
                    }
                )
            possible_steps_in_section.append(
                {
                    "id": operations,
                    "methods": methods,
                    "name": name_to_title(operations),
                }
            )

        displayed_steps.append(
            {
                "id": section,
                "name": name_to_title(section),
                "possible_steps": possible_steps_in_section,
                "steps": workflow_steps,
                "selected": steps.current_section == section,
                "finished": index_global - 1 < steps.current_step_index,
                "calculation_status": step.calculation_status,
            }
        )
    return displayed_steps


def display_message(message: dict, request):
    """
    Displays a message in the frontend.

    :param message: dict with keys "level", "msg" and optionally "trace" of the message to message
    :param request: request object
    """

    trace = ""
    if (
        "trace" in message
        and isinstance(message["trace"], str)
        and message["trace"] != ""
    ):
        trace = build_trace_alert(message["trace"])

    # map error level to bootstrap css class
    lvl_to_css_class = {
        40: "alert-danger",
        30: "alert-warning",
        20: "alert-info",
    }
    messages.add_message(
        request,
        message["level"],
        f"{message['msg']} {trace}",
        lvl_to_css_class[message["level"]],
    )


def display_messages(messages: list[dict], request):
    """
    Displays a list of messages in the frontend.

    :param messages: list with a dicts for each message to display containing keys "level", "msg" and optionally "trace"
    :param request: request object
    """
    for message in messages:
        display_message(message, request)


def clear_messages(request):
    """
    Clears all messages from the request object in the frontend.

    :param request: request object
    """
    storage = messages.get_messages(request)
    for message in messages.get_messages(request):
        pass
    storage.used = True


def get_filtered_data(run, index, key, reset=False):
    """
    Retrieves the corresponding output data and creates a copy for the filtered data in the data table

    :param run: the corresponding run
    :param index: the index of the current step
    :param key: the key of the datatable
    :param reset: the option to reload the real output data

    :return: a dict with the filtered data for the table 
    """
    if index < len(run.steps.previous_steps):
        if key not in run.steps.previous_steps[index].datatable_filtered_output or reset:
            outputs = run.steps.previous_steps[index].output[key]
            filtered_data = outputs.copy()
            filtered_data = filtered_data.replace(np.nan, None)
            run.steps.previous_steps[index].datatable_filtered_output[key] = filtered_data
        else:
            filtered_data = run.steps.previous_steps[index].datatable_filtered_output[key]
   
    else:
        if key not in run.current_filtered_data or reset:
            outputs = run.current_outputs[key]
            filtered_data = outputs.copy()
            filtered_data = filtered_data.replace(np.nan, None)
            run.current_filtered_data[key] = filtered_data
        else:
            filtered_data = run.current_filtered_data[key]

    return filtered_data

def set_filtered_data(run, index, key, filtered_data):
    """
    Saves the filtered data from the table
    
    :param run: the corresponding run
    :param index: the index of the current step
    :param key: the key of the datatable
    :param filtered_data: the filtered data from the table 
    """
    if index < len(run.steps.previous_steps):
        run.steps.previous_steps[index].datatable_filtered_output[key] = filtered_data
    else:
        run.current_filtered_data[key] = filtered_data