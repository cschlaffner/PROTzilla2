
def get_all_steps(workflow_config_dict):
    workflow_steps = []
    for section, steps in workflow_config_dict["sections"].items():
        workflow_steps.extend(steps["steps"])
    return [step["name"] for step in workflow_steps]

def get_all_default_params_for_methods(workflow_meta, section, step, method):
    workflow_meta_step = workflow_meta[section][step]
    method_params = workflow_meta_step[method]["parameters"]
    return {k: v["default"] for k, v in method_params.items()}
