from itertools import zip_longest


def get_steps_of_workflow(
    workflow_config_dict,
) -> list[dict[str, str | list[dict[str, str]]]]:
    workflow_steps = []
    for section, steps in workflow_config_dict["sections"].items():
        workflow_steps.append(
            {
                "section": section,
                "steps": [
                    {"name": step["name"], "method": step["method"]}
                    for step in steps["steps"]
                ],
            }
        )
    return workflow_steps


def get_steps_of_workflow_meta(workflow_meta) -> list[dict[str, str | list[str]]]:
    workflow_steps = []
    for section, steps in workflow_meta.items():
        workflow_steps.append(
            {"section": section, "possible_steps": list(steps.keys())}
        )
    return workflow_steps


def step_name(step: str) -> str:
    """
    Returns the name of a step in a workflow. Exceptions where the .title() method is not enough are handled here.
    """
    if step == "ms_data_import":
        return "MS Data Import"
    else:
        return step.replace("_", " ").title()


def section_name(section):
    return section.replace("_", " ").title()


def method_name(workflow_meta, section, step, method):
    return workflow_meta[section][step][method]["name"]


def get_all_default_params_for_methods(workflow_meta, section, step, method):
    method_params = workflow_meta[section][step][method]["parameters"]
    return get_defaults(method_params)


def get_defaults(method_params):
    return {
        k: v["default"] if "default" in v.keys() else v
        for k, v in method_params.items()
    }


def get_parameter_type(workflow_meta, section, step, method, param):
    return workflow_meta[section][step][method]["parameters"][param]["type"]


def get_workflow_default_param_value(
    workflow_config, section, step, method, step_index_in_section, param
):
    step_dict = workflow_config["sections"][section]["steps"][step_index_in_section]
    if step_dict["name"] == step and step_dict["method"] == method:
        if param in step_dict["parameters"]:
            return step_dict["parameters"][param]
        elif param in step_dict:
            return step_dict[param]
        else:
            return None
    return None


def validate_workflow_parameters(workflow_config, workflow_meta):
    # checks if all parameters in workflow_config exist in workflow_meta
    for section, steps in workflow_config["sections"].items():
        for step in steps["steps"]:
            for param in step["parameters"]:
                if (
                    param
                    not in workflow_meta[section][step["name"]][step["method"]][
                        "parameters"
                    ]
                ):
                    raise ValueError(
                        f"Parameter {param} in step {step['name']} does not exist in workflow_meta"
                    )
                # TODO 96 test if value is in options when type catergorical or numeric
    return True


def validate_workflow_graphs(workflow_config, workflow_meta):
    # checks if all graphs and their parameters in workflow_config exist in workflow_meta
    for section, steps in workflow_config["sections"].items():
        for step in steps["steps"]:
            if "graphs" in step:
                step_meta = workflow_meta[section][step["name"]][step["method"]]
                for i, (graph_config, graph_meta) in enumerate(
                    zip_longest(step["graphs"], step_meta["graphs"], fillvalue={})
                ):
                    for param in graph_config:
                        if param not in graph_meta:
                            raise ValueError(
                                f"Graph parameter {param} in graph {i} in step {step['name']} does not exist in workflow_meta"
                            )
    return True


def set_output_name(workflow_config, section, step_index, output_name):
    workflow_config["sections"][section]["steps"][step_index][
        "output_name"
    ] = output_name
