import copy

import gseapy
import matplotlib.colors as mcolors
import restring

from protzilla.data_integration.database_query import uniprot_databases, uniprot_columns
from protzilla.workflow_helper import get_workflow_default_param_value


def insert_special_params(param_dict, run):
    if param_dict["type"] == "named_output":
        param_dict["steps"] = [name for name in run.history.step_names if name][::-1]
        if param_dict.get("optional", False):
            param_dict["steps"].append("None")

        if param_dict["default"] and param_dict["default"][0] in param_dict["steps"]:
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
            param_dict["categories"] = gseapy.get_library_name()
        elif param_dict["fill"] == "matplotlib_colors":
            param_dict["categories"] = mcolors.CSS4_COLORS
        elif param_dict["fill"] == "uniprot_fields":
            databases = uniprot_databases()
            if databases:
                # use the first database as a default, only used to initalize
                param_dict["categories"] = uniprot_columns(databases[0]) + ["Links"]
            else:
                param_dict["categories"] = ["Links"]
        elif param_dict["fill"] == "uniprot_databases":
            databases = uniprot_databases()
            param_dict["default"] = databases[0] if databases else ""
            param_dict["categories"] = databases

    if "fill_dynamic" in param_dict:
        param_dict["class"] = "dynamic_trigger"

    if param_dict.get("default_select_all", False):
        param_dict["default"] = list(param_dict.get("categories", []))

    if (
        param_dict["type"] == "numeric"
        and ("multiple" in param_dict and param_dict["multiple"])
        and isinstance(param_dict["default"], list)
    ):
        # The default value of a multiselect numeric input is saved as a list of
        # numbers, but it needs to be shown in the frontend in the format "1|2|0.12"
        param_dict["default"] = "|".join(str(num) for num in param_dict["default"])


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
