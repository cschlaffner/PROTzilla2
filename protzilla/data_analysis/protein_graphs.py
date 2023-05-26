import logging
import re
import subprocess
from pathlib import Path

import networkx as nx
import pandas as pd
import requests
from django.contrib import messages

from protzilla.constants.paths import RUNS_PATH


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
                --output_csv={output_csv}\
                -ft VARIANT -d skip"
    # -ft VAR_SEQ --no_merge

    subprocess.run(cmd_str, shell=True)

    msg = f"Graph created for protein {protein_id} at {graph_path} using {path_to_protein_file}"

    return dict(graph_path=graph_path, messages=[dict(level=messages.INFO, msg=msg)])


def peptides_to_isoform(
    peptide_df: pd.DataFrame, protein_id: str, graph_name: str, run_name: str
):
    df = peptide_df[peptide_df["Protein ID"].str.contains(protein_id)]
    df["Sequence"].tolist()

    protein_graph = nx.read_graphml(
        f"{RUNS_PATH}/{run_name}/graphs/{graph_name}.graphml"
    )
    # n0 is always the __start__ node in ProtGraph
    _create_graph_index(protein_graph, "n0")

    return


def _create_graph_index(protein_graph: nx.Graph, starting_point: str):
    """
    create a mapping from the position in the protein to the node in the graph
    TODO: this might be broken (in conjunction with the ref.-seq index) for versions where a ref.-seq is shorter than the longest path
    """
    longest_paths = _longest_paths(protein_graph, starting_point)

    seq_len = 0
    for node in protein_graph.nodes:
        if protein_graph.nodes[node]["aminoacid"] == "__end__":
            try:
                seq_len = int(protein_graph.nodes[node]["position"]) - 1
            except KeyError:
                # minimum number of amino acids is number of nodes - 2 (start and end)
                seq_len = protein_graph.number_of_nodes() - 2
                logging.info(
                    f"Set sequence length to {seq_len}, based on number of nodes"
                )
            finally:
                break

    index = [[] for i in range(seq_len)]
    for node in longest_paths:
        if (
            protein_graph.nodes[node]["aminoacid"] == "__start__"
            or protein_graph.nodes[node]["aminoacid"] == "__end__"
        ):
            continue

        for i in range(
            longest_paths[node],
            longest_paths[node] + len(protein_graph.nodes[node]["aminoacid"]),
        ):
            # needed because variations can make the longest path longer than
            # the reference sequence.
            # As calculating that is hard, we just append when needed
            if i >= len(index):
                for _ in range(len(index), i + 1):
                    index.append([])
            index[i].append(node)

    return index


def _create_ref_seq_index(protein_id: str, k: int, run_name: str):
    # get seq from protein -> via protein-file?
    with open(f"{RUNS_PATH}/{run_name}/graphs/{protein_id}.txt", "r") as f:
        lines = f.readlines()

    sequence_pattern = r"^SQ\s+SEQUENCE\s+\d+"

    found_lines = []
    matched = False
    for line in lines:
        if re.match(sequence_pattern, line):
            matched = True
        if matched:
            if line.startswith("//"):
                break
            found_lines.append(line)

    ref_seq = ""
    for line in found_lines:
        if line.startswith("SQ"):
            line = line.split(" ")
            for s in line:
                if s == "":
                    del line[line.index(s)]
            print(line)
            seq_len = int(line[2])
            continue
        if line.startswith("//"):
            continue
        ref_seq += line.strip()
    ref_seq = ref_seq.replace(" ", "")

    # create index
    index = {}
    kmer_list = []
    for i, char in enumerate(ref_seq):
        end_index = i + k if i + k < len(ref_seq) else len(ref_seq)
        kmer = ref_seq[i:end_index]
        kmer_list.append(kmer)
        if kmer in index:
            index[kmer].append(i)
        else:
            index[kmer] = [i]

    for kmer in kmer_list:
        assert kmer in index, f"kmer {kmer} not in index but should be"

    return index, seq_len


def _longest_paths(protein_graph: nx.Graph, start_node: str):
    """
    create mapping from node to distance where the distance is the longest path
    from the starting point to each node

    A Variation is assumed to only ever be one aminoacid long
    """

    topo_order = list(nx.topological_sort(protein_graph))

    distances = {node: -1 for node in protein_graph.nodes}
    distances[start_node] = 0

    for node in topo_order:
        if node == start_node:
            aminoacid_len = 0
        else:
            aminoacid_len = int(len(protein_graph.nodes[node]["aminoacid"]))

        if distances[node] != -1:
            for neighbor in protein_graph.neighbors(node):
                distances[neighbor] = max(
                    distances[neighbor], distances[node] + aminoacid_len
                )
    return dict(sorted(distances.items(), key=lambda x: x[1]))


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


if __name__ == "__main__":
    # g = nx.read_graphml(
    #     "/Users/anton/Documents/code/PROTzilla2/user_data/runs/as/graphs/Q7Z3B0.graphml"
    # )
    # g = nx.read_graphml(
    #     "/Users/anton/Documents/code/PROTzilla2/user_data/runs/as/graphs/P10636.graphml"
    # )
    # index = _create_graph_index(protein_graph=g, starting_point="n0")

    _create_ref_seq_index("P10636", 5, "as")
