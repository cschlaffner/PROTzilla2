import argparse

from protzilla.runner import Runner

parser = argparse.ArgumentParser(
    argument_default=None,
)

# paths to files have to be supplied in quotes on the command line
parser.add_argument(
    "workflow", action="store", help="name of a workflow, saved in /user_data/workflows"
)
parser.add_argument(
    "msDataPath", action="store", help="path to the dataset you want to compute"
)
parser.add_argument(
    "--metaDataPath", action="store", help="path to the metadata for your dataset"
)
parser.add_argument("-n", "--name", action="store", help="Name of the run")
parser.add_argument("--dfMode", action="store", help="Disk or memory")
parser.add_argument(
    "-p",
    "--allPlots",
    action="store_true",
    help="create all plots and export them, default: false",
)

args = parser.parse_args()

runner = Runner(args)
