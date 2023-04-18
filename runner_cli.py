import argparse
import sys

from protzilla.runner import Runner


def args_parser():
    parser = argparse.ArgumentParser(
        argument_default=None,
        description="perform a protzilla-workflow on the provided MS Data",
        prog="PROTzilla Runner",
        epilog="Thanks for using PROTzilla! :)",
    )

    # paths to files have to be supplied in quotes on the command line
    parser.add_argument(
        "workflow",
        action="store",
        help="name of a workflow, saved in /user_data/workflows",
    )
    parser.add_argument(
        "msDataPath",
        action="store",
        help='path to the dataset you want to compute, provide like "<path>"',
    )
    parser.add_argument(
        "--metaDataPath", action="store", help="path to the metadata for your dataset"
    )
    parser.add_argument(
        "-n",
        "--name",
        action="store",
        help="Name of the run. If not provided a random name will be assigned",
    )
    parser.add_argument("-d", "--dfMode", action="store", help="disk or memory")
    parser.add_argument(
        "-p",
        "--allPlots",
        action="store_true",
        help="create all plots and save them to user_data/runs/<runName>/plots, default: false",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="when provided, all Parsed Arguments will be shown",
    )
    return parser


def main(raw_args):
    parser = args_parser()
    args = parser.parse_args(raw_args)
    print("raw:", raw_args)
    runner = Runner(args)
    runner.compute_workflow()


if __name__ == "__main__":
    main(sys.argv[1:])
