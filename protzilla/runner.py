import argparse

print("In module products __package__, __name__ ==", __package__, __name__)

import sys

print(sys.path)
print("In module products sys.path[0], __package__ ==", sys.path[0], __package__)

from .run import Run
from .utilities.random import random_string

parser = argparse.ArgumentParser(
    argument_default=argparse.SUPPRESS,
)

parser.add_argument("workflow", action="store")
parser.add_argument("ms-data-path", action="store")
parser.add_argument("--meta-data-path", action="store")
parser.add_argument("-n", "--name", action="store")
parser.add_argument("--df-mode", action="store")

args = parser.parse_args()
print("args:", args)

try:
    run_name = args.name
except AttributeError:
    run_name = f"runner_{random_string()}"
try:
    df_mode = args.df_mode
except AttributeError:
    df_mode = None

run = Run.create(
    run_name=run_name,
    workflow_config_name=args.workflow,
    df_mode=df_mode,
)

print(run.workflow_config)
