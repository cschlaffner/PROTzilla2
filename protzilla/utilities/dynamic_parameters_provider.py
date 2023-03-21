def input_df(run):
    categories = []
    for step in run.history.steps:
        if step.section == "importing":
            continue
        categories.append(step.step_name + "_df")
        for output_key in step.outputs.keys():
            categories.append(step.step_name + output_key)
    return categories
