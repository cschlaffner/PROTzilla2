import re

from django.contrib import messages

from protzilla.steps import StepManager
from protzilla.utilities import name_to_title
from ui.runs.utilities.alert import build_trace_alert
from ui.runs_v2.form_mapping import Mappings


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


def get_displayed_steps(steps: StepManager):
    possible_steps = Mappings.generate_hierarchical_dict()
    displayed_steps = []
    for section in possible_steps:
        workflow_steps = []
        global_index = 0

        for step in steps.all_steps_in_section(section):
            workflow_steps.append(
                {
                    "id": step.step,
                    "name": name_to_title(step.step),
                    "index": step.index,
                    "method_name": name_to_title(step.method),
                    "selected": step == steps.current_step,
                    "finished": step.index < steps.current_step_index,
                }
            )
            global_index = step.index

        displayed_steps.append(
            {
                "id": section,
                "name": name_to_title(section),
                "possible_steps": possible_steps[section],
                "steps": workflow_steps,
                "selected": steps.current_section() == section,
                "finished": global_index <= steps.current_step_index,
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
