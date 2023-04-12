import argparse

from protzilla.runner import Runner

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

runner = Runner(args)
