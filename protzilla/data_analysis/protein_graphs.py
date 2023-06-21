import re
import subprocess
from pathlib import Path

import networkx as nx
import pandas as pd
import requests
from django.contrib import messages

from protzilla.constants.logging import logger
from protzilla.constants.paths import RUNS_PATH


def peptides_to_isoform(
    peptide_df: pd.DataFrame, protein_id: str, run_name: str, k: int = 5
):
    """
    Creates a Protein-Variation-Graph for a given UniProt Protein ID using ProtGraph and
    matches the peptides from the given peptide_df to the graph. The graph is modified
    to include the matched peptides. Matches are indicated by red node-labels.

    Matches are not necessarily individual peptides but can be peptide-contigs when
    matching peptides overlap.

    ProtGraph Source: https://github.com/mpc-bioinformatics/ProtGraph/
    Used ProtGraph Version: https://github.com/antonneubauer/ProtGraph@master

    :param peptide_df: Peptide Dataframe with columns "sequence", "protein_id"
    :type peptide_df: pd.DataFrame
    :param protein_id: UniProt Protein-ID
    :type protein_id: str
    :param run_name: name of the run this is executed from. Used for saving the protein
        file, graph
    :type run_name: str
    :param k: k-mer size to build necessary indices for matching peptides, defaults to 5
    :type k: int, optional

    :return: dict(graph_path, peptide_matches, peptide_mismatches, messages)
    :rtype: dict[str, list, list, list]
    """

    assert k > 0, "k must be greater than 0"
    assert isinstance(k, int), "k must be an integer"
    allowed_mismatches = 2

    if not protein_id:
        return dict(
            graph_path=None,
            messages=[dict(level=messages.ERROR, msg="No protein ID provided")],
        )

    peptides = _get_peptides(peptide_df=peptide_df, protein_id=protein_id)

    if not peptides:
        msg = f"No peptides found for isoform {protein_id} in Peptide Dataframe"
        logger.error(msg)
        return dict(
            graph_path=None,
            messages=[dict(level=messages.ERROR, msg=msg)],
        )

    potential_graph_path = f"{RUNS_PATH}/{run_name}/graphs/{protein_id}.graphml"
    if not Path(potential_graph_path).exists():
        out_dict = _create_protein_variation_graph(protein_id, run_name)
        graph_path = out_dict["graph_path"]
        message = out_dict["messages"]
        if graph_path is None:
            return dict(graph_path=None, messages=message)
    else:
        logger.info(f"Graph already exists for protein {protein_id}. Skipping creation")
        graph_path = potential_graph_path

    protein_graph = nx.read_graphml(graph_path)
    protein_path = f"{RUNS_PATH}/{run_name}/graphs/{protein_id}.txt"
    matched_graph_path = f"{RUNS_PATH}/{run_name}/graphs/{protein_id}_modified.graphml"

    ref_index, ref_seq, seq_len = _create_ref_seq_index(protein_path, k=k)

    graph_index, msg, longest_paths = _create_graph_index(protein_graph, seq_len)
    if msg:
        return dict(
            graph_path=graph_path,
            messages=[dict(level=messages.ERROR, msg=msg)],
        )

    peptide_matches, peptide_mismatches = _match_peptides(
        allowed_mismatches=allowed_mismatches,
        k=k,
        peptides=peptides,
        ref_index=ref_index,
        ref_seq=ref_seq,
    )

    node_start_end = _get_start_end_pos_for_matches(peptide_matches, graph_index)
    contigs = _create_contigs_dict(node_start_end)
    modified_graph = _modify_graph(protein_graph, contigs, longest_paths)

    logger.info(f"writing modified graph at {matched_graph_path}")
    nx.write_graphml(modified_graph, matched_graph_path)

    msg = f"matched-peptides-graph created at {matched_graph_path}"
    return dict(
        graph_path=matched_graph_path,
        peptide_matches=list(peptide_matches.keys()),
        peptide_mismatches=peptide_mismatches,
        messages=[dict(level=messages.INFO, msg=msg)],
    )


def _create_protein_variation_graph(protein_id: str, run_name: str):
    """
    Creates a Protein-Variation-Graph for a given UniProt Protein ID using ProtGraph.
    Included features are just `Variation`, digestion is skipped.
    The Graph is saved in .graphml-Format.

    This is designed, so it can be used for peptides_to_isoform but works independently
    as well

    ProtGraph: https://github.com/mpc-bioinformatics/ProtGraph/

    :param protein_id: UniProt Protein-ID
    :type: str
    :param run_name: name of the run this is executed from. Used for saving the protein
        file, graph
    :type: str
    :param queue_size: Queue Size for ProtGraph, This is yet to be merged by ProtGraph
    :type: int

    :return: dict(graph_path, messages)
    """

    logger.info(f"Creating graph for protein {protein_id}")
    run_path = f"{RUNS_PATH}/{run_name}"
    path_to_protein_file, request = _get_protein_file(protein_id, run_path)

    if request is not None:
        if request.status_code != 200:
            msg = f"error while downloading protein file for {protein_id}. Statuscode:{request.status_code}, {request.reason}. Got: {request.text}. Tip: check if the ID is correct"
            logger.error(msg)
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
    logger.info(msg)
    return dict(graph_path=graph_path, messages=[dict(level=messages.INFO, msg=msg)])


def _create_graph_index(
    protein_graph: nx.DiGraph, seq_len: int
) -> tuple[list | None, str, dict | None]:
    """
    create a mapping from the position in the protein (using the longest path) to
    node(s) in the graph

    For information about _longest_path() please see the docstring of that function.

    TODO: this might be broken (in conjunction with the ref.-seq index) for versions where a ref.-seq is shorter than the longest path

    :param protein_graph: Protein-Graph as created by ProtGraph. Expected to have at
        least three nodes; one source, one sink, labeled by `__start__` and `__end__`.
        The labels of nodes are expected to be in the field "aminoacid".
    :type protein_graph: nx.DiGraph
    :param seq_len: length of the reference sequence of the Protein to map to
    :type seq_len: int

    :return: `index` of structure {aminoacid_pos : [nodes]}, `msg` with potential error
        info, `longest_paths`: {node: longest path counting aminoacids}
    :rtype: tuple(list, str, dict)
    """
    for node in protein_graph.nodes:
        if protein_graph.nodes[node]["aminoacid"] == "__start__":
            starting_point = node
            break
    else:
        msg = "No starting point found in the graph. An error in the graph creation is likely."
        logger.error(msg)
        return None, msg, None

    try:
        longest_paths = _longest_paths(protein_graph, starting_point)
    except Exception as e:
        logger.error(f"Error in _longest_paths in _create_graph_index: {e}")
        return None, str(e), None

    for node in protein_graph.nodes:
        if (
            protein_graph.nodes[node]["aminoacid"] == "__end__"
            and longest_paths[node] < seq_len
        ):
            msg = f"The longest path to the last node is shorter than the reference sequence. An error in the graph creation is likely. Node: {node}, longest path: {longest_paths[node]}, seq_len: {seq_len}"
            logger.error(msg)
            return None, msg, longest_paths

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


def _longest_paths(protein_graph: nx.DiGraph, start_node: str):
    """
    Create a mapping from node to longest_path from source to that node.

    Let n be a node in the graph and P be the set of all predecessors of n.
    longest_paths[n] = max(longest_paths[p] + len(aminoacid of n)) for p in P

    A Variation is assumed to only ever be one aminoacid long.

    e.g.:            n1     n2    n3   n5
        __start__ -> ABC -> DE -> F -> JK -> __end__
                               \  L  /
                                  n4
        longest_paths: {n1: 0, n2: 3, n3: 5, n4: 5, n5: 6, __end__: 8}

    :param protein_graph: Protein-Graph as created by ProtGraph \
        (-> _create_protein_variation_graph)
    :type protein_graph: nx.DiGraph
    :param start_node: Source of protein_graph
    :type start_node: str

    :return: Dict of {node: longest path from start_node to node}
    :rtype: dict
    """
    topo_order = list(nx.topological_sort(protein_graph))

    distances = {node: -1 for node in protein_graph.nodes}
    distances[start_node] = 0

    for node in topo_order:
        if node == start_node:
            aminoacid_len = 0
        else:
            aminoacid_len = len(protein_graph.nodes[node]["aminoacid"])

        # visiting in topological order, so distance to node should be set already
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

    # check for consistent order - probably overkill but better safe than sorry
    for node, d_node, longest_path in zip(
        topo_order, longest_paths.keys(), longest_paths.values()
    ):
        assert node == d_node, f"order is unequal to topological order, {longest_paths}"

    return longest_paths


def _get_protein_file(protein_id, run_path) -> (str, requests.models.Response | None):
    protein_id = protein_id.upper()
    path_to_graphs = Path(Path(run_path) / "graphs")
    path_to_protein_file = Path(path_to_graphs / f"{protein_id}.txt")
    url = f"https://rest.uniprot.org/uniprotkb/{protein_id}.txt"
    r = None

    if not path_to_graphs.exists():
        Path(path_to_graphs).mkdir(parents=True, exist_ok=True)
    if path_to_protein_file.exists():
        logger.info(
            f"Protein file {path_to_protein_file} already exists. Skipping download."
        )
    else:
        logger.info(f"Downloading protein file from {url}")
        r = requests.get(url)
        r.raise_for_status()

        with open(path_to_protein_file, "wb") as f:
            f.write(r.content)

    return path_to_protein_file, r


def _create_ref_seq_index(protein_path: str, k: int = 5) -> tuple[dict, str, int]:
    """
    Create mapping from kmer of reference_sequence of protein to starting position(s) \
    of kmer in reference_sequence

    :param protein_path: Path to protein file from UniProt (.txt)
    :type protein_path: str
    :param k: length of kmers
    :type k: int
    :return: index {kmer: [starting positions]}, reference sequence, length of reference
        sequence
    :rtype: tuple(dict, str, int)
    """

    logger.debug("Creating reference sequence index")
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

    logger.debug("Finished creating reference sequence index")
    return index, ref_seq, seq_len


def _get_ref_seq(protein_path: str) -> (str, int):
    """
    Parses Protein-File in UniProt SP-EMBL format in .txt files. Extracts reference
    sequence and sequence length.

    SP-EMBL Description: https://web.expasy.org/docs/userman.html

    :raises ValueError: If no lines were matched to the sequence pattern or if no
    sequence was found or if no sequence length was found.

    :param protein_path: Path to Protein-File in UniProt .txt format.
    :type protein_path: str

    :return: reference sequence of Protein, sequence length
    :rtype: str, int
    """

    if not Path(protein_path).exists():
        raise FileNotFoundError(f"Could not find protein file at {protein_path}")

    with open(protein_path, "r") as f:
        lines = f.readlines()

    sequence_pattern = r"^SQ\s+SEQUENCE\s+\d+"

    found_lines = []
    matched = False
    for line in lines:
        if re.match(sequence_pattern, line):
            matched = True
        if matched:
            # last line starts with "//"
            if line.startswith("//"):
                break
            found_lines.append(line)

    if not found_lines:
        raise ValueError(f"Could not find lines with Sequence in {protein_path}")

    ref_seq = ""
    seq_len = None
    for line in found_lines:
        # exactly one line starts with "SQ" with all following lines until "//" being
        # part of the sequence
        if line.startswith("SQ"):
            line = line.split()
            seq_len = int(line[2])
            continue
        if line.startswith("//"):
            break
        ref_seq += line.strip()
    ref_seq = ref_seq.replace(" ", "")

    if not ref_seq:
        raise ValueError(f"Could not find sequence for protein at path {protein_path}")
    if seq_len is None or not isinstance(seq_len, int) or seq_len < 1:
        raise ValueError(
            f"Could not find sequence length for protein file at path {protein_path}"
        )

    return ref_seq, seq_len


def _match_peptides(
    allowed_mismatches: int, k: int, peptides: list, ref_index: dict, ref_seq: str
):
    """
    Match peptides to reference sequence. `allowed_mismatches` many mismatches are
    allowed per try to match peptide to a potential start position in ref_index

    :param allowed_mismatches: number of mismatches allowed per peptide-match try
    :type allowed_mismatches: int
    :param k: size of kmer
    :type k: int
    :param peptides: list of peptide-strings
    :type peptides: list
    :param ref_index: mapping from kmer to match-positions on reference sequence
    :type ref_index: dict(kmer: [starting position]}
    :param ref_seq: reference sequence of protein
    :type ref_seq: str
    :return: dict(peptide: [match start on reference sequence]),
    list(peptides without match)
    :rtype: dict, list
    """

    if not isinstance(k, int) or k < 1:
        raise ValueError(f"k must be positive integer, but is {k}")
    if not isinstance(allowed_mismatches, int) or allowed_mismatches < 0:
        raise ValueError(
            f"allowed_mismatches must be non-negative integer, but is {allowed_mismatches}"
        )

    logger.debug("Matching peptides to reference sequence")
    peptide_matches = {}
    peptide_mismatches = set()
    seq_len = len(ref_seq)
    for peptide in peptides:
        kmer = peptide[:k]
        matched_starts = []
        if kmer not in ref_index:
            peptide_mismatches.add(peptide)
            continue
        for match_start_pos in ref_index[kmer]:
            mismatch_counter = 0
            if match_start_pos + len(peptide) > seq_len:
                # for now potential matches like this will be dismissed even if
                # match_start_pos + len(peptide) - allowed_mismatches <= seq_len
                logger.debug(
                    f"match would be out of bounds for peptide {peptide}, match_start_pos {match_start_pos}"
                )
                if peptide not in peptide_matches:
                    peptide_mismatches.add(peptide)
                continue
            for i in range(match_start_pos, match_start_pos + len(peptide)):
                if ref_seq[i] != peptide[i - match_start_pos]:
                    mismatch_counter += 1
                if mismatch_counter > allowed_mismatches:
                    peptide_mismatches.add(peptide)
                    break

            if mismatch_counter <= allowed_mismatches:
                matched_starts.append(match_start_pos)
                # append to easily check if peptide was previously matched for further
                # starting positions
                peptide_matches[peptide] = []
                if peptide in peptide_mismatches:
                    peptide_mismatches.remove(peptide)

        if matched_starts:
            peptide_matches[peptide] = matched_starts

    logger.debug(f"peptide matches - peptide:[starting_pos] :: {peptide_matches}")
    logger.debug(f"peptide mismatches: {peptide_mismatches}")

    return peptide_matches, sorted(list(peptide_mismatches))


def _create_contigs_dict(node_start_end: dict):
    """
    Create a start and end points of contigs for each node with a match.

    :param node_start_end: dict of node to list of tuples of
        start and end positions of matches within the node
    :type node_start_end: dict

    :return: dict of node to list of tuples of start and end positions of contigs
    """

    node_mod = {}
    for node, peptides_dict in node_start_end.items():
        for peptide, start_pos_dict in peptides_dict.items():
            for match_start_pos, match_end_pos in start_pos_dict.items():
                if node not in node_mod:
                    node_mod[node] = [(match_start_pos, match_end_pos)]
                else:
                    node_mod[node].append((match_start_pos, match_end_pos))
        node_mod[node] = sorted(node_mod[node])

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

    return node_mod


def _get_start_end_pos_for_matches(peptide_matches, graph_index):
    node_start_end = {}
    for peptide, indices in peptide_matches.items():
        for match_start_index in indices:
            for i in range(match_start_index, match_start_index + len(peptide)):
                # if match is over Variation: check which node is actually hit by
                # checking which amino acid matches
                if len(graph_index[i]) > 1:
                    raise NotImplementedError("Variation matching not implemented yet")
                for node, aa in graph_index[i]:
                    # TODO what happens when ref_seq < longest_path?
                    if node in node_start_end:
                        if peptide in node_start_end[node]:
                            if match_start_index in node_start_end[node][peptide]:
                                if i > node_start_end[node][peptide][match_start_index]:
                                    node_start_end[node][peptide][match_start_index] = i
                            else:
                                node_start_end[node][peptide][match_start_index] = i
                        else:
                            node_start_end[node][peptide] = {match_start_index: i}
                    else:
                        node_start_end[node] = {peptide: {match_start_index: i}}

    return node_start_end


def _modify_graph(graph, contig_positions, longest_paths):
    """
    Splits nodes of graph at into new contig nodes defined by the start- and
    end-positions in contig_positions. Adds `match` attribute to nodes, "true" when
    contig, "false" if not. Sink (__end__) node will end up without `match`-attribute

    :param graph: Protein Graph to be modified
    :type: nx.DiGraph
    :param contig_positions: Dict from node to contig-positions {node: [(start, end)]}.
    :type: dict(node: [(start, end)])
    :param longest_paths: mapping from node to the longest path to node
    (-> _longest_paths())
    :type: dict
    :return: modified protein graph, with contigs & not-matched AAs as nodes, indicated
    by node attribute `matched`
    """

    def _update_new_node_after(node, new_node, neighbors):
        for neighbor in neighbors:
            graph.add_edge(neighbor, new_node)
            graph.remove_edge(neighbor, node)

    def _node_length(node):
        return len(graph.nodes[node]["aminoacid"])

    logger.info("updating graph to visualise peptide matches")
    for node, positions_list in contig_positions.items():
        old_node = graph.nodes[node].copy()
        old_node_start = longest_paths[node]
        for start, end in positions_list:
            if (
                longest_paths[node] == start
                and longest_paths[node] + _node_length(node) - 1 == end
            ):
                logger.debug(f"matched full node {node}")
                nx.set_node_attributes(
                    graph,
                    {
                        node: {
                            "aminoacid": graph.nodes[node]["aminoacid"],
                            "match": "true",
                        }
                    },
                )
                continue

            before_node_id = None
            before_label = None
            if start > longest_paths[node]:
                s = longest_paths[node] - old_node_start
                e = start - old_node_start
                before_label = old_node["aminoacid"][s:e]
                before_node_id = f"n{len(graph.nodes)}"
                graph.add_node(before_node_id, aminoacid=before_label, match="false")

                predecessors = list(graph.predecessors(node))
                _update_new_node_after(node, before_node_id, predecessors)
                longest_paths[before_node_id] = longest_paths[node]
                longest_paths[node] = longest_paths[before_node_id] + len(before_label)

            # create match node
            after_node = True
            if (
                before_node_id
                and end
                == longest_paths[node] + _node_length(node) - len(before_label) - 1
            ):
                # match node is rest of node
                after_node = False
                s = longest_paths[node] - old_node_start
                e = end - old_node_start + 1
                match_label = old_node["aminoacid"][s:e]
                match_node_id = node
                nx.set_node_attributes(
                    graph,
                    {node: {"aminoacid": match_label, "match": "true"}},
                )
            else:
                s = longest_paths[node] - old_node_start
                e = end - old_node_start + 1
                match_label = old_node["aminoacid"][s:e]
                match_node_id = f"n{len(graph.nodes)}"
                graph.add_node(match_node_id, aminoacid=match_label, match="true")

            # adopt edges from predecessors of old node to before or match node
            # push old node back, position new nodes in front
            if before_node_id:
                graph.add_edge(before_node_id, match_node_id)
                longest_paths[match_node_id] = longest_paths[before_node_id] + len(
                    before_label
                )
            else:
                predecessors = list(graph.predecessors(node))
                _update_new_node_after(node, match_node_id, predecessors)
                longest_paths[match_node_id] = longest_paths[node]
                longest_paths[node] = longest_paths[match_node_id] + len(match_label)

            if after_node:
                if end < longest_paths[node] + _node_length(node) - 1:
                    s = longest_paths[match_node_id] - old_node_start + len(match_label)
                    after_label = old_node["aminoacid"][s:]

                    nx.set_node_attributes(
                        graph,
                        {node: {"aminoacid": after_label, "match": "false"}},
                    )
                    graph.add_edge(match_node_id, node)
                    longest_paths[node] = longest_paths[match_node_id] + len(
                        match_label
                    )
                else:
                    successors = list(graph.successors(node))
                    for successor in successors:
                        graph.add_edge(match_node_id, successor)
                        graph.remove_edge(node, successor)

    return graph


def _get_peptides(peptide_df: pd.DataFrame, protein_id: str) -> list[str] | None:
    df = peptide_df[peptide_df["Protein ID"].str.contains(protein_id)]
    pattern = rf"^({protein_id}-\d+)$"
    filter = df["Protein ID"].str.contains(pattern)
    df = df[~filter]

    intensity_name = [col for col in df.columns if "intensity" in col.lower()][0]
    df = df.dropna(subset=[intensity_name])
    df = df[df[intensity_name] != 0]
    return df["Sequence"].unique().tolist()
