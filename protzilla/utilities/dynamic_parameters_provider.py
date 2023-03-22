def input_data_name(run):
    categories = []
    for step_index, step in enumerate(run.history.steps):
        if step.section == "importing":
            continue
        input_df_name = step.step_name + "_df"
        categories.append(input_df_name)
        for dropout_key in step.outputs.keys():
            input_dropout_name = step.step_name + "_" + dropout_key
            categories.append(input_dropout_name)
    return categories


def input_data_name_to_step_index(run):
    name_to_step_index = dict()
    for step_index, step in enumerate(run.history.steps):
        if step.section == "importing":
            continue
        input_df_name = step.step_name + "_df"
        name_to_step_index[input_df_name] = step_index
        for dropout_key in step.outputs.keys():
            input_dropout_name = step.step_name + "_" + dropout_key
            name_to_step_index[input_dropout_name] = step_index
    return name_to_step_index
