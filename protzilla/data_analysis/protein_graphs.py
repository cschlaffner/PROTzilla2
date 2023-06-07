import logging
import math
import pprint
import re
import subprocess
from pathlib import Path

import networkx as nx
import pandas as pd
import requests
from django.contrib import messages

from protzilla.constants.paths import RUNS_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8.8s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def _create_graph(protein_id: str, run_name: str, queue_size: int = None):
    logger.info(f"Creating graph for protein {protein_id}")
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
                --output_csv={output_csv} \
                -ft VARIANT \
                -d skip"
    # -ft VAR_SEQ --no_merge

    subprocess.run(cmd_str, shell=True)

    msg = f"Graph created for protein {protein_id} at {graph_path} using {path_to_protein_file}"
    logging.info(msg)
    return dict(graph_path=graph_path, messages=[dict(level=messages.INFO, msg=msg)])


def peptides_to_isoform(peptide_df: pd.DataFrame, protein_id: str, run_name: str):
    df = peptide_df[peptide_df["Protein ID"].str.contains(protein_id)]
    pattern = rf"^({protein_id}-\d+)$"
    filter = df["Protein ID"].str.contains(pattern)
    df = df[~filter]

    intensity_name = [col for col in df.columns if "intensity" in col][0]
    df = df.dropna(subset=[intensity_name])
    # TODO drop where values == 0

    if df.empty:
        return dict(
            graph_path=None,
            messages=[
                dict(
                    level=messages.ERROR,
                    msg=f"No peptides found for isoform {protein_id} in Peptide Dataframe",
                )
            ],
        )
    peptides = df["Sequence"].unique().tolist()

    if not Path(f"{RUNS_PATH}/{run_name}/graphs/{protein_id}.graphml").exists():
        out_dict = _create_graph(protein_id, run_name)
    else:
        out_dict = dict(
            graph_path=f"{RUNS_PATH}/{run_name}/graphs/{protein_id}.graphml",
            messages=[dict(level=messages.INFO, msg="Graph already exists")],
        )

    if out_dict["graph_path"] is None:
        return out_dict
    graph_path = out_dict["graph_path"]

    k = 5
    allowed_mismatches = 2

    protein_graph = nx.read_graphml(graph_path)
    protein_path = f"{RUNS_PATH}/{run_name}/graphs/{protein_id}.txt"
    matched_graph_path = f"{RUNS_PATH}/{run_name}/graphs/{protein_id}_modified.graphml"

    ref_index, ref_seq, seq_len = _create_ref_seq_index(protein_path, k=k)

    graph_index, msg, longest_paths = _create_graph_index(protein_graph, seq_len)
    if msg:
        return dict(
            graph_path=graph_path,
            messages=[
                dict(
                    level=messages.ERROR,
                    msg=msg,
                )
            ],
        )

    # Peptide Matching
    peptide_matches = {}
    peptide_mismatches = []
    for peptide in peptides:
        kmer = peptide[:k]
        matched_starts = []
        for match_start_pos in ref_index[kmer]:
            mismatch_counter = 0
            for i, aminoacid in enumerate(
                ref_seq[match_start_pos : match_start_pos + len(peptide)]
            ):
                if aminoacid != peptide[i]:
                    mismatch_counter += 1
                if mismatch_counter > allowed_mismatches:
                    break

            if mismatch_counter <= allowed_mismatches:
                matched_starts.append(match_start_pos)
            else:
                peptide_mismatches.append(peptide)
        peptide_matches[peptide] = matched_starts

    logger.info(f"peptide matches - peptide:[starting_pos] :: {peptide_matches}")
    logger.info(f"peptide mismatches: {peptide_mismatches}")

    peptide_to_node = {}
    for peptide, indices in peptide_matches.items():
        for start_index in indices:
            for i in range(start_index, start_index + len(peptide)):
                # TODO: when match is part of variation:
                #  lookup in which of the possible nodes the aa is present
                #  -> adopt graph index

                if peptide in peptide_to_node:
                    peptide_to_node[peptide].append((graph_index[i], i))
                else:
                    peptide_to_node[peptide] = [(graph_index[i], i)]

    node_start_end = {}
    for peptide, values in peptide_to_node.items():
        peptide_len = len(peptide)

        for i, match_start_pos in enumerate(peptide_matches[peptide]):
            for aa_match_values in values:
                if i < len(peptide_matches[peptide]) - 1:
                    next_start = peptide_matches[peptide][i + 1]
                elif aa_match_values[1] < match_start_pos:
                    continue
                else:
                    next_start = math.inf

                if aa_match_values[1] < match_start_pos:
                    logger.debug(
                        "found 'less than match start'", peptide, aa_match_values[1]
                    )
                    continue
                if aa_match_values[1] > match_start_pos + peptide_len:
                    logger.debug(
                        "should probably be skipped as likely part of next match"
                    )
                if aa_match_values[1] >= next_start:
                    logger.debug(
                        "found 'greater than next start'", peptide, aa_match_values[1]
                    )
                    continue
                pos_aa = aa_match_values[1]

                for node, aa in aa_match_values[0]:
                    # TODO: what happens when ref_seq < longest path?
                    aa_pos_in_node = pos_aa

                    if node in node_start_end:
                        if peptide not in node_start_end[node]:
                            node_start_end[node][peptide] = {
                                match_start_pos: {
                                    "start": (aa_pos_in_node, aa),
                                    "end": (aa_pos_in_node, aa),
                                }
                            }
                            continue
                        if match_start_pos not in node_start_end[node][peptide]:
                            node_start_end[node][peptide][match_start_pos] = {
                                "start": (aa_pos_in_node, aa),
                                "end": (aa_pos_in_node, aa),
                            }
                            continue
                        if (
                            aa_pos_in_node
                            < node_start_end[node][peptide][match_start_pos]["start"][0]
                        ):
                            node_start_end[node][peptide][match_start_pos]["start"] = (
                                aa_pos_in_node,
                                aa,
                            )

                        elif (
                            aa_pos_in_node
                            > node_start_end[node][peptide][match_start_pos]["end"][0]
                        ):
                            node_start_end[node][peptide][match_start_pos]["end"] = (
                                aa_pos_in_node,
                                aa,
                            )

                        elif (
                            aa_pos_in_node
                            == node_start_end[node][peptide][match_start_pos]["start"][
                                0
                            ]
                        ):
                            logger.debug(
                                f"match_start_pos already exists for node {node}, peptide {peptide}, aa_pos_in_node {aa_pos_in_node}, aa {aa}"
                            )

                    else:
                        node_start_end[node] = {
                            peptide: {
                                match_start_pos: {
                                    "start": (aa_pos_in_node, aa),
                                    "end": (aa_pos_in_node, aa),
                                }
                            }
                        }

    node_mod = {}
    for node, peptides_dict in node_start_end.items():
        for peptide, start_pos_dict in peptides_dict.items():
            for match_start_pos, values in start_pos_dict.items():
                if node not in node_mod:
                    node_mod[node] = [(values["start"][0], values["end"][0])]
                else:
                    node_mod[node].append((values["start"][0], values["end"][0]))
        node_mod[node] = sorted(node_mod[node], key=lambda x: x[0])

    # node_mod
    # merge tuples where start of second tuple is smaller or equal to end of first tuple
    for node, positions_list in node_mod.items():
        new_positions_list = []
        for start, end in positions_list:
            if len(new_positions_list) == 0:
                new_positions_list.append((start, end))
                continue
            if start <= new_positions_list[-1][1]:
                new_positions_list[-1] = (new_positions_list[-1][0], end)
            else:
                new_positions_list.append((start, end))
        node_mod[node] = new_positions_list

    logger.info("modifying graph")
    for node, positions_list in node_mod.items():
        # 'n4': [(302, 308), (325, 349), (353, 359)]
        old_node = protein_graph.nodes[node].copy()
        old_node_starting_pos = longest_paths[node]
        for start, end in positions_list:
            if (
                longest_paths[node] == start
                and longest_paths[node] + len(protein_graph.nodes[node]["aminoacid"])
                == end
            ):
                logger.warning("match full node")
                nx.set_node_attributes(
                    protein_graph,
                    {
                        node: {
                            "aminoacid": protein_graph.nodes[node]["aminoacid"],
                            "match": "true",
                        }
                    },
                )
                continue

            before_node = False
            if start > longest_paths[node]:
                before_node = True
                before_node_label = old_node["aminoacid"][
                    longest_paths[node]
                    - old_node_starting_pos : start
                    - old_node_starting_pos
                ]
                before_node_id = f"n{len(protein_graph.nodes)}"
                predecessors = list(protein_graph.predecessors(node))

                protein_graph.add_node(
                    before_node_id, aminoacid=before_node_label, match="false"
                )
                for predecessor in predecessors:
                    protein_graph.add_edge(predecessor, before_node_id)
                    protein_graph.remove_edge(predecessor, node)

                # update longest_paths
                longest_paths[before_node_id] = longest_paths[node]
                longest_paths[node] = longest_paths[before_node_id] + len(
                    before_node_label
                )

            match_node_label = old_node["aminoacid"][
                longest_paths[node]
                - old_node_starting_pos : end
                - old_node_starting_pos
                + 1  # + 1 cause it doesn't include `end`
            ]
            match_node_id = f"n{len(protein_graph.nodes)}"
            protein_graph.add_node(
                match_node_id, aminoacid=match_node_label, match="true"
            )
            if before_node:
                protein_graph.add_edge(before_node_id, match_node_id)
                longest_paths[match_node_id] = longest_paths[before_node_id] + len(
                    before_node_label
                )
            else:
                longest_paths[match_node_id] = longest_paths[node]
                longest_paths[node] = longest_paths[match_node_id] + len(
                    match_node_label
                )
                predecessors = list(protein_graph.predecessors(node))
                for predecessor in predecessors:
                    protein_graph.add_edge(predecessor, match_node_id)
                    protein_graph.remove_edge(predecessor, node)

            if end < longest_paths[node] + len(protein_graph.nodes[node]["aminoacid"]):
                after_node_label = old_node["aminoacid"][
                    longest_paths[match_node_id]
                    - old_node_starting_pos
                    + len(match_node_label) :
                ]
                nx.set_node_attributes(
                    protein_graph,
                    {node: {"aminoacid": after_node_label, "match": "false"}},
                )
                protein_graph.add_edge(match_node_id, node)
                longest_paths[node] = longest_paths[match_node_id] + len(
                    match_node_label
                )
            elif end > longest_paths[node] + len(
                protein_graph.nodes[node]["aminoacid"]
            ):
                pprint.pprint(protein_graph.__dict__)
                print(
                    "end, longest_paths[node] + len(protein_graph.nodes[node]['aminoacid']), node, protein_graph.nodes[node]['aminoacid'], match_node_label"
                )
                print(
                    end,
                    longest_paths[node] + len(protein_graph.nodes[node]["aminoacid"]),
                    node,
                    protein_graph.nodes[node]["aminoacid"],
                    match_node_label,
                )
                raise Exception(
                    "end > longest_paths[node] + len(protein_graph.nodes[node]['aminoacid'])"
                )
            else:
                successors = list(protein_graph.successors(node))
                for successor in successors:
                    protein_graph.add_edge(match_node_id, successor)
                    protein_graph.remove_edge(node, successor)

    nx.write_graphml(protein_graph, matched_graph_path)

    return dict(
        graph_path=graph_path,
        matched_graph_path=matched_graph_path,
        peptide_matches=peptide_matches,
        peptide_mismatches=peptide_mismatches,
        messages=out_dict["messages"],
    )


def _create_graph_index(protein_graph: nx.Graph, seq_len: int):
    """
    create a mapping from the position in the protein to the node in the graph
    TODO: this might be broken (in conjunction with the ref.-seq index) for versions where a ref.-seq is shorter than the longest path
    """
    for node in protein_graph.nodes:
        if protein_graph.nodes[node]["aminoacid"] == "__start__":
            starting_point = node
            break
    else:
        msg = "No starting point found in the graph. An error in the graph creation is likely."
        logging.error(msg)
        return None, msg

    longest_paths = _longest_paths(protein_graph, starting_point)

    for node in protein_graph.nodes:
        if (
            protein_graph.nodes[node]["aminoacid"] == "__end__"
            and longest_paths[node] < seq_len
        ):
            msg = f"The longest path to the last node is shorter than the reference \
            sequence. An error in the graph creation is likely. Node: {node}, \
            longest path: {longest_paths[node]}, seq_len: {seq_len}"
            return None, msg

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
                # (node, AA)
                (node, protein_graph.nodes[node]["aminoacid"][aa_pos_in_node])
            )

    return index, "", longest_paths


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
            aminoacid_len = len(protein_graph.nodes[node]["aminoacid"])

        if distances[node] != -1:
            for neighbor in protein_graph.neighbors(node):
                distances[neighbor] = max(
                    distances[neighbor], distances[node] + aminoacid_len
                )
        else:
            raise Exception(
                f"The node {node} was not visited in the topological order (distance should be set already)"
            )

    longest_paths = dict(sorted(distances.items(), key=lambda x: x[1]))

    # check for consistent order
    for node, d_node, longest_path in zip(
        topo_order, longest_paths.keys(), longest_paths.values()
    ):
        assert node == d_node, f"{node} != {d_node}, {longest_path}"

    return longest_paths


def _get_protein_file(protein_id, run_path) -> (str, requests.models.Response | None):
    protein_id = protein_id.upper()
    path_to_graphs = f"{run_path}/graphs"
    path_to_protein_file = f"{path_to_graphs}/{protein_id}.txt"
    url = f"https://rest.uniprot.org/uniprotkb/{protein_id}.txt"
    r = None

    if not Path(path_to_graphs).exists():
        Path(path_to_graphs).mkdir(parents=True, exist_ok=True)
    if Path(path_to_protein_file).exists():
        logger.info(
            f"Protein file {path_to_protein_file} already exists. Skipping download."
        )
    else:
        logger.info(f"Downloading protein file from {url}")
        r = requests.get(url)
        if r.status_code == 200:
            with open(path_to_protein_file, "wb") as f:
                f.write(r.content)
        else:
            return "", r

    return path_to_protein_file, r


def _create_ref_seq_index(protein_path: str, k: int = 5):
    logger.info("Creating reference sequence index")
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
        raise ValueError(
            f"Could not find sequence length for protein at path {protein_path}"
        )

    return ref_seq, seq_len


if __name__ == "__main__":
    #     G = nx.DiGraph()
    #     G.add_edge("0", "1")
    #     G.add_edge("1", "2")
    #     G.add_edge("1", "3")
    #     G.add_edge("1", "4")
    #     G.add_edge("2", "4")
    #     G.add_edge("3", "4")
    #     G.add_edge("4", "5")
    #
    #     nx.set_node_attributes(
    #         G,
    #         {
    #             "0": {"aminoacid": "__start__"},
    #             "1": {"aminoacid": "ABC"},
    #             "2": {"aminoacid": "D"},
    #             "3": {"aminoacid": "E"},
    #             "4": {"aminoacid": "FG"},
    #             "5": {"aminoacid": "__end__"},
    #         },
    #     )
    #     g = G
    # g = nx.read_graphml(
    #     "/Users/anton/Documents/code/PROTzilla2/user_data/runs/peptide_test/graphs/Q7Z3B0.graphml"
    # )
    # g = nx.read_graphml(
    #     "/Users/anton/Documents/code/PROTzilla2/user_data/runs/peptide_test/graphs/P98160.graphml"
    # )
    # index = _create_graph_index(protein_graph=g, seq_len=4391)

    peptide_df = pd.read_csv(
        "/Users/anton/Documents/code/PROTzilla2/user_data/runs/peptide2/history_dfs/simple_P22626.csv"
    )
    peptide_df = peptide_df.drop(columns=["Unnamed: 0"])

    out_dict = peptides_to_isoform(
        peptide_df=peptide_df, protein_id="P22626", run_name="peptide3"
    )
