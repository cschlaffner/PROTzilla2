from itertools import zip_longest


def get_all_steps(workflow_config_dict) -> list[dict[str, list[str|dict[str, str]]]]:
    workflow_steps = []
    for section, steps in workflow_config_dict["sections"].items():
        workflow_steps.append(
            {"section": section, "steps": [{"name":step["name"], "method":step["method"]} for step in steps["steps"]]}
        )
    return workflow_steps


def get_all_possible_steps(workflow_meta) -> list[dict[str, list[str]]]:
    workflow_steps = []
    for section, steps in workflow_meta.items():
        workflow_steps.append(
            {"section": section, "possible_steps": list(steps.keys())}
        )
    return workflow_steps


def get_displayed_steps(workflow_config_dict, workflow_meta, step_index):
    workflow_steps = get_all_steps(workflow_config_dict)
    possible_steps = get_all_possible_steps(workflow_meta)
    displayed_steps = []
    index = 0
    for workflow_section, possible_section in zip(workflow_steps, possible_steps):
        assert workflow_section["section"] == possible_section["section"]
        section = possible_section["section"]
        section_selected = False
        workflow_steps = []
        for step in workflow_section["steps"]:
            if index == step_index:
                section_selected = True
            workflow_steps.append(
                {
                    "name": step["name"],
                    "method": step["method"],
                    "selected": index == step_index,
                    "display_name": step["name"].replace("_", " ").title(),
                    "finished": index < step_index,
                }
            )
            index += 1
        section_finished = index <= step_index

        possible_steps = []
        for step in possible_section["possible_steps"]:
            methods = [
                {
                    "method": method,
                    "name": method_params["name"],
                    "description": method_params["description"],
                }
                for method, method_params in list(workflow_meta[section][step].items())
            ]
            possible_steps.append(
                {
                    "name": step,
                    "methods": methods,
                    "display_name": step.replace("_", " ").title(),
                }
            )

        displayed_steps.append(
            {
                "section": section,
                "finished": section_finished,
                "possible_steps": possible_steps,
                "steps": workflow_steps,
                "selected": section_selected,
            }
        )
    print("displayed_steps")
    print(displayed_steps)
    return displayed_steps


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
