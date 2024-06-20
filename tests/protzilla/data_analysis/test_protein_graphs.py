import logging
import pprint
import re
import shutil
from pathlib import Path
from unittest import mock

import networkx as nx
import numpy as np
import pandas as pd
import pytest

from protzilla.constants.paths import RUNS_PATH, TEST_DATA_PATH
from protzilla.data_analysis.protein_graphs import (
    _create_contigs_dict,
    _create_graph_index,
    _create_protein_variation_graph,
    _create_reference_sequence_index,
    _get_peptides,
    _get_reference_sequence,
    _longest_paths,
    _match_potential_matches,
    _modify_graph,
    _potential_peptide_matches,
    peptides_to_isoform,
)
from protzilla.utilities.utilities import random_string


# TODO: add markdown pictures of the graphs
@pytest.fixture
def simple_graph():
    graph = nx.DiGraph()
    graph.add_edge("0", "1")
    graph.add_edge("1", "2")
    nx.set_node_attributes(
        graph,
        {
            "0": {"aminoacid": "__start__"},
            "1": {"aminoacid": "ABCDEFG"},
            "2": {"aminoacid": "__end__"},
        },
    )

    start_node = "0"
    seq_len = 7

    return graph, start_node, seq_len


@pytest.fixture
def shortcut():
    graph = nx.DiGraph()
    graph.add_edge("0", "1")
    graph.add_edge("1", "2")
    graph.add_edge("1", "3")
    graph.add_edge("2", "3")
    graph.add_edge("3", "4")

    nx.set_node_attributes(
        graph,
        {
            "0": {"aminoacid": "__start__"},
            "1": {"aminoacid": "ABC"},
            "2": {"aminoacid": "D"},
            "3": {"aminoacid": "E"},
            "4": {"aminoacid": "__end__"},
        },
    )

    start_node = "0"
    seq_len = 5
    return graph, start_node, seq_len


@pytest.fixture
def multi_route():
    graph = nx.DiGraph()
    graph.add_edge("0", "1")
    graph.add_edge("1", "2")
    graph.add_edge("1", "3")
    graph.add_edge("2", "4")
    graph.add_edge("3", "4")
    graph.add_edge("4", "5")

    nx.set_node_attributes(
        graph,
        {
            "0": {"aminoacid": "__start__"},
            "1": {"aminoacid": "ABC"},
            "2": {"aminoacid": "D"},
            "3": {"aminoacid": "E"},
            "4": {"aminoacid": "FG"},
            "5": {"aminoacid": "__end__"},
        },
    )

    start_node = "0"
    seq_len = 6
    return graph, start_node, seq_len


@pytest.fixture
def multi_route_long_nodes():
    graph = nx.DiGraph()
    graph.add_edge("0", "1")
    graph.add_edge("1", "2")
    graph.add_edge("1", "3")
    graph.add_edge("2", "4")
    graph.add_edge("3", "4")
    graph.add_edge("4", "5")

    nx.set_node_attributes(
        graph,
        {
            "0": {"aminoacid": "__start__"},
            "1": {"aminoacid": "ABCDEFG"},
            "2": {"aminoacid": "H"},
            "3": {"aminoacid": "I"},
            "4": {"aminoacid": "JKABCDLMNOP"},
            "5": {"aminoacid": "__end__"},
        },
    )

    start_node = "0"
    seq_len = 6
    return graph, start_node, seq_len


@pytest.fixture
def multi_route_shortcut():
    graph = nx.DiGraph()
    graph.add_edge("0", "1")
    graph.add_edge("1", "2")
    graph.add_edge("1", "3")
    graph.add_edge("1", "4")
    graph.add_edge("2", "4")
    graph.add_edge("3", "4")
    graph.add_edge("4", "5")

    nx.set_node_attributes(
        graph,
        {
            "0": {"aminoacid": "__start__"},
            "1": {"aminoacid": "ABC"},
            "2": {"aminoacid": "D"},
            "3": {"aminoacid": "E"},
            "4": {"aminoacid": "FG"},
            "5": {"aminoacid": "__end__"},
        },
    )

    start_node = "0"
    seq_len = 6
    return graph, start_node, seq_len


@pytest.fixture
def complex_route():
    graph = nx.DiGraph()
    graph.add_edge("0", "1")
    graph.add_edge("1", "2")
    graph.add_edge("1", "3")
    graph.add_edge("2", "4")
    graph.add_edge("2", "5")
    graph.add_edge("3", "5")
    graph.add_edge("3", "6")
    graph.add_edge("6", "7")
    graph.add_edge("4", "8")
    graph.add_edge("5", "8")
    graph.add_edge("7", "8")
    graph.add_edge("8", "9")

    nx.set_node_attributes(
        graph,
        {
            "0": {"aminoacid": "__start__"},
            "1": {"aminoacid": "ABC"},
            "2": {"aminoacid": "D"},
            "3": {"aminoacid": "E"},
            "4": {"aminoacid": "F"},
            "5": {"aminoacid": "H"},
            "6": {"aminoacid": "I"},
            "7": {"aminoacid": "L"},
            "8": {"aminoacid": "RS"},
            "9": {"aminoacid": "__end__"},
        },
    )

    start_node = "0"
    seq_len = 8
    return graph, start_node, seq_len


@pytest.fixture
def test_protein_variation_graph():
    # specific node names are usd because that is exactly the way ProtGraph generates
    # the graph for this specific protein. This is not the most stable way

    graph = nx.DiGraph()

    graph.add_node(
        "n0", aminoacid="__start__", accession="test_protein_variation", position=0.0
    )
    graph.add_node(
        "n1", aminoacid="D", accession="test_protein_variation", position=4.0
    )
    graph.add_node(
        "n2", aminoacid="__end__", accession="test_protein_variation", position=13.0
    )
    graph.add_node("n3", aminoacid="V", accession="test_protein_variation")
    graph.add_node(
        "n4", aminoacid="EGABCDET", accession="test_protein_variation", position=5.0
    )
    graph.add_node(
        "n5", aminoacid="ABC", accession="test_protein_variation", position=1.0
    )

    graph.add_edge("n0", "n5")
    graph.add_edge("n1", "n4")
    graph.add_edge("n3", "n4")
    graph.add_edge("n4", "n2")
    graph.add_edge("n5", "n1")
    graph.add_edge("n5", "n3")

    graph.graph = {"edge_default": {}, "node_default": {}}

    return graph


@pytest.fixture
def test_peptide_df() -> pd.DataFrame:
    # sample, protein groups, sequence, intensity, pep, Group
    peptide_protein_list = (
        ["Sample01", "MadeUp", "COOLSEQ", 123123.0, 0.87452, "D"],
        ["Sample02", "MadeUp-2", "SHOUDLNTAPPEAR", 234234.0, 0.86723, "CTR"],
        ["Sample03", "MadeUp-1;MadeUp", "SHOULDAPPEAR", 234234.0, 0.57263, "D"],
        ["Sample01", "MadeDown", "VCOOLSEQ1", 253840.0, 0.98734, "D"],
        ["Sample02", "MadeDown", "VCOOLSEQ2", np.NaN, 0.86723, "CTR"],
        ["Sample03", "MadeDown", "VCOOLSEQ3", 0, 0.87643, "D"],
        ["Sample01", "MadeLeft", "LCOOLSEQ1", np.NaN, 0.2876, "D"],
        ["Sample02", "MadeLeft-2;MadeLeft", "LCOOLSEQ2", 13200.0, 0.549078, "CTR"],
        ["Sample03", "MadeLeft", "LCOOLSEQ3", 7100.0, 0.726354, "D"],
        ["Sample01", "MadeRight", "RCOOLSEQ", np.NaN, 0.75498, "D"],
        ["Sample02", "MadeRight", "RCOOLSEQ", np.NaN, 0.87423, "CTR"],
        ["Sample03", "MadeRight", "RCOOLSEQ", np.NaN, 0.01922, "D"],
    )

    peptide_df = pd.DataFrame(
        data=peptide_protein_list,
        columns=["Sample", "Protein ID", "Sequence", "Intensity", "PEP", "Group"],
    )

    peptide_df = peptide_df[
        ["Sample", "Protein ID", "Sequence", "Intensity", "PEP", "Group"]
    ]
    peptide_df.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)

    return peptide_df


@pytest.fixture()
def integration_test_peptides() -> pd.DataFrame:
    #              0  3  6
    # Protein Seq: ABCDEGABCDET
    # Variation:      V
    # Missing:        _
    peptide_protein_list = (
        ["Sample01", "test_protein_variation", "ABC", 123123.0, 0.87452],
        ["Sample02", "test_protein_variation", "ABC", 234, 0.87452],
        ["Sample03", "test_protein_variation", "ABC", 234234.0, 0.87452],
        ["Sample01", "test_protein_variation", "DETYYY", 253840.0, 0.98734],
        ["Sample02", "test_protein_variation", "DETYYY", np.NaN, 0.98734],
        ["Sample03", "test_protein_variation", "DETYYY", 0, 0.98734],
        ["Sample01", "test_protein_variation-2", "DETXXX", 253840.0, 0.98734],
        ["Sample02", "test_protein_variation-2", "DETXXX", np.NaN, 0.98734],
        ["Sample03", "test_protein_variation-2", "DETXXX", 0, 0.98734],
        [
            "Sample01",
            "test_protein_variation-1;test_protein_variation",
            "DET",
            253840.0,
            0.98734,
        ],
        [
            "Sample02",
            "test_protein_variation-1;test_protein_variation",
            "DET",
            np.NaN,
            0.98734,
        ],
        [
            "Sample03",
            "test_protein_variation-1;test_protein_variation",
            "DET",
            0,
            0.98734,
        ],
        ["Sample01", "test_protein_variation", "ZZZ", 0, 0.98734],
        ["Sample02", "test_protein_variation", "ZZZ", np.NaN, 0.98734],
        ["Sample03", "test_protein_variation", "ZZZ", 0, 0.98734],
        ["Sample01", "test_protein_variation", "ABCVEG", 9845, 0.98734],
        [
            "Sample01",
            "test_protein-shortcut;test_protein_variation",
            "ABCEGA",
            93478.0,
            0.98734,
        ],
        ["Sample01", "test_protein-shortcut", "ABCDEGA", 93478.0, 0.98734],
    )

    peptide_df = pd.DataFrame(
        data=peptide_protein_list,
        columns=["Sample", "Protein ID", "Sequence", "Intensity", "PEP"],
    )
    peptide_df = peptide_df[["Sample", "Protein ID", "Sequence", "Intensity", "PEP"]]
    peptide_df.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)

    return peptide_df


def test_longest_paths_simple(simple_graph):
    graph, start_node, _ = simple_graph
    longest_paths = _longest_paths(graph, start_node)

    planned = {"0": 0, "1": 0, "2": 7}
    assert longest_paths == planned


def test_longest_paths_multiple_paths(multi_route):
    graph, start_node, _ = multi_route
    longest_paths = _longest_paths(graph, start_node)

    planned = {"0": 0, "1": 0, "2": 3, "3": 3, "4": 4, "5": 6}
    assert longest_paths == planned


def test_longest_paths_multiple_shortcut(multi_route_shortcut):
    graph, start_node, _ = multi_route_shortcut
    longest_paths = _longest_paths(graph, start_node)

    planned = {"0": 0, "1": 0, "2": 3, "3": 3, "4": 4, "5": 6}
    assert longest_paths == planned


def test_longest_paths_shortcut(shortcut):
    graph, start_node, _ = shortcut
    longest_paths = _longest_paths(graph, start_node)

    planned = {"0": 0, "1": 0, "2": 3, "3": 4, "4": 5}
    assert longest_paths == planned


def test_longest_paths_multi_route(complex_route):
    graph, start_node, _ = complex_route
    longest_paths = _longest_paths(graph, start_node)

    planned = {
        "0": 0,
        "1": 0,
        "2": 3,
        "3": 3,
        "4": 4,
        "5": 4,
        "6": 4,
        "7": 5,
        "8": 6,
        "9": 8,
    }
    assert planned == longest_paths


# All graph_index tests depend on the longest_paths tests passing
def test_create_graph_index_simple(simple_graph):
    graph, _, seq_len = simple_graph
    index, msg, longest_paths = _create_graph_index(graph, seq_len)

    planned = [
        [("1", "A")],
        [("1", "B")],
        [("1", "C")],
        [("1", "D")],
        [("1", "E")],
        [("1", "F")],
        [("1", "G")],
    ]
    assert index == planned
    assert msg == ""


def test_create_graph_index_shortcut(shortcut):
    graph, _, seq_len = shortcut
    index, msg, longest_paths = _create_graph_index(graph, seq_len)

    planned = [[("1", "A")], [("1", "B")], [("1", "C")], [("2", "D")], [("3", "E")]]
    assert index == planned
    assert msg == ""


def test_create_graph_index_multiple(multi_route):
    graph, _, seq_len = multi_route
    index, msg, longest_paths = _create_graph_index(graph, seq_len)

    planned = [
        [("1", "A")],
        [("1", "B")],
        [("1", "C")],
        [("2", "D"), ("3", "E")],
        [("4", "F")],
        [("4", "G")],
    ]
    assert index == planned
    assert msg == ""


def test_create_graph_index_multiple_shortcut(multi_route_shortcut):
    graph, _, seq_len = multi_route_shortcut
    index, msg, longest_paths = _create_graph_index(graph, seq_len)

    planned = [
        [("1", "A")],
        [("1", "B")],
        [("1", "C")],
        [("2", "D"), ("3", "E")],
        [("4", "F")],
        [("4", "G")],
    ]
    assert index == planned
    assert msg == ""


def test_create_graph_index_multi_route(complex_route):
    graph, _, seq_len = complex_route
    index, msg, longest_paths = _create_graph_index(graph, seq_len)

    planned = [
        [("1", "A")],
        [("1", "B")],
        [("1", "C")],
        [("2", "D"), ("3", "E")],
        [("4", "F"), ("5", "H"), ("6", "I")],
        [("7", "L")],
        [("8", "R")],
        [("8", "S")],
    ]
    assert index == planned
    assert msg == ""


def test_create_graph_index_invalid_start_node(critical_logger):
    # expecting "error" in log -> supress below critical
    graph = nx.DiGraph()
    graph.add_edge("0", "1")
    graph.add_edge("1", "2")
    nx.set_node_attributes(
        graph,
        {
            "0": {"aminoacid": "unexpected_label"},
            "1": {"aminoacid": "ABCDEFG"},
            "2": {"aminoacid": "__end__"},
        },
    )
    seq_len = 7

    index, msg, longest_paths = _create_graph_index(graph, seq_len)
    assert index is None
    assert (
        msg
        == "No starting point found in the graph. An error in the graph creation is likely."
    )


def test_create_graph_index_invalid_end_node(critical_logger):
    graph = nx.DiGraph()
    graph.add_edge("0", "1")
    graph.add_edge("1", "2")
    graph.add_edge("1", "3")
    graph.add_edge("2", "4")
    graph.add_edge("3", "4")
    graph.add_edge("4", "5")

    nx.set_node_attributes(
        graph,
        {
            "0": {"aminoacid": "__start__"},
            "1": {"aminoacid": "ABC"},
            "2": {"aminoacid": "D"},
            "3": {"aminoacid": "E"},
            "4": {"aminoacid": "FG"},
            "5": {"aminoacid": "__end__"},
        },
    )

    # should be 7, but the graph is invalid
    seq_len = 8

    index, msg, longest_paths = _create_graph_index(graph, seq_len)
    assert index is None
    partial_error_msg = f"The longest path to the last node is shorter than the reference sequence. An error in the graph creation is likely. Node: "
    assert partial_error_msg in msg


def test_create_ref_seq_index_C0HM02():
    index, _, seq_len = _create_reference_sequence_index(
        protein_path=f"{TEST_DATA_PATH}/proteins/C0HM02.txt", k=5
    )

    planned = {
        "MASRG": [0],
        "ASRGA": [1],
        "SRGAL": [2],
        "RGALR": [3],
        "GALRR": [4],
        "ALRRC": [5],
        "LRRCL": [6],
        "RRCLS": [7],
        "RCLSP": [8],
        "CLSPG": [9],
        "LSPGL": [10],
        "SPGLP": [11],
        "PGLPR": [12],
        "GLPRL": [13],
        "LPRLL": [14],
        "PRLLH": [15],
        "RLLHL": [16],
        "LLHLS": [17],
        "LHLSR": [18],
        "HLSRG": [19],
        "LSRGL": [20],
        "SRGLA": [21],
        "RGLA": [22],
        "GLA": [23],
        "LA": [24],
        "A": [25],
    }
    assert index == planned
    assert seq_len == 26


def test_create_ref_seq_index_own_protein_k_1():
    index, _, seq_len = _create_reference_sequence_index(
        protein_path=f"{TEST_DATA_PATH}/proteins/test_protein.txt", k=1
    )

    planned = {
        "A": [0, 6],
        "B": [1, 7],
        "C": [2, 8],
        "D": [3, 9],
        "E": [4, 10],
        "G": [5],
        "T": [11],
    }
    assert index == planned
    assert seq_len == 12


def test_create_ref_seq_index_own_protein_k_2():
    index, _, seq_len = _create_reference_sequence_index(
        protein_path=f"{TEST_DATA_PATH}/proteins/test_protein.txt", k=2
    )

    planned = {
        "AB": [0, 6],
        "BC": [1, 7],
        "CD": [2, 8],
        "DE": [3, 9],
        "EG": [4],
        "GA": [5],
        "ET": [10],
        "T": [11],
    }
    assert index == planned
    assert seq_len == 12


def test_create_ref_seq_index_own_protein_k_5():
    index, _, seq_len = _create_reference_sequence_index(
        protein_path=f"{TEST_DATA_PATH}/proteins/test_protein.txt", k=5
    )

    planned = {
        "ABCDE": [0, 6],
        "BCDEG": [1],
        "CDEGA": [2],
        "DEGAB": [3],
        "EGABC": [4],
        "GABCD": [5],
        "BCDET": [7],
        "CDET": [8],
        "DET": [9],
        "ET": [10],
        "T": [11],
    }
    assert index == planned
    assert seq_len == 12


def test_get_ref_seq_C0HM02():
    ref_seq, seq_len = _get_reference_sequence(f"{TEST_DATA_PATH}/proteins/C0HM02.txt")

    planned_ref_seq = "MASRGALRRCLSPGLPRLLHLSRGLA"
    planned_seq_len = 26

    assert ref_seq == planned_ref_seq
    assert seq_len == planned_seq_len


def test_get_ref_seq_test_protein():
    protein_path = f"{TEST_DATA_PATH}/proteins/test_protein.txt"
    ref_seq, seq_len = _get_reference_sequence(protein_path)

    planned_ref_seq = "ABCDEGABCDET"
    planned_seq_len = 12

    assert ref_seq == planned_ref_seq
    assert seq_len == planned_seq_len


def test_get_ref_seq_empty_seq():
    protein_path = Path(TEST_DATA_PATH, "proteins", "empty_seq.txt")
    error_msg = f"Could not find sequence for protein at path {protein_path}"
    with pytest.raises(ValueError, match=re.escape(error_msg)):
        _get_reference_sequence(str(protein_path))


def test_get_ref_seq_no_seq_len():
    protein_path = Path(TEST_DATA_PATH, "proteins", "no_seq_len.txt")
    error_msg = f"Could not find lines with Sequence in {protein_path}"
    with pytest.raises(ValueError, match=re.escape(error_msg)):
        _get_reference_sequence(str(protein_path))


def test_potential_peptide_matches_k5():
    peptides = ["ABCDEGA", "BCDET", "CDE"]
    allowed_mismatches = 2
    k = 5
    ref_seq_index = {
        "ABCDE": [0, 6],
        "BCDEG": [1],
        "CDEGA": [2],
        "DEGAB": [3],
        "EGABC": [4],
        "GABCD": [5],
        "BCDET": [7],
        "CDET": [8],
        "DET": [9],
        "ET": [10],
        "T": [11],
    }
    ref_seq = "ABCDEGABCDET"
    peptide_matches, peptide_mismatches = _potential_peptide_matches(
        allowed_mismatches, k, peptides, ref_seq_index, len(ref_seq)
    )

    planned_peptide_matches = {
        "ABCDEGA": [0],
        "BCDET": [7],
    }
    planned_peptide_mismatches = ["CDE"]

    assert peptide_matches == planned_peptide_matches
    assert peptide_mismatches == planned_peptide_mismatches


def test_potential_peptide_matches_k3():
    peptides = ["ABCDEGA", "BCDET", "CDE"]
    allowed_mismatches = 2
    k = 3
    ref_seq_index = {
        "ABC": [0, 6],
        "BCD": [1, 7],
        "CDE": [2, 8],
        "DEG": [3],
        "EGA": [4],
        "GAB": [5],
        "DET": [9],
        "ET": [10],
        "T": [11],
    }
    ref_seq = "ABCDEGABCDET"
    peptide_matches, peptide_mismatches = _potential_peptide_matches(
        allowed_mismatches, k, peptides, ref_seq_index, len(ref_seq)
    )

    planned_peptide_matches = {
        "ABCDEGA": [0],
        "BCDET": [1, 7],
        "CDE": [2, 8],
    }
    planned_peptide_mismatches = []

    assert peptide_matches == planned_peptide_matches
    assert peptide_mismatches == planned_peptide_mismatches


def test_potential_peptide_matches_mismatches_k3():
    peptides = ["ABCDEGA", "BCDET", "CDE", "ABDEF"]
    allowed_mismatches = 2
    k = 3
    ref_seq_index = {
        "ABC": [0, 6],
        "BCD": [1, 7],
        "CDE": [2, 8],
        "DEG": [3],
        "EGA": [4],
        "GAB": [5],
        "DET": [9],
        "ET": [10],
        "T": [11],
    }
    ref_seq = "ABCDEGABCDET"
    peptide_matches, peptide_mismatches = _potential_peptide_matches(
        allowed_mismatches, k, peptides, ref_seq_index, len(ref_seq)
    )

    planned_peptide_matches = {
        "ABCDEGA": [0],
        "BCDET": [1, 7],
        "CDE": [2, 8],
    }
    planned_peptide_mismatches = ["ABDEF"]

    assert peptide_matches == planned_peptide_matches
    assert peptide_mismatches == planned_peptide_mismatches


def test_potential_peptide_matches_k0():
    k = 0
    error_msg = f"k must be positive integer, but is {k}"
    with pytest.raises(ValueError, match=re.escape(error_msg)):
        _potential_peptide_matches(
            allowed_mismatches=2,
            k=k,
            peptides=[""],
            ref_index={},
            seq_len=len("ABCDEGABCDET"),
        )


def test_potential_peptide_matches_k_str():
    peptides = [""]
    allowed_mismatches = 2
    k = "test_str"
    ref_seq_index = {}
    ref_seq = "ABCDEGABCDET"
    error_msg = f"k must be positive integer, but is {k}"
    with pytest.raises(ValueError, match=re.escape(error_msg)):
        _potential_peptide_matches(
            allowed_mismatches, k, peptides, ref_seq_index, len(ref_seq)
        )


def test_potential_peptide_matches_allowed_mismatches_negative():
    peptides = [""]
    allowed_mismatches = -1
    k = 5
    ref_seq_index = {}
    ref_seq = "ABCDEGABCDET"
    error_msg = (
        f"allowed_mismatches must be non-negative integer, but is {allowed_mismatches}"
    )
    with pytest.raises(ValueError, match=re.escape(error_msg)):
        _potential_peptide_matches(
            allowed_mismatches, k, peptides, ref_seq_index, len(ref_seq)
        )


@pytest.mark.skip(reason="Some file read/write error, TODO")
@mock.patch("protzilla.data_analysis.protein_graphs._get_protein_file")
def test_create_prot_variation_graph(
    mock_get_protein_file,
    tests_folder_name,
    test_protein_variation_graph,
    error_logger,
):
    # something is wrong with this test as it fails to write the statistics file (.csv)
    # as it isn't needed for what we do with protgraph, you can ignore errors concerning
    # that

    protein_id = "test_protein_variation"
    protein_path = TEST_DATA_PATH / "proteins" / f"{protein_id}.txt"
    mock_request = mock.MagicMock()
    mock_request.status_code = 200

    run_name = (
        tests_folder_name + "/test_create_prot_variation_graph_" + random_string()
    )
    (RUNS_PATH / run_name).mkdir(exist_ok=True)

    output_folder = RUNS_PATH / run_name / f"graphs"
    graph_path = output_folder / f"{protein_id}.graphml"
    planned_msg = (
        f"Graph created for protein {protein_id} at {graph_path} using {protein_path}"
    )

    mock_get_protein_file.return_value = (protein_path, [], mock_request)
    out_dict = _create_protein_variation_graph(protein_id=protein_id, run_name=run_name)

    planned_out_dict = {
        "graph_path": str(output_folder / f"{protein_id}.graphml"),
        "filtered_blocks": [],
        "messages": [dict(level=logging.INFO, msg=planned_msg)],
    }

    assert out_dict == planned_out_dict
    created_graph = nx.read_graphml(graph_path)
    assert nx.is_isomorphic(created_graph, test_protein_variation_graph)
    assert nx.utils.graphs_equal(created_graph, test_protein_variation_graph)


@mock.patch("protzilla.data_analysis.protein_graphs._get_protein_file")
def test_create_protein_variation_graph_bad_request(
    mock_get_protein_file, critical_logger
):
    # error in log is expected -> surpress error and below using critical_logger

    protein_id = "test_protein_variation"
    protein_path = f"/non/existing/path/{protein_id}.txt"

    mock_request = mock.MagicMock()
    mock_request.status_code = 0
    mock_request.reason = "test_reason"
    mock_request.text = "test_text"

    mock_get_protein_file.return_value = (protein_path, [], mock_request)

    planned_msg = f"error while downloading protein file for {protein_id}. Statuscode:{mock_request.status_code}, {mock_request.reason}. Got: {mock_request.text}. Tip: check if the ID is correct"

    planned_out = dict(
        graph_path=None,
        filtered_blocks=[],
        messages=[
            dict(level=logging.ERROR, msg=planned_msg, trace=mock_request.__dict__)
        ],
    )

    assert (
        _create_protein_variation_graph(protein_id=protein_id, run_name="test_run")
        == planned_out
    )


def test_get_pos_potential_matches_simple(simple_graph):
    graph, _, _ = simple_graph
    graph_index_simple = [
        [("1", "A")],
        [("1", "B")],
        [("1", "C")],
        [("1", "D")],
        [("1", "E")],
        [("1", "F")],
        [("1", "G")],
    ]
    potential_matches = {"ABC": [0], "EFG": [4]}
    planned_match_info = {"ABC": {0: {"1": (0, 2)}}, "EFG": {4: {"1": (4, 6)}}}

    match_info, peptide_mismatches = _match_potential_matches(
        potential_peptide_matches=potential_matches,
        graph_index=graph_index_simple,
        peptide_mismatches=[],
        allowed_mismatches=2,
        graph=graph,
        longest_paths={"1": 0},
    )
    assert planned_match_info == match_info
    assert peptide_mismatches == []


def test_get_pos_potential_matches_1_pep_2_match(multi_route):
    graph, _, _ = multi_route
    graph.nodes["4"]["aminoacid"] = "AB"
    graph_index_mulitroute = [
        [("1", "A")],
        [("1", "B")],
        [("1", "C")],
        [("2", "D"), ("3", "E")],
        [("4", "A")],
        [("4", "B")],
    ]
    potential_matches = {"AB": [0, 4]}
    planned_match_info = {"AB": {0: {"1": (0, 1)}, 4: {"4": (0, 1)}}}

    match_info, peptide_mismatches = _match_potential_matches(
        potential_peptide_matches=potential_matches,
        graph_index=graph_index_mulitroute,
        peptide_mismatches=[],
        allowed_mismatches=2,
        graph=graph,
        longest_paths={"1": 0, "2": 3, "3": 3, "4": 4},
    )
    assert planned_match_info == match_info
    assert peptide_mismatches == []


def test_get_pos_potential_matches_1_pep_2_match_same_node():
    graph = nx.DiGraph()
    graph.add_node("0", aminoacid="__start__")
    graph.add_node("1", aminoacid="ABCDEFGABCD")
    graph.add_node("2", aminoacid="__end__")
    graph.add_edge("0", "1")
    graph.add_edge("1", "2")

    graph_index = [
        [("1", "A")],
        [("1", "B")],
        [("1", "C")],
        [("1", "D")],
        [("1", "E")],
        [("1", "F")],
        [("1", "G")],
        [("1", "A")],
        [("1", "B")],
        [("1", "C")],
        [("1", "D")],
    ]
    potential_matches = {"ABCD": [0, 7]}
    planned_match_info = {"ABCD": {0: {"1": (0, 3)}, 7: {"1": (7, 10)}}}

    match_info, peptide_mismatches = _match_potential_matches(
        potential_peptide_matches=potential_matches,
        graph_index=graph_index,
        peptide_mismatches=[],
        allowed_mismatches=2,
        graph=graph,
        longest_paths={"1": 0},
    )
    assert planned_match_info == match_info
    assert peptide_mismatches == []


def test_get_pos_potential_matches_variation_matching(multi_route):
    graph, _, _ = multi_route
    graph.nodes["4"]["aminoacid"] = "AB"
    graph_index = [
        [("1", "A")],
        [("1", "B")],
        [("1", "C")],
        [("2", "D"), ("3", "E")],
        [("4", "A")],
        [("4", "B")],
    ]
    potential_matches = {"ABCDA": [0]}
    planned_match_info = {"ABCDA": {0: {"1": (0, 2), "2": (0, 0), "4": (0, 0)}}}

    match_info, peptide_mismatches = _match_potential_matches(
        potential_peptide_matches=potential_matches,
        graph_index=graph_index,
        peptide_mismatches=[],
        allowed_mismatches=2,
        graph=graph,
        longest_paths={"1": 0, "2": 3, "3": 3, "4": 4},
    )
    assert planned_match_info == match_info
    assert peptide_mismatches == []


def test_get_pos_potential_matches_shortcut(multi_route_shortcut):
    graph, _, _ = multi_route_shortcut
    graph.nodes["4"]["aminoacid"] = "FGH"
    graph_index = [
        [("1", "A")],
        [("1", "B")],
        [("1", "C")],
        [("2", "D"), ("3", "E")],
        [("4", "F")],
        [("4", "G")],
        [("4", "H")],
    ]
    potential_matches = {"ABCFG": [0]}
    planned_match_info = {"ABCFG": {0: {"1": (0, 2), "4": (0, 1)}}}

    match_info, peptide_mismatches = _match_potential_matches(
        potential_peptide_matches=potential_matches,
        graph_index=graph_index,
        peptide_mismatches=[],
        allowed_mismatches=2,
        graph=graph,
        longest_paths={"1": 0, "2": 3, "3": 3, "4": 4},
    )
    assert planned_match_info == match_info
    assert peptide_mismatches == []


def test_create_contigs_dict_simple():
    node_start_end = {"ABC": {0: {"1": (0, 2)}, 4: {"1": (4, 6)}}}
    planned_contigs = {"1": [(0, 2, "ABC"), (4, 6, "ABC")]}

    contigs = _create_contigs_dict(node_start_end)
    assert planned_contigs == contigs


def test_create_contigs_dict_1_pep_2_match():
    node_start_end = {"ABCD": {0: {"1": (0, 1), "2": (0, 1)}}}
    planned_contigs = {
        "1": [(0, 1, "ABCD")],
        "2": [(0, 1, "ABCD")],
    }

    contigs = _create_contigs_dict(node_start_end)
    assert contigs == planned_contigs


def test_create_contigs_dict_1_pep_2_match_same_node():
    node_start_end = {"ABCD": {0: {"1": (0, 3)}, 7: {"1": (7, 10)}}}
    planned_contigs = {"1": [(0, 3, "ABCD"), (7, 10, "ABCD")]}

    contigs = _create_contigs_dict(node_start_end)
    assert contigs == planned_contigs


def test_create_contigs_dict_2_pep_multi_match():
    node_start_end = {
        "ABCD": {
            0: {"1": (0, 3)},
            7: {"1": (7, 10)},
            12: {"4": (12, 15)},
            19: {"4": (19, 22)},
        },
        "EFA": {5: {"1": (5, 7)}, 17: {"4": (17, 19)}},
    }

    planned_contigs = {
        "1": [(0, 3, "ABCD"), (5, 10, "EFA;ABCD")],
        "4": [(12, 15, "ABCD"), (17, 22, "EFA;ABCD")],
    }

    contigs = _create_contigs_dict(node_start_end)
    assert contigs == planned_contigs


def test_modify_graph_simple_1_pep_start_match(simple_graph, critical_logger):
    # peptide: ABC
    longest_paths = {"1": 0}
    contigs = {"1": [(0, 2, "ABC")]}
    graph, _, _ = simple_graph
    planned_graph = graph.copy()
    planned_graph.add_node("n3", aminoacid="ABC")
    planned_graph.add_edge("0", "n3")
    planned_graph.add_edge("n3", "1")
    planned_graph.remove_edge("0", "1")

    # for node in planned_graph.nodes:
    #     planned_graph.nodes[node]["peptide"] = ""

    nx.set_node_attributes(
        planned_graph,
        {
            "1": {"aminoacid": "DEFG", "match": "false"},
            "n3": {"aminoacid": "ABC", "match": "true", "peptides": "ABC"},
        },
    )

    graph = _modify_graph(graph, contigs)

    assert planned_graph.nodes == graph.nodes
    assert nx.utils.graphs_equal(graph, planned_graph)


def test_modify_graph_simple_1_pep_end_match(simple_graph, critical_logger):
    # "0": {"aminoacid": "__start__"},
    # "1": {"aminoacid": "ABCDEFG"},
    # "2": {"aminoacid": "__end__"},

    # peptide EFG, ref_seq: ABCDEFG
    longest_paths = {"1": 0}
    contigs = {"1": [(4, 6, "EFG")]}
    graph, _, _ = simple_graph
    planned_graph = graph.copy()
    planned_graph.add_node("n3", aminoacid="ABCD", match="false")
    planned_graph.add_edge("0", "n3")
    planned_graph.add_edge("n3", "1")
    planned_graph.remove_edge("0", "1")
    nx.set_node_attributes(
        planned_graph, {"1": {"aminoacid": "EFG", "match": "true", "peptides": "EFG"}}
    )

    graph = _modify_graph(graph, contigs)
    assert nx.utils.graphs_equal(graph, planned_graph)


def test_modify_graph_simple_1_pep_full_match(simple_graph, critical_logger):
    # peptide: ABCDEFG
    longest_paths = {"1": 0}
    contigs = {"1": [(0, 6, "ABCDEFG")]}
    graph, _, _ = simple_graph
    planned_graph = graph.copy()
    nx.set_node_attributes(
        planned_graph,
        {
            "1": {"aminoacid": "ABCDEFG", "match": "true", "peptides": "ABCDEFG"},
        },
    )

    graph = _modify_graph(graph, contigs)
    assert nx.utils.graphs_equal(graph, planned_graph)


def test_modify_graph_simple_2_pep_2_nodes_start_middle_end_match(
    multi_route_long_nodes,
):
    # "0": {"aminoacid": "__start__"},
    # "1": {"aminoacid": "ABCDEFG"},
    #                     0   4
    # "2": {"aminoacid": "H"},
    # "3": {"aminoacid": "I"},
    #                     0
    # "4": {"aminoacid": "JKABCDLMNOP"},
    #                     0 2   6 8
    # "5": {"aminoacid": "__end__"},
    # peptides: ABCD, NOP

    longest_paths = {"1": 0, "2": 7, "3": 7, "4": 8}
    contigs = {
        "1": [(0, 3, "ABCD")],
        "4": [(2, 5, "ABCD"), (8, 10, "NOP")],
    }

    graph, _, _ = multi_route_long_nodes
    planned_graph = graph.copy()
    planned_graph.add_node("n6", aminoacid="ABCD", match="true", peptides="ABCD")
    planned_graph.add_edge("0", "n6")
    planned_graph.add_edge("n6", "1")
    planned_graph.remove_edge("0", "1")
    planned_graph.add_node("n7", aminoacid="JK", match="false")
    planned_graph.add_edge("2", "n7")
    planned_graph.add_edge("3", "n7")
    planned_graph.remove_edge("2", "4")
    planned_graph.remove_edge("3", "4")
    planned_graph.add_node("n8", aminoacid="ABCD", match="true", peptides="ABCD")
    planned_graph.add_edge("n7", "n8")
    planned_graph.add_node("n9", aminoacid="LM", match="false")
    planned_graph.add_edge("n8", "n9")
    planned_graph.add_edge("n9", "4")

    nx.set_node_attributes(
        planned_graph,
        {
            "1": {"aminoacid": "EFG", "match": "false"},
            "2": {"aminoacid": "H"},
            "3": {"aminoacid": "I"},
            "4": {"aminoacid": "NOP", "match": "true", "peptides": "NOP"},
        },
    )

    graph = _modify_graph(graph, contigs)
    assert nx.utils.graphs_equal(graph, planned_graph)


def test_modify_graphs_1_pep_variation_match(multi_route_long_nodes):
    # despite variation matching not yet being implemented when getting start and end
    # position of matches in the graph, once you have correct contigs, variation matches
    # are correctly added to the graph

    # "0": {"aminoacid": "__start__"},
    # "1": {"aminoacid": "ABCDEFG"},
    #                     0   4
    # "2": {"aminoacid": "H"},
    # "3": {"aminoacid": "I"},
    #                     7
    # "4": {"aminoacid": "JKABCDLMNOP"},
    #                     8 10    16
    # "5": {"aminoacid": "__end__"},
    # peptides: EFGHJK

    graph, _, _ = multi_route_long_nodes
    longest_paths = {"1": 0, "2": 7, "3": 7, "4": 8}
    contigs = {
        "1": [(4, 6, "EFGHJK")],
        "2": [(0, 0, "EFGHJK")],
        "4": [(0, 1, "EFGHJK")],
    }

    planned_graph = graph.copy()
    planned_graph.add_node("n6", aminoacid="ABCD", match="false")
    planned_graph.add_edge("0", "n6")
    planned_graph.add_edge("n6", "1")
    planned_graph.remove_edge("0", "1")
    planned_graph.add_node("n7", aminoacid="JK", match="true", peptides="EFGHJK")
    planned_graph.add_edge("2", "n7")
    planned_graph.add_edge("3", "n7")
    planned_graph.add_edge("n7", "4")
    planned_graph.remove_edge("2", "4")
    planned_graph.remove_edge("3", "4")
    nx.set_node_attributes(
        planned_graph,
        {
            "1": {"aminoacid": "EFG", "match": "true", "peptides": "EFGHJK"},
            "2": {"aminoacid": "H", "match": "true", "peptides": "EFGHJK"},
            "3": {"aminoacid": "I"},  # _modify_graph doesn't touch node->no match value
            "4": {"aminoacid": "ABCDLMNOP", "match": "false"},
        },
    )

    graph = _modify_graph(graph, contigs)
    assert nx.utils.graphs_equal(graph, planned_graph)


def test_get_peptides_all_0(test_peptide_df):
    protein_id = "MadeUp"
    peptide_df = test_peptide_df
    peptides = _get_peptides(peptide_df, protein_id, None, None)
    assert peptides == ["COOLSEQ", "SHOULDAPPEAR"]


def test_get_peptides_nan_0(test_peptide_df):
    protein_id = "MadeDown"
    peptide_df = test_peptide_df
    peptides = _get_peptides(peptide_df, protein_id, None, None)
    assert peptides == ["VCOOLSEQ1"]


def test_get_peptides_all_nan(test_peptide_df):
    protein_id = "MadeRight"
    peptide_df = test_peptide_df
    peptides = _get_peptides(peptide_df, protein_id, None, None)
    assert peptides == []


def test_get_peptides_one_nan(test_peptide_df):
    protein_id = "MadeLeft"
    peptide_df = test_peptide_df
    peptides = _get_peptides(peptide_df, protein_id, None, None)
    assert peptides == ["LCOOLSEQ2", "LCOOLSEQ3"]


def test_get_peptides_group_by_sample(test_peptide_df):
    protein_id = "MadeUp"
    peptide_df = test_peptide_df
    peptides = _get_peptides(peptide_df, protein_id, "Sample", ["Sample01"])
    assert peptides == ["COOLSEQ"]


def test_get_peptides_group_by_sample_no_match(test_peptide_df):
    protein_id = "MadeUp"
    peptide_df = test_peptide_df
    peptides = _get_peptides(peptide_df, protein_id, "Sample", ["Sample02"])
    assert peptides == []


def test_get_peptides_group_by_group_D(test_peptide_df):
    protein_id = "MadeUp"
    peptide_df = test_peptide_df
    peptides = _get_peptides(peptide_df, protein_id, "Group", ["D"])
    assert peptides == ["COOLSEQ", "SHOULDAPPEAR"]


def test_get_peptides_group_by_group_CTR(test_peptide_df):
    protein_id = "MadeUp"
    peptide_df = test_peptide_df
    peptides = _get_peptides(peptide_df, protein_id, "Group", ["CTR"])
    assert peptides == []


def test_get_peptides_group_by_group_D_CTR(test_peptide_df):
    protein_id = "MadeLeft"
    peptide_df = test_peptide_df
    peptides = _get_peptides(peptide_df, protein_id, "Group", ["D", "CTR"])
    assert peptides == ["LCOOLSEQ2", "LCOOLSEQ3"]


def test_get_peptides_group_by_non_existent_group(test_peptide_df):
    protein_id = "MadeUp"
    peptide_df = test_peptide_df
    error_msg = f"Group 'NonExistent' not found in peptide_df column 'Group'"
    with pytest.raises(AssertionError, match=re.escape(error_msg)):
        _get_peptides(peptide_df, protein_id, "Group", ["NonExistent"])


def test_get_peptides_group_by_non_existent_grouping(test_peptide_df):
    protein_id = "MadeUp"
    peptide_df = test_peptide_df
    grouping = "NonExistent"
    error_msg = f"Grouping '{grouping}' not found in peptide_df"
    with pytest.raises(AssertionError, match=re.escape(error_msg)):
        _get_peptides(peptide_df, protein_id, grouping, ["D"])


def test_get_peptides_no_grouping_selected_groups(test_peptide_df):
    protein_id = "MadeUp"
    peptide_df = test_peptide_df
    error_msg = "Grouping must be set if selected_groups is set"
    with pytest.raises(ValueError, match=re.escape(error_msg)):
        _get_peptides(peptide_df, protein_id, None, ["D"])


@mock.patch("protzilla.data_analysis.protein_graphs._get_peptides")
def test_peptides_to_isoform_no_peptides(mock_get_peptides, critical_logger):
    mock_get_peptides.return_value = []
    protein_id = "SomeID"
    out_dict = peptides_to_isoform(pd.DataFrame(), protein_id, "run_name")
    assert out_dict["graph_path"] is None
    assert (
        out_dict["messages"][0]["msg"]
        == f"No peptides found for isoform {protein_id} in Peptide Dataframe"
    )


@mock.patch.multiple(
    "protzilla.data_analysis.protein_graphs",
    _get_peptides=mock.MagicMock(return_value=["not_falsey_list"]),
    _create_protein_variation_graph=mock.MagicMock(
        return_value=dict(
            graph_path=None,
            filtered_blocks=[],
            messages=[{"level": logging.ERROR, "msg": "No graph found"}],
        )
    ),
)
def test_peptides_to_isoform_no_graph(critical_logger, tests_folder_name):
    run_name = f"{tests_folder_name}/test_peptides_to_isoform_no_graph"

    protein_id = "SomeID"
    out_dict = peptides_to_isoform(pd.DataFrame(), protein_id, run_name)
    assert out_dict["graph_path"] is None
    assert out_dict["messages"][0]["msg"] == "No graph found"


def test_peptides_to_isoform_integration_test(
    integration_test_peptides,
    test_protein_variation_graph,
    critical_logger,
    tests_folder_name,
):
    run_name = f"{tests_folder_name}/test_peptides_to_isoform_integration_test"
    run_path = RUNS_PATH / run_name
    (run_path / "graphs").mkdir(parents=True, exist_ok=True)
    test_protein_path = Path(TEST_DATA_PATH / "proteins" / "test_protein_variation.txt")
    test_protein_destination = Path(run_path / "graphs" / "test_protein_variation.txt")
    shutil.copy(test_protein_path, test_protein_destination)

    protein_id = "test_protein_variation"
    out_dict = peptides_to_isoform(
        peptide_df=integration_test_peptides,
        protein_id=protein_id,
        run_name=run_name,
        k=3,  # for easier test data creation
        allowed_mismatches=1,
    )

    planned_modified_graph_path = run_path / "graphs" / f"{protein_id}_modified.graphml"
    assert out_dict["graph_path"] == str(planned_modified_graph_path)
    assert Path(planned_modified_graph_path).exists()
    assert list(out_dict["peptide_matches"]) == ["ABC", "ABCVEG", "DET"]
    assert out_dict["peptide_mismatches"] == ["ABCEGA", "DETYYY"]
    assert out_dict["protein_id"] == protein_id

    created_graph = nx.read_graphml(out_dict["graph_path"])

    planned_graph = test_protein_variation_graph.copy()
    planned_graph.add_node("n6", aminoacid="EG", match="true", peptides="ABCVEG")
    planned_graph.add_node("n7", aminoacid="ABC", match="true", peptides="ABC")

    planned_graph.add_edge("n1", "n6")
    planned_graph.add_edge("n3", "n6")
    planned_graph.add_edge("n6", "n7")
    planned_graph.add_edge("n7", "n4")
    planned_graph.remove_edge("n1", "n4")
    planned_graph.remove_edge("n3", "n4")

    nx.set_node_attributes(
        planned_graph,
        {
            "n3": {"aminoacid": "V", "match": "true", "peptides": "ABCVEG"},
            "n4": {"aminoacid": "DET", "match": "true", "peptides": "DET"},
            "n5": {"match": "true", "peptides": "ABC;ABCVEG"},
        },
    )

    assert created_graph.nodes == planned_graph.nodes
    assert nx.utils.graphs_equal(created_graph, planned_graph)


def test_peptides_to_isoform_integration_test_shortcut(
    integration_test_peptides,
    test_protein_variation_graph,
    critical_logger,
    tests_folder_name,
):
    run_name = f"{tests_folder_name}/test_peptides_to_isoform_integration_test_shortcut"
    run_path = RUNS_PATH / run_name
    (run_path / "graphs").mkdir(parents=True, exist_ok=True)

    protein_id = "test_protein-shortcut"
    test_protein_path = Path(TEST_DATA_PATH / "proteins" / f"{protein_id}.txt")
    test_protein_destination = Path(run_path / "graphs" / f"{protein_id}.txt")
    shutil.copy(test_protein_path, test_protein_destination)

    out_dict = peptides_to_isoform(
        peptide_df=integration_test_peptides,
        protein_id=protein_id,
        run_name=run_name,
        k=3,  # k = 3 for easier test data creation
        allowed_mismatches=0,
    )

    planned_modified_graph_path = run_path / "graphs" / f"{protein_id}_modified.graphml"
    assert out_dict["graph_path"] == str(planned_modified_graph_path)
    assert Path(planned_modified_graph_path).exists()
    assert list(out_dict["peptide_matches"]) == ["ABCDEGA", "ABCEGA"]
    assert out_dict["peptide_mismatches"] == []
    assert out_dict["protein_id"] == protein_id

    created_graph = nx.read_graphml(out_dict["graph_path"])

    planned_graph = test_protein_variation_graph.copy()
    planned_graph.add_node(
        "n6", aminoacid="EGA", match="true", peptides="ABCDEGA;ABCEGA"
    )

    planned_graph.add_edge("n1", "n6")
    planned_graph.add_edge("n3", "n6")
    planned_graph.add_edge("n5", "n6")
    planned_graph.add_edge("n6", "n4")
    planned_graph.remove_edge("n1", "n4")
    planned_graph.remove_edge("n3", "n4")

    nx.set_node_attributes(
        planned_graph,
        {
            "n0": {"accession": "test_protein-shortcut"},
            "n1": {
                "accession": "test_protein-shortcut",
                "match": "true",
                "peptides": "ABCDEGA",
            },
            "n2": {"accession": "test_protein-shortcut"},
            "n3": {"accession": "test_protein-shortcut"},
            "n4": {
                "aminoacid": "BCDET",
                "match": "false",
                "accession": "test_protein-shortcut",
            },
            "n5": {
                "match": "true",
                "accession": "test_protein-shortcut",
                "peptides": "ABCDEGA;ABCEGA",
            },
        },
    )

    assert planned_graph.nodes == created_graph.nodes
    assert nx.utils.graphs_equal(planned_graph, created_graph)


def test_graph_index_longer_variations():
    planned_index = [
        [("n11", "A")],
        [("n11", "B")],
        [("n11", "C")],
        [("n1", "D"), ("n5", "V"), ("n7", "F")],
        [("n2", "E"), ("n6", "T"), ("n8", "L"), ("n10", "Q")],
        [("n10", "W"), ("n3", "G")],
        [("n9", "A")],
        [("n9", "B")],
        [("n9", "C")],
        [("n9", "D")],
        [("n9", "E")],
        [("n9", "T")],
    ]
    planned_longest_paths = {
        "n0": 0,
        "n11": 0,
        "n1": 3,
        "n5": 3,
        "n7": 3,
        "n2": 4,
        "n6": 4,
        "n8": 4,
        "n10": 4,
        "n3": 5,
        "n9": 6,
        "n4": 12,
    }

    graph = nx.read_graphml(
        TEST_DATA_PATH / "graphs" / "test_protein_variation_long.graphml"
    )
    graph_index, msg, longest_paths = _create_graph_index(graph, 12)
    assert graph_index == planned_index
    assert longest_paths == planned_longest_paths
    assert msg == ""


def test_peptides_to_isoform_integration_test_longer_variations(
    test_protein_variation_graph,
    critical_logger,
    tests_folder_name,
):
    run_name = f"{tests_folder_name}/test_peptides_to_isoform_integration_test_longer_variations"
    run_path = (
        RUNS_PATH
        / tests_folder_name
        / "test_peptides_to_isoform_integration_test_longer_variations"
    )
    (run_path / "graphs").mkdir(parents=True, exist_ok=True)

    protein_id = "test_protein_variation_long"
    test_protein_path = Path(TEST_DATA_PATH / "proteins" / f"{protein_id}.txt")
    test_protein_destination = Path(run_path / "graphs" / f"{protein_id}.txt")
    shutil.copy(test_protein_path, test_protein_destination)

    peptide_protein_list = (
        ["Sample01", "test_protein_variation_long", "DEG", 123123.0, 0.87452],
        ["Sample01", "test_protein_variation_long", "ABCFQ", 234, 0.87452],
        ["Sample01", "test_protein_variation_long", "ABCVTG", 234234.0, 0.87452],
        ["Sample01", "test_protein_variation_long", "ABCFLA", 234, 0.87452],
        ["Sample01", "test_protein_variation_long", "FLG", 234, 0.87452],
    )
    peptide_df = pd.DataFrame(
        data=peptide_protein_list,
        columns=["Sample", "Protein ID", "Sequence", "Intensity", "PEP"],
    )
    peptide_df = peptide_df[["Sample", "Protein ID", "Sequence", "Intensity", "PEP"]]
    peptide_df.sort_values(by=["Sample", "Protein ID"], ignore_index=True, inplace=True)

    out_dict = peptides_to_isoform(
        peptide_df=peptide_df,
        protein_id=protein_id,
        run_name=run_name,
        k=3,  # for easier test data creation
        allowed_mismatches=0,  # for easier test data creation
    )

    planned_modified_graph_path = run_path / "graphs" / f"{protein_id}_modified.graphml"
    assert out_dict["graph_path"] == str(planned_modified_graph_path)
    assert Path(planned_modified_graph_path).exists()
    assert list(out_dict["peptide_matches"]) == ["ABCFQ", "ABCVTG", "DEG"]
    assert out_dict["peptide_mismatches"] == ["ABCFLA", "FLG"]
    assert out_dict["protein_id"] == protein_id
    assert out_dict["filtered_blocks"] == [
        [
            "FT   VARIANT         5\n",
            'FT                   /note="E -> THISSHOULDBEPARSEDOUT (things)"\n',
            'FT                   /evidence="madethisupastestdata5"\n',
            'FT                   /id="veryOwnID5"\n',
        ]
    ]

    created_graph = nx.read_graphml(planned_modified_graph_path)
    planned_graph = nx.read_graphml(
        TEST_DATA_PATH / "graphs" / "test_protein_variation_long.graphml"
    )
    planned_graph.add_node("n12")
    planned_graph.add_edge("n10", "n12")
    planned_graph.add_edge("n12", "n9")
    planned_graph.remove_edge("n10", "n9")
    nx.set_node_attributes(
        planned_graph,
        {
            "n1": {"match": "true", "peptides": "DEG"},
            "n2": {"match": "true", "peptides": "DEG"},
            "n3": {"match": "true", "peptides": "ABCVTG;DEG"},
            "n5": {"match": "true", "peptides": "ABCVTG"},
            "n6": {"match": "true", "peptides": "ABCVTG"},
            "n7": {"match": "true", "peptides": "ABCFQ"},
            "n10": {"aminoacid": "W", "match": "false"},
            "n11": {"match": "true", "peptides": "ABCFQ;ABCVTG"},
            "n12": {"aminoacid": "Q", "match": "true", "peptides": "ABCFQ"},
        },
    )

    assert created_graph.nodes == planned_graph.nodes
    nx.utils.graphs_equal(planned_graph, created_graph)


def pprint_graphs(graph, planned_graph):
    # for debugging
    print("graph")
    pprint.pprint(graph.__dict__)
    print("planned_graph")
    pprint.pprint(planned_graph.__dict__)
