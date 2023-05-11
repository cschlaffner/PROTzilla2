import subprocess

from protzilla.constants.paths import TEST_DATA_PATH


def create_graph():
    cmd_str = f"protgraph -egml {TEST_DATA_PATH}/p53.txt --export_output_folder={TEST_DATA_PATH}/exported_graphs_test"
    subprocess.run(cmd_str, shell=True)


if __name__ == "__main__":
    create_graph()
