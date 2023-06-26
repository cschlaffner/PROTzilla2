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

    :return: dict of path to graph - either the modified graph or the original graph if
    the modification failed, list of matched peptides, list of unmatched peptides,
    messages passed to the frontend
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

    potential_graph_path = RUNS_PATH / run_name / "graphs" / f"{protein_id}.graphml"
    if not potential_graph_path.exists():
        out_dict = _create_protein_variation_graph(protein_id, run_name)
        graph_path = out_dict["graph_path"]
        message = out_dict["messages"]
        if graph_path is None:
            return dict(graph_path=None, messages=message)
    else:
        logger.info(f"Graph already exists for protein {protein_id}. Skipping creation")
        graph_path = potential_graph_path

    protein_graph = nx.read_graphml(graph_path)
    protein_path = RUNS_PATH / run_name / "graphs" / f"{protein_id}.txt"
    matched_graph_path = (
        RUNS_PATH / run_name / "graphs" / f"{protein_id}_modified.graphml"
    )

    ref_index, ref_seq, seq_len = _create_ref_seq_index(protein_path, k=k)

    graph_index, msg, longest_paths = _create_graph_index(protein_graph, seq_len)
    if msg:
        return dict(
            graph_path=graph_path,
            messages=[dict(level=messages.ERROR, msg=msg)],
        )

    potential_peptide_matches, peptide_mismatches = _match_peptides(
        allowed_mismatches=allowed_mismatches,
        k=k,
        peptides=peptides,
        ref_index=ref_index,
        ref_seq=ref_seq,
    )

    peptide_match_node_start_end, peptide_mismatches = _get_start_end_pos_for_matches(
        potential_peptide_matches=potential_peptide_matches,
        graph_index=graph_index,
        peptide_mismatches=peptide_mismatches,
        allowed_mismatches=allowed_mismatches,
        graph=protein_graph,
        longest_paths=longest_paths,
    )
    contigs = _create_contigs_dict(peptide_match_node_start_end)
    modified_graph = _modify_graph(protein_graph, contigs, longest_paths)

    logger.info(f"writing modified graph at {matched_graph_path}")
    nx.write_graphml(modified_graph, matched_graph_path)

    msg = f"matched-peptides-graph created at {matched_graph_path}"
    return dict(
        graph_path=str(matched_graph_path),
        peptide_matches=list(peptide_match_node_start_end.keys()),
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
    run_path = RUNS_PATH / run_name
    path_to_protein_file, request = _get_protein_file(protein_id, run_path)

    path_to_protein_file = Path(path_to_protein_file)
    if not path_to_protein_file.exists() and request.status_code != 200:
        msg = f"error while downloading protein file for {protein_id}. Statuscode:{request.status_code}, {request.reason}. Got: {request.text}. Tip: check if the ID is correct"
        logger.error(msg)
        return dict(
            graph_path=None,
            messages=[dict(level=messages.ERROR, msg=msg, trace=request.__dict__)],
        )

    output_folder_path = run_path / "graphs"
    output_csv = output_folder_path / f"{protein_id}.csv"
    graph_path = output_folder_path / f"{protein_id}.graphml"
    cmd_str = f"protgraph -egraphml {path_to_protein_file} \
                --export_output_folder={output_folder_path} \
                --output_csv={output_csv} \
                -ft VARIANT \
                -d skip"
    # -ft VAR_SEQ --no_merge

    subprocess.run(cmd_str, shell=True)

    msg = f"Graph created for protein {protein_id} at {graph_path} using {path_to_protein_file}"
    logger.info(msg)
    return dict(
        graph_path=str(graph_path), messages=[dict(level=messages.INFO, msg=msg)]
    )


def _create_graph_index(
    protein_graph: nx.DiGraph, seq_len: int
) -> tuple[list | None, str, dict | None]:
    """
    create a mapping from the position in the protein (using the longest path) to
    node(s) in the graph

    For information about _longest_path() please see the docstring of that function.

    TODO: this might be broken (in conjunction with the ref.-seq index) for versions
    where a ref.-seq is shorter than the longest path. This would indicate additions to
    the reference sequence

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
        if protein_graph.nodes[node]["aminoacid"] == "__end__":
            if longest_paths[node] < seq_len:
                msg = f"The longest path to the last node is shorter than the reference sequence. An error in the graph creation is likely. Node: {node}, longest path: {longest_paths[node]}, seq_len: {seq_len}"
                logger.error(msg)
                return None, msg, longest_paths
            elif longest_paths[node] > seq_len:
                msg = f"The longest path to the last node is longer than the reference sequence. This could occur if a Variation is longer than just one Amino Acid. This is unexpected behaviour. Node: {node}, longest path: {longest_paths[node]}, seq_len: {seq_len}"
                logger.warning(msg)
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


def _get_protein_file(
    protein_id: str, run_path: Path
) -> (Path, requests.models.Response | None):
    path_to_graphs = run_path / "graphs"
    path_to_protein_file = path_to_graphs / f"{protein_id}.txt"
    url = f"https://rest.uniprot.org/uniprotkb/{protein_id}.txt"
    r = None

    path_to_graphs.mkdir(parents=True, exist_ok=True)

    if path_to_protein_file.exists():
        logger.info(
            f"Protein file {path_to_protein_file} already exists. Skipping download."
        )
    else:
        logger.info(f"Downloading protein file from {url}")
        r = requests.get(url)
        r.raise_for_status()

        path_to_protein_file.write_bytes(r.content)

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
    TODO: out of date! -> update
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
    potential_peptide_matches = {}
    peptide_mismatches = set()
    seq_len = len(ref_seq)
    for peptide in peptides:
        kmer = peptide[:k]
        matched_starts = []
        if kmer not in ref_index:
            peptide_mismatches.add(peptide)
            continue
        for match_start_pos in ref_index[kmer]:
            if match_start_pos + len(peptide) > seq_len:
                # for now potential matches like this will be dismissed even if
                # match_start_pos + len(peptide) - allowed_mismatches <= seq_len
                logger.debug(
                    f"match would be out of bounds for peptide {peptide}, match_start_pos {match_start_pos}"
                )
                continue
            matched_starts.append(match_start_pos)

        if matched_starts:
            potential_peptide_matches[peptide] = matched_starts
        else:
            peptide_mismatches.add(peptide)

    logger.debug(
        f"potential peptide matches - peptide:[starting_pos] :: {potential_peptide_matches}"
    )
    logger.debug(f"peptide mismatches: {peptide_mismatches}")

    return potential_peptide_matches, sorted(list(peptide_mismatches))


def _create_contigs_dict(node_start_end: dict):
    """
    Create a start and end points of contigs for each node with a match.

    :param node_start_end: dict of node to list of tuples of
        start and end positions of matches within the node
    :type node_start_end: dict

    :return: dict of node to list of tuples of start and end positions of contigs
    """

    node_match_data = {}
    for peptide, start_pos_dict in node_start_end.items():
        for start_index, node_dict in start_pos_dict.items():
            for node, start_end in node_dict.items():
                if node not in node_match_data:
                    node_match_data[node] = {
                        "match_locations": [(start_end[0], start_end[1])],
                        "peptides": [peptide],
                    }
                else:
                    node_match_data[node]["match_locations"].append(
                        (start_end[0], start_end[1])
                    )
                    if peptide not in node_match_data[node]["peptides"]:
                        node_match_data[node]["peptides"].append(peptide)

    print("node_match_data in contigs")
    print(node_match_data)

    for node in node_match_data:
        node_match_data[node]["match_locations"] = sorted(
            node_match_data[node]["match_locations"]
        )
        node_match_data[node]["peptides"] = sorted(node_match_data[node]["peptides"])

    # merge tuples where start of second tuple is smaller or equal to end of first tuple
    node_mod = {}
    for node, node_dict in node_match_data.items():
        new_positions_list = []
        for start, end in node_dict["match_locations"]:
            if not len(new_positions_list):
                new_positions_list.append((start, end))
                continue
            if start <= new_positions_list[-1][1]:
                new_positions_list[-1] = (new_positions_list[-1][0], end)
            else:
                new_positions_list.append((start, end))
        node_mod[node] = {
            "contigs": new_positions_list,
            "peptides": node_dict["peptides"],
        }

    print("node_mod in contigs")
    print(node_mod)

    return node_mod


def _get_start_end_pos_for_matches(
    potential_peptide_matches,
    graph_index,
    peptide_mismatches,
    allowed_mismatches,
    graph,
    longest_paths,
):
    """
    DISCLAIMER: Does not account for Variations that skip an AA
    """
    peptide_mismatches = set(peptide_mismatches)

    def _match_on_graph(
        mismatches,
        allowed_mismatches,
        graph,
        current_node,
        left_over_peptide,
        node_match_data,
        current_index,
    ):
        if mismatches > allowed_mismatches:
            return False, {}, mismatches
        if not left_over_peptide:
            return True, node_match_data, mismatches

        # check if leftover peptide and rest of aminoacids in current node match
        # if so, add node and start and end position to node_match_data,
        # return True, node_match_data, mismatches
        last_index = current_index
        for i, label_aa in enumerate(
            graph.nodes[current_node]["aminoacid"][current_index:]
        ):
            print("check node til end")
            if i > len(left_over_peptide) - 1:
                return True, node_match_data, mismatches
            print(
                "i, last index, current_node, left_over_peptide, label_aa, left_over_peptide[i], node_match_data"
            )
            print(
                i,
                last_index,
                current_node,
                left_over_peptide,
                label_aa,
                left_over_peptide[i],
                node_match_data,
            )
            if label_aa == left_over_peptide[i]:
                if current_node in node_match_data:
                    node_match_data[current_node] = (
                        node_match_data[current_node][0],
                        i + current_index,
                    )
                else:
                    node_match_data[current_node] = (current_index, current_index)
            else:
                mismatches += 1
                if mismatches > allowed_mismatches:
                    return False, {}, mismatches
            last_index = i
            print("node_match_data post node check")
            print(node_match_data)

        # node is matched til end, peptide not done
        data_from_succ = {}
        for succ in graph.successors(current_node):
            # if longest_paths[succ] > longest_paths[current_node] + len(
            #         graph.nodes[current_node]["aminoacid"]
            # ):
            match, node_match_data, mismatches = _match_on_graph(
                mismatches,
                allowed_mismatches,
                graph,
                succ,
                left_over_peptide[last_index + 1 :],
                node_match_data,
                current_index + last_index + 1,
            )
            if match:
                data_from_succ[succ] = (match, node_match_data, mismatches)
        if data_from_succ:
            return min(data_from_succ.items(), key=lambda item: item[1][2])[1]
        else:
            return False, {}, mismatches

    peptide_match_info = {}
    for peptide, indices in potential_peptide_matches.items():
        peptide_match_nodes = {}  # store positions of matches for each node
        for match_start_index in indices:  # start index is of ref_index
            # len(graph_index[match_start_index]) must be 1 -> match never starts on VAR
            matched, node_match_data, mismatches = _match_on_graph(
                mismatches=0,
                allowed_mismatches=allowed_mismatches,
                graph=graph,
                current_node=graph_index[match_start_index][0][0],
                left_over_peptide=peptide,
                node_match_data={},
                current_index=match_start_index
                - longest_paths[graph_index[match_start_index][0][0]],
            )
            if matched:
                logger.info(f"matched {peptide} at {match_start_index}")
                logger.info(f"match data: {node_match_data}")
                peptide_match_nodes[match_start_index] = node_match_data
            else:
                logger.info(f"mismatched start pos {match_start_index} for {peptide}")
        if peptide_match_nodes:
            peptide_match_info[peptide] = peptide_match_nodes
        else:
            peptide_mismatches.add(peptide)

    print("#############")
    print("peptide_match_info")
    print(peptide_match_info)

    return peptide_match_info, list(peptide_mismatches)


def _modify_graph(graph, contig_positions, longest_paths):
    """
    Splits nodes of graph at into new contig nodes defined by the start- and
    end-positions in contig_positions. Adds `match` attribute to nodes, "true" when
    contig, "false" if not. Sink (__end__) node will end up without `match`-attribute

    :param graph: Protein Graph to be modified
    :type: nx.DiGraph
    :param contig_positions: Dict from node to contig-positions {node: [(start, end)]}.
    :type: dict(list[tuple])
    :param longest_paths: mapping from node to the longest path to node
    (-> _longest_paths())
    :type: dict
    :return: modified protein graph, with contigs & not-matched AAs as nodes, indicated
    by node attribute `matched`
    """

    def _update_new_node_after(node, new_node, neighbors):
        for neighbor in neighbors:
            graph.remove_edge(neighbor, node)
            graph.add_edge(neighbor, new_node)

    def _node_length(node):
        return len(graph.nodes[node]["aminoacid"])

    logger.info("updating graph to visualise peptide matches")
    for node, node_dict in contig_positions.items():
        positions_list = node_dict["contigs"]
        old_node = graph.nodes[node].copy()
        old_node_aminoacids = old_node["aminoacid"]
        for start, end in positions_list:
            if start == 0 and _node_length(node) - 1 == end:
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

            # the start
            if _node_length(node) > start:
                before_label = old_node_aminoacids[:start]
                before_node_id = f"n{len(graph.nodes)}"
                graph.add_node(before_node_id, aminoacid=before_label, match="false")

                predecessors = list(graph.predecessors(node))
                _update_new_node_after(node, before_node_id, predecessors)
                longest_paths[before_node_id] = longest_paths[node]
                longest_paths[node] = longest_paths[before_node_id] + len(before_label)

            # create match node
            after_node = end < _node_length(node) - 1
            if not after_node:
                # no after node -> before node must exist
                match_label = old_node_aminoacids[start:]
                match_node_id = node
                nx.set_node_attributes(
                    graph,
                    {node: {"aminoacid": match_label, "match": "true"}},
                )
            else:
                match_label = old_node_aminoacids[start : end + 1]
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
                after_label = old_node_aminoacids[end + 1 :]

                nx.set_node_attributes(
                    graph,
                    {node: {"aminoacid": after_label, "match": "false"}},
                )
                graph.add_edge(match_node_id, node)
                longest_paths[node] = longest_paths[match_node_id] + len(match_label)
            else:
                # elif match_node_id != node:
                successors = list(graph.successors(node))
                for successor in successors:
                    graph.remove_edge(node, successor)
                    graph.add_edge(match_node_id, successor)

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
