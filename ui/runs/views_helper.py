import re

from protzilla.workflow_helper import (
    get_steps_of_workflow,
    get_steps_of_workflow_meta,
    method_name,
    section_name,
    step_name,
)


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


def get_displayed_steps(workflow_config_dict, workflow_meta, step_index):
    workflow_steps = get_steps_of_workflow(workflow_config_dict)
    possible_steps = get_steps_of_workflow_meta(workflow_meta)
    displayed_steps = []
    global_index = 0
    for workflow_section, possible_section in zip(workflow_steps, possible_steps):
        assert workflow_section["section"] == possible_section["section"]
        section = possible_section["section"]
        section_selected = False
        workflow_steps = []
        global_finished = global_index < step_index
        for i, step in enumerate(workflow_section["steps"]):
            if global_index == step_index:
                section_selected = True
            global_finished = global_index < step_index
            workflow_steps.append(
                {
                    "id": step["name"],
                    "name": step_name(step["name"]),
                    "index": i,
                    "method_name": method_name(
                        workflow_meta, section, step["name"], step["method"]
                    ),
                    "selected": global_index == step_index,
                    "finished": global_index < step_index,
                }
            )
            global_index += 1
        section_finished = global_finished

        possible_steps = []
        for step in possible_section["possible_steps"]:
            methods = [
                {
                    "id": method,
                    "name": method_params["name"],
                    "description": method_params["description"],
                }
                for method, method_params in list(workflow_meta[section][step].items())
            ]
            possible_steps.append(
                {"id": step, "methods": methods, "name": step_name(step)}
            )

        displayed_steps.append(
            {
                "id": section,
                "name": section_name(section),
                "possible_steps": possible_steps,
                "steps": workflow_steps,
                "selected": section_selected,
                "finished": section_finished,
            }
        )
    return displayed_steps
