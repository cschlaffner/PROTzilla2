
def get_all_steps(workflow_config_dict):
    workflow_steps = []
    for section, steps in workflow_config_dict["sections"].items():
        workflow_steps.extend(steps["steps"])
    return [step["name"] for step in workflow_steps]