import logging
import re
import subprocess
from pathlib import Path

import networkx as nx
import pandas as pd
import requests
from django.contrib import messages

from protzilla.constants.paths import RUNS_PATH


def _create_graph(protein_id: str, run_name: str, queue_size: int = None):
    run_path = f"{RUNS_PATH}/{run_name}"
    path_to_protein_file, request = _get_protein_file(protein_id, run_path)

    if request is not None:
        if request.status_code != 200:
            msg = f"error while downloading protein file for {protein_id}.\
                         Statuscode:{request.status_code}, {request.reason}. \
                         Got: {request.text}. Tip: check if the ID is correct"
            return dict(
                graph_path=None,
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


def peptides_to_isoform(peptide_df: pd.DataFrame, protein_id: str, run_name: str):
    if not Path(f"{RUNS_PATH}/{run_name}/graphs/{protein_id}.graphml").exists():
        out_dict = _create_graph(protein_id, run_name)
    else:
        out_dict = dict(
            graph_path=f"{RUNS_PATH}/{run_name}/graphs/{protein_id}.graphml",
            messages=[dict(level=messages.INFO, msg="Graph already exists")],
        )

    if protein_id not in peptide_df["Protein ID"].tolist():
        return dict(
            graph_path=out_dict["graph_path"],
            messages=[
                dict(
                    level=messages.ERROR,
                    msg=f"Protein {protein_id} cannot be found in the peptide data",
                )
            ],
        )

    if out_dict["graph_path"] is None:
        return out_dict
    graph_path = out_dict["graph_path"]

    k = 5
    allowed_mismatches = 2

    protein_graph = nx.read_graphml(graph_path)
    protein_path = f"{RUNS_PATH}/{run_name}/graphs/{protein_id}.txt"

    # n0 is always the __start__ node in ProtGraph
    graph_index = _create_graph_index(protein_graph, "n0")
    print(graph_index)

    ref_index, ref_seq, seq_len = _create_ref_seq_index(protein_path, k=k)
    print(ref_index)
    print(ref_seq)
    print(seq_len)

    df = peptide_df[peptide_df["Protein ID"].str.contains(protein_id)]
    peptides = df["Sequence"].tolist()
    peptide_matches = {}
    mismatched_peptides = []
    for peptide in peptides:
        kmer = peptide[:k]
        matched_starts = []
        for start_pos in ref_index[kmer]:
            mismatch_counter = 0
            for i, aminoacid in enumerate(
                ref_seq[start_pos : start_pos + len(peptide)]
            ):
                if aminoacid != peptide[i]:
                    mismatch_counter += 1
                if mismatch_counter > allowed_mismatches:
                    break

            if mismatch_counter <= allowed_mismatches:
                matched_starts.append(start_pos)
            else:
                mismatched_peptides.append(peptide)
        peptide_matches[peptide] = matched_starts
    logging.warning("peptide_matches")
    logging.warning(peptide_matches)

    # P82909: {'DNPKPNVSEALR': [29], 'KLVSQEEMEFIQR': [86], 'VVQVVKPHTPLIR': [11]}

    peptide_to_node = {}
    for peptide, indices in peptide_matches.items():
        for start_index in indices:
            for i in range(start_index, start_index + len(peptide)):
                # lookup in which of the possible nodes the aa is present -> adopt graph index

                if peptide in peptide_to_node:
                    peptide_to_node[peptide].append((graph_index[i], i))
                else:
                    peptide_to_node[peptide] = [(graph_index[i], i)]

    node_start_end = {}
    for peptide, values in peptide_to_node.items():
        for value in values:
            for start_pos in peptide_matches[peptide]:
                # TODO: iterate over all possible start positions for all values?
                pos_aa = value[1]

                for node, aa in value[0]:
                    # TODO: what happens when ref_seq < longest path?
                    aa_pos_in_node = pos_aa

                    if node in node_start_end:
                        if peptide not in node_start_end[node]:
                            node_start_end[node][peptide] = {
                                "start": (aa_pos_in_node, aa),
                                "end": (aa_pos_in_node, aa),
                            }
                            continue

                        if aa_pos_in_node < node_start_end[node][peptide]["start"][0]:
                            node_start_end[node][peptide]["start"] = (
                                aa_pos_in_node,
                                aa,
                            )

                        elif aa_pos_in_node > node_start_end[node][peptide]["end"][0]:
                            node_start_end[node][peptide]["end"] = (aa_pos_in_node, aa)

                        elif (
                            aa_pos_in_node == node_start_end[node][peptide]["start"][0]
                        ):
                            logging.warning(
                                f"start_pos already exists for node {node}, peptide {peptide}, aa_pos_in_node {aa_pos_in_node}, aa {aa}"
                            )

                    else:
                        node_start_end[node] = {
                            peptide: {
                                "start": (aa_pos_in_node, aa),
                                "end": (aa_pos_in_node, aa),
                            }
                        }


    was passiert, wenn ein peptid mehrfach pro knoten vorkommt?
    muss vlt noch in node_start_end berücksichtigt werden
    -> verschiedene start_pos aus peptide_matching!


    print("node_start_end")
    print(node_start_end)

    node_mod = {}
    for node, peptides_dict in node_start_end.items():
        for peptide, values in peptides_dict.items():
            if node not in node_mod:
                node_mod[node] = [(values["start"][0], values["end"][0])]
            else:
                node_mod[node].append((values["start"][0], values["end"][0]))
        node_mod[node] = sorted(node_mod[node], key=lambda x: x[0])

    print("node_mod")
    print(node_mod)

    for node, positions_list in node_mod.items():
        for start, end in positions_list:
            pass

    return dict(
        graph_path=graph_path,
        peptide_matches=peptide_matches,  # , messages=[out_dict["messages"]]
    )


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
            aa_pos_in_node = i - longest_paths[node]
            index[i].append(
                (node, protein_graph.nodes[node]["aminoacid"][aa_pos_in_node])
            )

    return index


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


def _create_ref_seq_index(protein_path: str, k: int = 5):
    ref_seq, seq_len = _get_ref_seq(protein_path)

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

    return index, ref_seq, seq_len


def _get_ref_seq(protein_path: str):
    with open(protein_path, "r") as f:
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
    seq_len = None
    for line in found_lines:
        # guaranteed to be exactly one line with all following aside from
        # last line to be ref sequence
        if line.startswith("SQ"):
            line = line.split()
            seq_len = int(line[2])
            continue
        # last line starts with "//"
        if line.startswith("//"):
            break
        ref_seq += line.strip()
    ref_seq = ref_seq.replace(" ", "")

    if not ref_seq:
        raise ValueError(f"Could not find sequence for protein at path {protein_path}")
    if seq_len is None:
        logging.warning(
            f"Could not find sequence length for protein at path {protein_path}"
        )

    return ref_seq, seq_len


if __name__ == "__main__":
    # g = nx.read_graphml(
    #     "/Users/anton/Documents/code/PROTzilla2/user_data/runs/as/graphs/Q7Z3B0.graphml"
    # )
    # g = nx.read_graphml(
    #     "/Users/anton/Documents/code/PROTzilla2/user_data/runs/as/graphs/P10636.graphml"
    # )
    # index = _create_graph_index(protein_graph=g, starting_point="n0")

    index, ref_seq, seq_len = _create_ref_seq_index("SIM46", 5, "as")
    print(index)
