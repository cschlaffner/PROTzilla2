from ui.runs.fields import make_parameter_input


def parameters_from_post(post):
    d = dict(post)
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


def get_current_fields(run, section, step, method):
    parameters = run.workflow_meta[section][step][method]["parameters"]
    current_fields = []

    for key, param_dict in parameters.items():
        # todo use workflow default
        # todo 59 - restructure current_parameters
        param_dict = param_dict.copy()  # to not change workflow_meta
        if run.current_parameters is not None:
            param_dict["default"] = run.current_parameters[key]

        insert_special_params(param_dict, run)

        current_fields.append(make_parameter_input(key, param_dict, disabled=False))
    return current_fields


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

    pass
