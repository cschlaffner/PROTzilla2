import logging
import subprocess
from pathlib import Path

import requests
from django.contrib import messages


def create_graph(protein_id: str, run_path: str, queue_size: int = None):
    path_to_protein_file, request = _get_protein_file(protein_id, run_path)

    if request is not None:
        if request.status_code != 200:
            msg = f"error while downloading protein file for {protein_id}.\
                         Statuscode:{request.status_code}, {request.reason}. \
                         Got: {request.text}. Tip: check if the ID is correct"
            return dict(
                raph_path=None,
                messages=[dict(level=messages.ERROR, msg=msg, trace=request.__dict__)],
            )

    output_folder = f"{run_path}/graphs"
    output_csv = f"{output_folder}/{protein_id}.csv"
    graph_path = f"{output_folder}/{protein_id}.graphml"
    cmd_str = f"protgraph -egraphml {path_to_protein_file} \
                --export_output_folder={output_folder} \
                --output_csv={output_csv}"
    subprocess.run(cmd_str, shell=True)

    msg = f"Graph created for protein {protein_id} at {graph_path} using {path_to_protein_file}"

    return dict(graph_path=graph_path, messages=[dict(level=messages.INFO, msg=msg)])


def _get_protein_file(protein_id, run_path) -> (str, requests.models.Response | None):
    protein_id = protein_id.upper()
    path_to_graphs = f"{run_path}/graphs"
    path_to_protein_file = f"{path_to_graphs}/{protein_id}.txt"
    url = f"https://rest.uniprot.org/uniprotkb/{protein_id}.txt"
    r = None

    if not Path(path_to_graphs).exists():
        Path(path_to_graphs).mkdir(parents=True, exist_ok=True)
    if Path(path_to_protein_file).exists():
        logging.info(
            f"Protein file {path_to_protein_file} already exists. Skipping download."
        )
    else:
        r = requests.get(url)
        if r.status_code == 200:
            with open(path_to_protein_file, "wb") as f:
                f.write(r.content)
        else:
            return "", r

    return path_to_protein_file, r
