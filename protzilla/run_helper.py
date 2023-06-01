import copy

import gseapy as gp
import restring

from protzilla.workflow_helper import get_workflow_default_param_value


def insert_special_params(param_dict, run):
    if (
        param_dict["type"] == "named_output"
        or param_dict["type"] == "named_output_with_fields"
    ):
        param_dict["steps"] = [name for name in run.history.step_names if name]
        if param_dict.get("optional", False):
            param_dict["steps"].append("None")

        if (
            "default" in param_dict
            and param_dict["default"]
            and param_dict["default"][0] in param_dict["steps"]
        ):
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
        elif param_dict["fill"] == "dbs_restring":
            param_dict["categories"] = restring.settings.file_types
        elif param_dict["fill"] == "dbs_gseapy":
            param_dict["categories"] = gp.get_library_name()

    if "fill_dynamic" in param_dict:
        param_dict["class"] = "dynamic_trigger"

    if param_dict.get("default_select_all", False):
        param_dict["default"] = list(param_dict.get("categories", []))


def get_parameters(run, section, step, method):
    """constructs a dict with all parameters, inserts the correct defaults
    and handles special parameter types"""
    # deepcopy to not change run.workflow_meta
    parameters = copy.deepcopy(run.workflow_meta[section][step][method]["parameters"])
    output = {}

    for key, param_dict in parameters.items():
        workflow_default = get_workflow_default_param_value(
            run.workflow_config, section, step, method, key
        )
        if method in run.current_parameters and key in run.current_parameters[method]:
            param_dict["default"] = run.current_parameters[method][key]
        elif workflow_default is not None:
            param_dict["default"] = workflow_default

        insert_special_params(param_dict, run)
        output[key] = param_dict
    return output
