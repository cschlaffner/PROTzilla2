import re
import subprocess
from pathlib import Path

import networkx as nx
import pandas as pd
import requests
from django.contrib import messages

from protzilla.constants.logging import logger
from protzilla.constants.paths import RUNS_PATH


def variation_graph(protein_id: str, run_name: str):
    """
    Wrapper function for creating a Protein-Variation-Graph for a given UniProt Protein.

    For functionality see _create_protein_variation_graph

    :param protein_id: UniProt Protein-ID
    :type protein_id: str
    :param run_name: name of the run this is executed from. Used for saving the protein
        file, graph
    :type run_name: str

    :return: dict of path to graph, protein id, messages passed to the frontend
    :rtype: dict[str, str, list]
    """

    if not protein_id:
        return dict(
            graph_path=None,
            messages=[dict(level=messages.ERROR, msg="No protein ID provided")],
        )

    out = _create_protein_variation_graph(protein_id=protein_id, run_name=run_name)
    out["protein_id"] = protein_id
    return out


def peptides_to_isoform(
    peptide_df: pd.DataFrame,
    protein_id: str,
    run_name: str,
    k: int = 5,
    allowed_mismatches: int = 2,
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
    the modification failed, the protein id, list of matched peptides, list of unmatched
    peptides, messages passed to the frontend
    :rtype: dict[str, str, list, list, list]
    """

    assert isinstance(
        allowed_mismatches, int
    ), f"allowed_mismatches must be int, is {type(allowed_mismatches)}"
    assert (
        allowed_mismatches >= 0
    ), f"allowed mismatches must be >= 0, is {allowed_mismatches}"

    assert isinstance(k, int), f"k must be an integer, is {type(k)}"
    assert k > 0, f"k must be > 0, is {k}"

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

    print("ref_index", ref_index)
    print("graph_index", graph_index)
    print("longest_paths", longest_paths)

    potential_peptide_matches, peptide_mismatches = _potential_peptide_matches(
        allowed_mismatches=allowed_mismatches,
        k=k,
        peptides=peptides,
        ref_index=ref_index,
        seq_len=seq_len,
    )

    peptide_match_node_start_end, peptide_mismatches = _match_potential_matches(
        potential_peptide_matches=potential_peptide_matches,
        graph_index=graph_index,
        peptide_mismatches=peptide_mismatches,
        allowed_mismatches=allowed_mismatches,
        graph=protein_graph,
        longest_paths=longest_paths,
    )

    contigs = _create_contigs_dict(peptide_match_node_start_end)
    modified_graph = _modify_graph(protein_graph, contigs)

    logger.info(f"writing modified graph at {matched_graph_path}")
    nx.write_graphml(modified_graph, matched_graph_path)

    msg = f"matched-peptides-graph created at {matched_graph_path}"
    return dict(
        graph_path=str(matched_graph_path),
        protein_id=protein_id,
        peptide_matches=sorted(list(peptide_match_node_start_end.keys())),
        peptide_mismatches=sorted(peptide_mismatches),
        messages=[dict(level=messages.INFO, msg=msg)],
    )


def _create_protein_variation_graph(protein_id: str, run_name: str) -> dict:
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
    path_to_protein_file, filtered_blocks, request = _get_protein_file(
        protein_id, run_path
    )

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

    This is intended to be used with graphs that include the VARIANT feature. Features
    that lengthen the protein are not supported.

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
            node_len = 0
        else:
            node_len = len(protein_graph.nodes[node]["aminoacid"])

        # visiting in topological order, so distance to node should be set already
        if distances[node] != -1:
            for neighbor in protein_graph.neighbors(node):
                distances[neighbor] = max(
                    distances[neighbor], distances[node] + node_len
                )
        else:
            raise Exception(
                f"The node {node} was not visited in the topological order (distance should be set already)"
            )

    longest_paths = dict(sorted(distances.items(), key=lambda x: x[1]))

    return longest_paths


def _get_protein_file(
    protein_id: str, run_path: Path
) -> (Path, requests.models.Response | None):
    path_to_graphs = run_path / "graphs"
    protein_file_path = path_to_graphs / f"{protein_id}.txt"
    filtered_protein_file_path = path_to_graphs / f"{protein_id}.txt"
    url = f"https://rest.uniprot.org/uniprotkb/{protein_id}.txt"
    r = None

    path_to_graphs.mkdir(parents=True, exist_ok=True)

    if protein_file_path.exists():
        logger.info(
            f"Protein file {protein_file_path} already exists. Skipping download."
        )
    else:
        logger.info(f"Downloading protein file from {url}")
        r = requests.get(url)
        r.raise_for_status()

        protein_file_path.write_bytes(r.content)

    filtered_lines, filtered_blocks = _parse_file(protein_file_path)
    with open(filtered_protein_file_path, "w") as file:
        file.writelines(filtered_lines)

    return filtered_protein_file_path, filtered_blocks, r


def _parse_file(file_path):
    """
    The current implementation of the matching algorithm relies on the longest path
    through the graph to be exactly as long as the reference sequence. This needs to be
    the case because otherwise the potential peptide match positions from
    `_potential_peptide_matches` will not be useful.
    For this reason, we filter out all "VARIANT" features that cause the length of the
    longest path to be longer than the reference sequence.
    """

    def is_valid_block(block_lines):
        """
        valid "VARIANT" blocks are those that don't substitute more amino acids than
        they replace
        """
        pre_aa = None
        post_line = None

        for line in block_lines:
            if "/note" in line:
                if "Missing" in line:
                    return True
                pre_aa = line.split("->")[0].split()[1].replace('/note="', "").strip()
                post_line = line.split("->")[1].split(" (")[0].strip()

        if (
            pre_aa is not None
            and post_line is not None
            and len(pre_aa) >= len(post_line)
        ):
            return True
        return False

    with open(file_path, "r") as file:
        lines = file.readlines()

    filtered_lines = []
    block_lines = []
    filtered_blocks = []
    in_variant_block = False

    for line in lines:
        line_seg = line.split()
        if len(line_seg) == 3 and line_seg[0] == "FT" and line_seg[1].isupper():
            block_start = True
        else:
            block_start = False

        if block_start:
            if in_variant_block and len(block_lines) > 0:
                if not is_valid_block(block_lines):
                    filtered_lines = filtered_lines[: -len(block_lines)]
                    filtered_blocks.append((block_lines,))
                block_lines = []
            if "VARIANT" in line:
                in_variant_block = True
            else:
                in_variant_block = False

        if in_variant_block:
            block_lines.append(line)
        filtered_lines.append(line)

    if in_variant_block and len(block_lines) > 0:
        if not is_valid_block(block_lines):
            filtered_lines = filtered_lines[: -len(block_lines)]

    return filtered_lines, filtered_blocks


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


def _potential_peptide_matches(
    allowed_mismatches: int, k: int, peptides: list, ref_index: dict, seq_len: int
):
    """
    Get potential start positions for peptides on reference sequence. This is done by
    looking up the k-mers of the peptide in the reference sequence index.

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
    Creates mapping from node to start and end position of contigs as well as the
    peptide(s) that is responsible for the match.

    :param node_start_end: dict of peptide to dict of start index of peptide match to
    dict of node to tuple of start and end positions of matches within the node
    :type node_start_end: dict[str, dict[int, dict[str, tuple[int, int]]]]

    :return: dict of node to list of triple of start position, end position and
    peptide(s) responsible for match
    """

    node_match_data = {}
    for peptide, start_pos_dict in node_start_end.items():
        for start_index, node_dict in start_pos_dict.items():
            for node, start_end in node_dict.items():
                if node not in node_match_data:
                    node_match_data[node] = {
                        "match_locations": [(start_end[0], start_end[1], peptide)],
                    }
                else:
                    node_match_data[node]["match_locations"].append(
                        (start_end[0], start_end[1], peptide)
                    )

    for node in node_match_data:
        node_match_data[node]["match_locations"] = sorted(
            node_match_data[node]["match_locations"]
        )

    # merge tuples where start of second tuple is smaller or equal to end of first tuple
    node_mod = {}
    for node, node_dict in node_match_data.items():
        new_positions_list = []
        for start, end, peptide in node_dict["match_locations"]:
            if not len(new_positions_list):
                new_positions_list.append((start, end, peptide))
                continue
            if start <= new_positions_list[-1][1]:
                new_positions_list[-1] = (
                    new_positions_list[-1][0],
                    end,
                    new_positions_list[-1][2] + ";" + peptide,
                )
            else:
                new_positions_list.append((start, end, peptide))

        node_mod[node] = {
            "contigs": new_positions_list,
        }

    return node_mod


def _match_potential_matches(
    potential_peptide_matches,
    graph_index,
    peptide_mismatches,
    allowed_mismatches,
    graph,
    longest_paths,
):
    """
    Matches the potential peptide matches to the graph. This function utilizes a
    recursive matching method that branches off at the end of each node that is matches
    to the end while there is still amino acids left over in the peptide. A new
    recursion is opened for each successor of a node, given the scenario above.
    A recursion is closed if the end of the peptide is reached or if the number of mismatches
    exceeds the allowed number of mismatches. This leads to potential run time problems
    for many allowed mismatches and long peptides in graphs with frequent Variations.

    For the recursive method, see below.

    :param potential_peptide_matches: dict of peptide to list of starting positions
    :type potential_peptide_matches: dict[str, list[int]]
    :param graph_index: list of lists, each list contains the nodes and AAs at that
    given index along the longest path through the graph
    :type graph_index: list[list[tuple[str, str]]]
    :param peptide_mismatches: list of peptides that did not match to the reference
    sequence
    :type peptide_mismatches: list[str]
    :param allowed_mismatches: number of mismatches allowed for a peptide to be
    considered a match
    :type allowed_mismatches: int
    :param graph: protein variation graph, as created by ProtGraph
    (-> _create_protein_variation_graph)
    :type graph: networkx.DiGraph
    :param longest_paths: length of longest path through the graph to each node
    :type longest_paths: dict[str, int]

    return: dict of peptide to dict of start index of peptide match to dict of node
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
        """
        Recursive function that matches a peptide to the graph. The function branches
        off at the end of each node that is matches to the end while there is still
        amino acids left over in the peptide. A new recursion is opened for each
        successor of a node, given the scenario above. A recursion is closed if the end
        of the peptide is reached or if the number of mismatches exceeds the allowed
        number of mismatches.
        For cases where multiple paths through the graph are possible to match to a
        given peptide from a starting position, the function will return the path with
        the least number of mismatches. If the number of mismatches is equal,
        the first of the equal options will be returned.

        :param mismatches: number of mismatches so far
        :type mismatches: int
        :param allowed_mismatches: number of mismatches allowed per start position
        :type allowed_mismatches: int
        :param graph: protein variation graph, as created by ProtGraph
        (-> _create_protein_variation_graph)
        :type graph: networkx.DiGraph
        :param current_node: current node in the graph, starting with the node of the match start
        :type current_node: str
        :param left_over_peptide: peptide that still needs to be matched to the graph
        :type left_over_peptide: str
        :param node_match_data: dict of node to tuple of start position, end position
        :param current_index: index of the amino acid in the current node that is being
        matched to the peptide
        :type current_index: int

        :return: tuple of bool, dict of node to tuple of start position, end position,
        number of mismatches
        :rtype: tuple[bool, dict[str, tuple[int, int]], int]
        """

        if mismatches > allowed_mismatches:
            return False, {}, mismatches
        if not left_over_peptide:
            return True, node_match_data, mismatches

        # check if leftover peptide and rest of aminoacids in current node match
        # if so, add node and start and end position to node_match_data,
        # return True, node_match_data, mismatches
        last_index = current_index
        added_nodes = []
        for i, label_aa in enumerate(
            graph.nodes[current_node]["aminoacid"][current_index:]
        ):
            if i > len(left_over_peptide) - 1:
                return True, node_match_data, mismatches
            if label_aa != left_over_peptide[i]:
                mismatches += 1
            if mismatches > allowed_mismatches:
                return False, {}, mismatches
            if current_node in added_nodes:
                node_match_data[current_node] = (
                    node_match_data[current_node][0],
                    node_match_data[current_node][1] + 1,
                )
            else:
                node_match_data[current_node] = (current_index, current_index)
                added_nodes.append(current_node)

            last_index = i

        # node is matched til end, peptide not done
        data_from_succ = {}
        recursion_start_mismatches = mismatches
        for succ in graph.successors(current_node):
            recursion_start_data = node_match_data.copy()
            match, match_data_from_succ, mismatches = _match_on_graph(
                recursion_start_mismatches,
                allowed_mismatches,
                graph,
                succ,
                left_over_peptide[last_index + 1 :],
                recursion_start_data,
                0,
            )
            if match:
                data_from_succ[succ] = (match, match_data_from_succ, mismatches)
        if data_from_succ:
            return_val = min(data_from_succ.values(), key=lambda item: item[2])
            return return_val
        else:
            return False, {}, mismatches

    peptide_match_info = {}
    for peptide, indices in potential_peptide_matches.items():
        peptide_match_nodes = {}  # store positions of matches for each node
        for match_start_index in indices:  # start index is of ref_index
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
                logger.debug(f"matched {peptide} at {match_start_index}")
                logger.debug(f"match data: {node_match_data}")
                peptide_match_nodes[match_start_index] = node_match_data
            else:
                logger.debug(f"mismatched start pos {match_start_index} for {peptide}")
        if peptide_match_nodes:
            peptide_match_info[peptide] = peptide_match_nodes
        else:
            peptide_mismatches.add(peptide)

    return peptide_match_info, list(peptide_mismatches)


def _modify_graph(graph, contig_positions):
    """
    Splits nodes of graph at into new contig nodes defined by the start- and
    end-positions in contig_positions. Adds `match` attribute to nodes, "true" when
    contig, "false" if not. Adds `peptide` attribute to match nodes with a string of ';'
    separated peptides that are responsible for the matchSink (__end__) current_node
    will end up without `match`-attribute.

    :param graph: Protein Graph to be modified
    :type: nx.DiGraph
    :param contig_positions: Dict from current_node to contig-positions {current_node: [(start, end)]}.
    :type: dict(list[tuple])
    :param longest_paths: mapping from current_node to the longest path to current_node
    (-> _longest_paths())
    :type: dict
    :return: modified protein graph, with contigs & not-matched AAs as nodes, indicated
    by current_node attribute `matched`
    """

    def _node_length(node):
        return len(graph.nodes[node]["aminoacid"])

    logger.info("updating graph to visualise peptide matches")
    for current_node, node_dict in contig_positions.items():
        contigs = node_dict["contigs"]
        chars_removed = 0
        for start, end, peptide in contigs:
            start = start - chars_removed
            end = end - chars_removed
            first_node = None
            second_node = None
            third_node = None
            if start == 0 and end == _node_length(current_node) - 1:
                logger.debug(
                    f"matched whole current_node {current_node}, contig: ({start, end})"
                )
                nx.set_node_attributes(
                    graph,
                    {current_node: {"match": "true", "peptides": peptide}},
                )
                continue

            before_node_id = None
            # check if contig starts at beginning of current_node, if not create before_node
            if start != 0:
                before_node_id = f"n{len(graph.nodes)}"
                before_node_label = graph.nodes[current_node]["aminoacid"][:start]
                graph.add_node(
                    before_node_id,
                    aminoacid=before_node_label,
                    match="false",
                )

            match_node_id = None
            after_node_label = None
            # check if after_node is needed, if yes create match current_node
            if end != _node_length(current_node) - 1:
                if before_node_id:  # before_node, match_node and after_node
                    match_node_id = f"n{len(graph.nodes)}"
                    match_node_label = graph.nodes[current_node]["aminoacid"][
                        start : end + 1
                    ]
                    graph.add_node(
                        match_node_id,
                        aminoacid=match_node_label,
                        match="true",
                        peptides=peptide,
                    )
                    # adopt current_node to be after_node
                    after_node_label = graph.nodes[current_node]["aminoacid"][end + 1 :]
                    nx.set_node_attributes(
                        graph,
                        {
                            current_node: {
                                "aminoacid": after_node_label,
                                "match": "false",
                            }
                        },
                    )
                    first_node = before_node_id
                    second_node = match_node_id
                    third_node = current_node

                else:  # match_node and after_node
                    match_node_id = f"n{len(graph.nodes)}"
                    match_node_label = graph.nodes[current_node]["aminoacid"][: end + 1]
                    graph.add_node(
                        match_node_id,
                        aminoacid=match_node_label,
                        match="true",
                        peptides=peptide,
                    )

                    # adopt current_node to be match/after_node
                    after_node_label = graph.nodes[current_node]["aminoacid"][end + 1 :]
                    nx.set_node_attributes(
                        graph,
                        {
                            current_node: {
                                "aminoacid": after_node_label,
                                "match": "false",
                            }
                        },
                    )
                    first_node = match_node_id
                    second_node = None
                    third_node = current_node

            else:  # before_node and match_node
                # turn current_node into match_node
                match_node_label = graph.nodes[current_node]["aminoacid"][start:]

                nx.set_node_attributes(
                    graph,
                    {
                        current_node: {
                            "aminoacid": match_node_label,
                            "match": "true",
                            "peptides": peptide,
                        }
                    },
                )
                first_node = before_node_id
                second_node = None
                third_node = current_node

            # add edges
            predecessors = list(graph.predecessors(current_node))
            for pre in predecessors:
                graph.remove_edge(pre, current_node)
                graph.add_edge(pre, first_node)
            if second_node:
                graph.add_edge(first_node, second_node)
                graph.add_edge(second_node, third_node)
            else:
                graph.add_edge(first_node, third_node)

            chars_removed += len(graph.nodes[first_node]["aminoacid"])
            if second_node:
                chars_removed += len(graph.nodes[second_node]["aminoacid"])

    return graph


def _get_peptides(peptide_df: pd.DataFrame, protein_id: str) -> list[str] | None:
    """
    Get peptides for a protein ID from a peptide dataframe.
    Includes all peptides where either just the protein ID occurs or it is in the group
    of proteins associated with a given peptide

    :param peptide_df: Peptide dataframe
    :type peptide_df: pd.DataFrame
    :param protein_id: (UniProt) Protein ID
    :type protein_id: str

    :return: List of peptides
    :rtype: list[str]
    """

    df = peptide_df[peptide_df["Protein ID"].str.contains(protein_id)]
    pattern = rf"^({protein_id}-\d+)$"
    filter = df["Protein ID"].str.contains(pattern)
    df = df[~filter]

    intensity_name = [col for col in df.columns if "intensity" in col.lower()][0]
    df = df.dropna(subset=[intensity_name])
    df = df[df[intensity_name] != 0]

    return df["Sequence"].unique().tolist()
