import logging
import re

import networkx as nx

from protzilla.constants.logging import logger


def _create_graph_index(protein_graph: nx.DiGraph, seq_len: int):
    """
    create a mapping from the position in the protein (using the longest path) to
    node(s) in the graph

    TODO: this might be broken (in conjunction with the ref.-seq index) for versions where a ref.-seq is shorter than the longest path

    :param protein_graph: Protein-Graph as created by ProtGraph. Expected to have at
        least three nodes; one source, one sink, labeled by `__start__` and `__end__`.
        The labels of nodes are expected to be in the field "aminoacid".
    :type protein_graph: nx.DiGraph
    :param seq_len: length of the reference sequence of the Protein to map to
    :type seq_len: int

    :return: `index` of structure {aminoacid_pos : [nodes]}, `msg` with potential error
        info, `longest_paths`: {node: longest path counting aminoacids}
    """
    for node in protein_graph.nodes:
        if protein_graph.nodes[node]["aminoacid"] == "__start__":
            starting_point = node
            break
    else:
        msg = "No starting point found in the graph. An error in the graph creation is likely."
        logger.critical(msg)
        return None, msg, None

    longest_paths = _longest_paths(protein_graph, starting_point)

    for node in protein_graph.nodes:
        if (
            protein_graph.nodes[node]["aminoacid"] == "__end__"
            and longest_paths[node] < seq_len
        ):
            msg = f"The longest path to the last node is shorter than the reference sequence. An error in the graph creation is likely. Node: {node}, longest path: {longest_paths[node]}, seq_len: {seq_len}"
            logger.critical(msg)
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
    create mapping from node to distance where the distance is the longest path
    from the starting point to each node

    A Variation is assumed to only ever be one aminoacid long.

    :param protein_graph: Protein-Graph as created by ProtGraph \
        (-> _create_protein_variation_graph)
    :type: nx.DiGraph
    :param start_node: Source of protein_graph
    :type: str

    :return: dict {node: length of the longest path to node}
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
        assert node == d_node, f"order is unequal to topological order, {longest_paths}"

    return longest_paths


def _create_ref_seq_index(protein_path: str, k: int = 5):
    """
    Create mapping from kmer of reference_sequence of protein to starting position(s) \
    of kmer in reference_sequence

    :param protein_path: Path to protein file from UniProt (.txt)
    :type: str
    :param k: length of kmers
    :type: int
    :return: index {kmer: [starting positions]}, reference sequence, length of reference
        sequence
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

    logging.debug("Finished creating reference sequence index")
    return index, ref_seq, seq_len


def _get_ref_seq(protein_path: str):
    """
    Parses Protein-File in UniProt SP-EMBL format in .txt files. Extracts reference
    sequence and sequence length.

    SP-EMBL Description: https://web.expasy.org/docs/userman.html

    :raises ValueError: If no lines were matched to the sequence pattern or if no
    sequence was found or if no sequence length was found.

    :param protein_path: Path to Protein-File in UniProt .txt format.
    :type: str

    :return: reference sequence of Protein, sequence length
    """

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

    if not found_lines:
        raise ValueError(f"Could not find lines with Sequence in {protein_path}")

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
        raise ValueError(
            f"Could not find sequence for protein at path {str(protein_path)}"
        )
    if seq_len is None or not isinstance(seq_len, int) or seq_len < 1:
        raise ValueError(
            f"Could not find sequence length for protein file at path {protein_path}"
        )

    return ref_seq, seq_len


def _match_peptides(
    allowed_mismatches: int, k: int, peptides: list, ref_index: dict, ref_seq: str
):
    """
    # TODO peptides aren't yet matched if a mismatch occurs within the first k chars
    Match peptides to reference sequence. `allowed_mismatches` many mismatches are
    allowed per try to match peptide to a potential start position in ref_index

    :param allowed_mismatches: number of mismatches allowed per peptide-match try
    :type: int
    :param k: size of kmer
    :type int:
    :param peptides: list of peptide-strings
    :type: list
    :param ref_index: mapping from kmer to match-positions on reference sequence
    :type: dict(kmer: [starting position]}
    :param ref_seq: reference sequence of protein
    :type: str
    :return: dict(peptide: [match start on reference sequence]),
    list(peptides without match)
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
                    break

            if mismatch_counter <= allowed_mismatches:
                matched_starts.append(match_start_pos)
                # append to easily check if peptide was previously matched for further
                # starting positions
                peptide_matches[peptide] = []
                if peptide in peptide_mismatches:
                    peptide_mismatches.remove(peptide)
            else:
                peptide_mismatches.add(peptide)
        if matched_starts:
            peptide_matches[peptide] = matched_starts

    logger.debug(f"peptide matches - peptide:[starting_pos] :: {peptide_matches}")
    logger.debug(f"peptide mismatches: {peptide_mismatches}")

    return peptide_matches, peptide_mismatches
