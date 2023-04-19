from itertools import zip_longest

import pandas as pd


def get_all_steps(workflow_config_dict) -> list[dict[str, list[str | dict[str, str]]]]:
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


def get_all_possible_steps(workflow_meta) -> list[dict[str, str | list[str]]]:
    workflow_steps = []
    for section, steps in workflow_meta.items():
        workflow_steps.append(
            {"section": section, "possible_steps": list(steps.keys())}
        )
    return workflow_steps


def get_step_name(step):
    return step.replace("_", " ").title()


def get_section_name(section):
    return section.replace("_", " ").title()


def get_method_name(workflow_meta, section, step, method):
    return workflow_meta[section][step][method]["name"]


def get_all_default_params_for_methods(workflow_meta, section, step, method):
    workflow_meta_step = workflow_meta[section][step]
    method_params = workflow_meta_step[method]["parameters"]
    return {k: v["default"] for k, v in method_params.items()}


def get_workflow_default_param_value(workflow_config, section, step, method, param):
    steps = workflow_config["sections"][section]["steps"]
    for step_dict in steps:
        if step_dict["name"] == step and step_dict["method"] == method:
            return (
                step_dict["parameters"][param]
                if param in step_dict["parameters"]
                else None
            )
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
