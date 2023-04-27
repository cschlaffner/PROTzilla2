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
        "ms_data_path",
        action="store",
        help='path to the dataset you want to compute, provide like "<path>"',
    )
    parser.add_argument(
        "--meta_data_path", action="store", help="path to the metadata for your dataset"
    )
    parser.add_argument(
        "--peptides_path", action="store", help="path to the peptides-dataset"
    )
    parser.add_argument(
        "-n",
        "--run_name",
        action="store",
        help="Name of the run. If not provided a random name will be assigned",
    )
    parser.add_argument("-d", "--df_mode", action="store", help="disk or memory")
    parser.add_argument(
        "-p",
        "--all_plots",
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
    kwargs = parser.parse_args(raw_args).__dict__
    runner = Runner(**kwargs)
    runner.compute_workflow()


if __name__ == "__main__":
    main(sys.argv[1:])
