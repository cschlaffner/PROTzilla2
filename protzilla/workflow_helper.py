def get_all_steps(workflow_config_dict):
    workflow_steps = []
    for section, steps in workflow_config_dict["sections"].items():
        workflow_steps.extend(steps["steps"])
    return [step["name"] for step in workflow_steps]


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
    raise ValueError(
        f"Could not find method {method} in step {step} in section {section}"
    )
