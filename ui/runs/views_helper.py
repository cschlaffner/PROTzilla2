from protzilla.workflow_helper import (
    get_all_possible_steps,
    get_all_steps,
    get_method_name,
    get_section_name,
    get_step_name,
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
    except ValueError:
        return s
    return int(f) if int(f) == f else f


def insert_special_params(param_dict, run):
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


def get_displayed_steps(workflow_config_dict, workflow_meta, step_index):
    workflow_steps = get_all_steps(workflow_config_dict)
    possible_steps = get_all_possible_steps(workflow_meta)
    displayed_steps = []
    global_index = 0
    for workflow_section, possible_section in zip(workflow_steps, possible_steps):
        assert workflow_section["section"] == possible_section["section"]
        section = possible_section["section"]
        section_selected = False
        workflow_steps = []
        for i, step in enumerate(workflow_section["steps"]):
            if global_index == step_index:
                section_selected = True
            workflow_steps.append(
                {
                    "id": step["name"],
                    "name": get_step_name(step["name"]),
                    "index": i,
                    "method_name": get_method_name(
                        workflow_meta, section, step["name"], step["method"]
                    ),
                    "selected": global_index == step_index,
                    "finished": global_index < step_index,
                }
            )
            global_index += 1
        section_finished = global_index <= step_index

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
                {"id": step, "methods": methods, "name": get_step_name(step)}
            )

        displayed_steps.append(
            {
                "id": section,
                "name": get_section_name(section),
                "possible_steps": possible_steps,
                "steps": workflow_steps,
                "selected": section_selected,
                "finished": section_finished,
            }
        )
    return displayed_steps
