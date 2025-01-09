import re

from django.contrib import messages

import ui.runs.form_mapping as form_map
from protzilla.steps import StepManager
from protzilla.utilities import name_to_title
from ui.runs.utilities.alert import build_trace_alert

from typing import Callable

SORTING_METHODS = {
    "name_asc": (lambda run: run["run_name"].lower(), False),
    "name_desc": (lambda run: run["run_name"].lower(), True),
    "created_asc": (lambda run: run["creation_date"], False),
    "created_desc": (lambda run: run["creation_date"], True),
    "last_modified_asc": (lambda run: run["modification_date"], False),
    "last_modified_desc": (lambda run: run["modification_date"], True),
    "memory_mode_asc": (lambda run: run["memory_mode"].lower(), False),
    "memory_mode_desc": (lambda run: run["memory_mode"].lower(), True),
}


def parameters_from_post(post):
    d = dict(post)
    if "csrfmiddlewaretoken" in d:
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
        return int(f) if int(f) == f else f
    except ValueError:
        if s == "checked":
            # s is a checkbox
            return True
        if re.fullmatch(r"\d+(\.\d+)?(\|\d+(\.\d+)?)*", s):
            # s is a multi-numeric input e.g. 1-0.12-5
            numbers_str = re.findall(r"\d+(?:\.\d+)?", s)
            numbers = []
            for num in numbers_str:
                num = float(num)
                num = int(num) if int(num) == num else num
                numbers.append(num)
            return numbers
        return s

def get_all_possible_step_names() -> list[str]:
    """
    Returns a list of names of step classes. Not to be confused with class display names.

    :return: List of names.
    :rtype: String
    """
    step_classes = form_map._forward_mapping.keys()
    step_names = []
    for step in step_classes:
        step_names.append(
            step.__name__
        )
    return step_names


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
                    "section": step.section,
                    "method_name": step.display_name,
                    "selected": step == steps.current_step,
                    "finished": index_global < steps.current_step_index,
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
            }
        )
    return displayed_steps

def filter_for_name(runs, search_string) -> list[dict[str, str | list[str]]]:
    return [run for run in runs if search_string in run["run_name"]]

def filter_for_steps(runs, search_steps) -> list[dict[str, str | list[str]]]:
    # get step display names
    step_classes = form_map._forward_mapping.keys()
    step_names = {}
    for step in step_classes:
        step_names[step.__name__] = step.display_name

    return [run for run in runs if all(step_names[step] in run["run_steps"] for step in search_steps)]

def filter_for_tags(runs, search_tags) -> list[dict[str, str | list[str]]]:
    return [run for run in runs if all(tag in run["run_tags"] for tag in search_tags)]

def filter_for_memory_mode(runs, memory_modes) -> list[dict[str, str | list[str]]]:
    internal_memory_modes = {"disk_memory": "standard", "disk": "low memory"}
    return [run for run in runs if internal_memory_modes.get(run["memory_mode"]) in memory_modes]

def filter_runs(runs, filters) -> list[dict[str, str | list[str]]]:
    """
    Filters runs according to the given filters.

    :param runs: List of runs.
    :param filters: List of filters.

    :return: List of runs.
    """
    if filters["name"]:
        runs = filter_for_name(runs, filters["name"])
    if filters["steps"]:
        runs = filter_for_steps(runs, filters["steps"])
    if filters["tags"]:
        runs = filter_for_tags(runs, filters["tags"])
    if filters["memory_mode"]:
        runs = filter_for_memory_mode(runs, filters["memory_mode"])
    return runs

def sort_runs(runs: list[dict[str, str | list[str]]], sorting_method: str):
    """
        Filters runs according to the given sorting method. Favorite and normal are handled seperately at the moment.

        :param runs: List of runs.
        :param sorting_method: One method as in dictionary SORTING_METHODS.

        :return: List of runs.
        """
    if sorting_method in SORTING_METHODS:
        key_func, reverse = SORTING_METHODS[sorting_method]  # Extract the key function and reverse flag
        runs = sorted(runs, key=key_func, reverse=reverse)
    return runs

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
