import copy

import gseapy
import matplotlib.colors as mcolors
import restring

from protzilla.constants.protzilla_logging import MESSAGE_TO_LOGGING_FUNCTION
from protzilla.data_integration.database_query import (
    biomart_database,
    uniprot_columns,
    uniprot_databases,
)
from protzilla.workflow import get_workflow_default_param_value


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
        if "sorted" in param_dict and param_dict["sorted"]:
            param_dict["outputs"].sort()

    if param_dict["type"] == "multi_named_output":
        all_steps = [name for name in run.history.step_names if name][::-1]
        required_outputs = list(param_dict["mapping"].values())
        param_dict["steps"] = [
            step
            for step in all_steps
            if set(required_outputs).issubset(
                set(run.history.output_keys_of_named_step(step))
            )
        ]
        param_dict["class"] = "dynamic_trigger"

        try:
            for output_key in run.history.output_keys_of_named_step(
                param_dict["steps"][0]
            ):
                run.current_out_sources[output_key] = param_dict["steps"][0]
        except IndexError:
            pass

    if param_dict["type"] == "named_output_v2":
        param_dict["steps"] = [name for name in run.history.step_names if name][::-1]
        if param_dict["default"] and param_dict["default"][0] in param_dict["steps"]:
            selected = param_dict["default"][0]
        else:
            selected = param_dict["steps"][0] if param_dict["steps"] else None
        param_dict["outputs"] = run.history.output_keys_of_named_step(selected)
        if "sorted" in param_dict and param_dict["sorted"]:
            param_dict["outputs"].sort()

    if "fill" in param_dict:
        if param_dict["fill"] == "metadata_non_sample_columns":
            # Sample not needed for anova and t-test
            param_dict["categories"] = run.metadata.columns[
                run.metadata.columns != "Sample"
            ].unique()
        elif param_dict["fill"] == "metadata_unknown_columns":
            # give selection of existing columns without ["Sample", "Group", "Batch"]
            # as they are already named correctly for our purposes
            param_dict["categories"] = run.metadata.columns[
                ~run.metadata.columns.isin(["Sample", "Group", "Batch"])
            ].unique()
        elif param_dict["fill"] == "metadata_required_columns":
            # TODO add other possible metadata columns
            # exclude columns that are already in metadata and known to be required
            param_dict["categories"] = [
                col
                for col in ["Sample", "Group", "Batch"]
                if col not in run.metadata.columns
            ]
        elif param_dict["fill"] == "metadata_columns":
            param_dict["categories"] = run.metadata.columns.unique()
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
        elif param_dict["fill"] == "biomart_datasets":
            # retrieve datasets from BioMart server
            database = biomart_database("ENSEMBL_MART_ENSEMBL")
            # get the display names instead if the internal names, then map them back
            param_dict["categories"] = [
                database.datasets[dataset].display_name for dataset in database.datasets
            ]
            # param_dict["categories"] = database.datasets
        elif param_dict["fill"] == "protein_group_column":
            param_dict["categories"] = run.df["Protein ID"].unique()

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
        # allow for conditional parameters that are only shown if a certain condition
        # is met all parameters that depend on the condition need to have a "condition"
        # key and the fitting value
        if "condition" in param_dict:
            if param_dict["condition"] == "metadata":
                if not run.has_metadata:
                    continue
        workflow_default = get_workflow_default_param_value(
            run.workflow_config,
            section,
            step,
            method,
            run.step_index_in_current_section(),
            key,
        )
        if method in run.current_parameters and key in run.current_parameters[method]:
            param_dict["default"] = run.current_parameters[method][key]
        elif workflow_default is not None:
            param_dict["default"] = workflow_default

        insert_special_params(param_dict, run)
        output[key] = param_dict
    return output


def log_message(level: int = 40, msg: str = "", trace: str | list[str] = ""):
    """
    Logs a message to the console.

    :param level: The logging level of the message. See https://docs.python.org/3/library/logging.html#logging-levels
    :param msg: The message to log.
    :param trace: The trace to log.
    """
    log_function = MESSAGE_TO_LOGGING_FUNCTION.get(level)
    if log_function:
        if trace != "":
            trace = f"\nTrace: {trace}"
        log_function(f"{msg}{trace}")


def log_messages(messages: list[dict] = None):
    """
    Logs a list of messages to the console.

    :param messages: A list of messages to log, each message is a dict with the keys "level", "msg" and optional "trace".
    """
    if messages is None:
        messages = []
    for message in messages:
        log_message(
            message["level"],
            message["msg"],
            message["trace"] if "trace" in message else "",
        )
