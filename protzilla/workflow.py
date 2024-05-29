from itertools import zip_longest

from protzilla.constants import paths


def get_available_workflow_names() -> list[str]:
    if not paths.WORKFLOWS_PATH.exists():
        return []
    return [
        file.stem
        for file in paths.WORKFLOWS_PATH.iterdir()
        if not file.name.startswith(".") and not file.suffix == ".json"
    ]


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


def get_steps_amount_of_workflow(
    workflow_config_dict,
) -> int:
    amount = 0
    for section, steps in workflow_config_dict["sections"].items():
        amount += steps["steps"].__len__()

    return amount


def get_steps_of_workflow_meta(workflow_meta) -> list[dict[str, str | list[str]]]:
    workflow_steps = []
    for section, steps in workflow_meta.items():
        workflow_steps.append(
            {"section": section, "possible_steps": list(steps.keys())}
        )
    return workflow_steps


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


def get_global_index_of_step(workflow_config, section: str, step_index_in_section: int):
    """
    Get the global index of a step in a workflow.

    :param workflow_config: The workflow config
    :param section: The section of the step
    :param step_index_in_section: The index of the step in the section
    """
    index = 0
    for s, steps in workflow_config["sections"].items():
        if s == section:
            return (
                index + step_index_in_section
                if step_index_in_section < steps["steps"].__len__()
                else -1
            )
        index += steps["steps"].__len__()
    return -1


def is_last_step_in_section(workflow_config, section, step_index_in_section) -> bool:
    amount_steps_in_section = workflow_config["sections"][section]["steps"].__len__()
    return amount_steps_in_section <= step_index_in_section + 1


def is_last_step(workflow_config, index) -> bool:
    """
    Checks if the step is the last step in the workflow.

    :param workflow_config: The workflow config
    :param section: The section of the step
    :param index: The global index of the step
    """

    return get_steps_amount_of_workflow(workflow_config) <= index + 1


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
