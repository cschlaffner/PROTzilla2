import logging
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from django.contrib import messages


def create_graph(protein_id: str, run_path: str, queue_size: int = None):
    path_to_protein_file, msg = _get_protein_file(protein_id, run_path)

    if msg and path_to_protein_file is None:
        return dict(graph_path=None, messages=[dict(level=messages.ERROR, msg=msg)])

    output_folder = f"{run_path}/graphs"
    output_csv = f"{run_path}/graphs/{protein_id}.csv"
    graph_path = f"{run_path}/exported_graphs/{protein_id}.graphml"
    cmd_str = f"protgraph -egraphml {path_to_protein_file} --export_output_folder={output_folder} --output_csv={output_csv}"
    subprocess.run(cmd_str, shell=True)

    msg = f"Graph created for protein {protein_id} at {graph_path}"

    return dict(graph_path=graph_path, messages=[dict(level=messages.INFO, msg=msg)])


def _get_protein_file(protein_id, run_path) -> (str, str):
    protein_id = protein_id.upper()
    path_to_graphs = f"{run_path}/graphs"
    path_to_protein_file = f"{path_to_graphs}/{protein_id}.txt"
    url = f"https://rest.uniprot.org/uniprotkb/{protein_id}.txt"
    msg = ""

    if not Path(path_to_graphs).exists():
        Path(path_to_graphs).mkdir(parents=True, exist_ok=True)
    if Path(path_to_protein_file).exists():
        logging.info(
            f"Protein file {path_to_protein_file} already exists. Skipping download."
        )
    else:
        try:
            urllib.request.urlretrieve(url, path_to_protein_file)
        except urllib.error.URLError as e:
            msg = f"Error downloading protein {protein_id}. Error: {e}"
            logging.error(msg)

    return path_to_protein_file, msg


if __name__ == "__main__":
    create_graph("F1SN85", "test_run")
