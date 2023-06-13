import networkx as nx
import pytest

from protzilla.constants.paths import TEST_DATA_PATH
from protzilla.data_analysis.protein_graphs import (
    _create_graph_index,
    _create_ref_seq_index,
    _get_ref_seq,
    _longest_paths,
    _match_peptides,
)


# TODO: add markdown pictures of the graphs
@pytest.fixture
def simple_graph():
    G = nx.DiGraph()
    G.add_edge("0", "1")
    G.add_edge("1", "2")
    nx.set_node_attributes(
        G,
        {
            "0": {"aminoacid": "__start__"},
            "1": {"aminoacid": "ABCDEFG"},
            "2": {"aminoacid": "__end__"},
        },
    )

    start_node = "0"
    seq_len = 7

    return G, start_node, seq_len


@pytest.fixture
def shortcut():
    G = nx.DiGraph()
    G.add_edge("0", "1")
    G.add_edge("1", "2")
    G.add_edge("1", "4")
    G.add_edge("2", "3")
    G.add_edge("3", "4")

    nx.set_node_attributes(
        G,
        {
            "0": {"aminoacid": "__start__"},
            "1": {"aminoacid": "ABC"},
            "2": {"aminoacid": "D"},
            "3": {"aminoacid": "E"},
            "4": {"aminoacid": "__end__"},
        },
    )

    start_node = "0"
    seq_len = 4
    return G, start_node, seq_len


@pytest.fixture
def multi_route():
    G = nx.DiGraph()
    G.add_edge("0", "1")
    G.add_edge("1", "2")
    G.add_edge("1", "3")
    G.add_edge("2", "4")
    G.add_edge("3", "4")
    G.add_edge("4", "5")

    nx.set_node_attributes(
        G,
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
    return G, start_node, seq_len


@pytest.fixture
def multi_route_shortcut():
    G = nx.DiGraph()
    G.add_edge("0", "1")
    G.add_edge("1", "2")
    G.add_edge("1", "3")
    G.add_edge("1", "4")
    G.add_edge("2", "4")
    G.add_edge("3", "4")
    G.add_edge("4", "5")

    nx.set_node_attributes(
        G,
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
    return G, start_node, seq_len


@pytest.fixture
def complex_route():
    G = nx.DiGraph()
    G.add_edge("0", "1")
    G.add_edge("1", "2")
    G.add_edge("1", "3")
    G.add_edge("2", "4")
    G.add_edge("2", "5")
    G.add_edge("3", "5")
    G.add_edge("3", "6")
    G.add_edge("6", "7")
    G.add_edge("4", "8")
    G.add_edge("5", "8")
    G.add_edge("7", "8")
    G.add_edge("8", "9")

    nx.set_node_attributes(
        G,
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
    return G, start_node, seq_len


def test_longest_paths_simple(simple_graph):
    G, start_node, _ = simple_graph
    longest_paths = _longest_paths(G, start_node)

    planned = {"0": 0, "1": 0, "2": 7}
    assert longest_paths == planned


def test_longest_paths_multiple_paths(multi_route):
    G, start_node, _ = multi_route
    longest_paths = _longest_paths(G, start_node)

    planned = {"0": 0, "1": 0, "2": 3, "3": 3, "4": 4, "5": 6}
    assert longest_paths == planned


def test_longest_paths_multiple_shortcut(multi_route_shortcut):
    G, start_node, _ = multi_route_shortcut
    longest_paths = _longest_paths(G, start_node)

    planned = {"0": 0, "1": 0, "2": 3, "3": 3, "4": 4, "5": 6}
    assert longest_paths == planned


def test_longest_paths_shortcut(shortcut):
    G, start_node, _ = shortcut
    longest_paths = _longest_paths(G, start_node)

    planned = {"0": 0, "1": 0, "2": 3, "3": 4, "4": 5}
    assert longest_paths == planned


def test_longest_paths_multi_route(complex_route):
    G, start_node, _ = complex_route
    longest_paths = _longest_paths(G, start_node)

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
    G, _, seq_len = simple_graph
    index, msg, longest_paths = _create_graph_index(G, seq_len)

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
    G, _, seq_len = shortcut
    index, msg, longest_paths = _create_graph_index(G, seq_len)

    planned = [[("1", "A")], [("1", "B")], [("1", "C")], [("2", "D")], [("3", "E")]]
    assert index == planned
    assert msg == ""


def test_create_graph_index_multiple(multi_route):
    G, _, seq_len = multi_route
    index, msg, longest_paths = _create_graph_index(G, seq_len)

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
    G, _, seq_len = multi_route_shortcut
    index, msg, longest_paths = _create_graph_index(G, seq_len)

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
    G, _, seq_len = complex_route
    index, msg, longest_paths = _create_graph_index(G, seq_len)

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


def test_create_graph_index_invalid_start_node():
    G = nx.DiGraph()
    G.add_edge("0", "1")
    G.add_edge("1", "2")
    nx.set_node_attributes(
        G,
        {
            "0": {"aminoacid": "unexpected_label"},
            "1": {"aminoacid": "ABCDEFG"},
            "2": {"aminoacid": "__end__"},
        },
    )
    seq_len = 7

    index, msg, longest_paths = _create_graph_index(G, seq_len)
    assert index is None
    assert (
        msg
        == "No starting point found in the graph. An error in the graph creation is likely."
    )


def test_create_graph_index_invalid_end_node():
    G = nx.DiGraph()
    G.add_edge("0", "1")
    G.add_edge("1", "2")
    G.add_edge("1", "3")
    G.add_edge("2", "4")
    G.add_edge("3", "4")
    G.add_edge("4", "5")

    nx.set_node_attributes(
        G,
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

    index, msg, longest_paths = _create_graph_index(G, seq_len)
    assert index is None
    partial_error_msg = f"The longest path to the last node is shorter than the reference sequence. An error in the graph creation is likely. Node: "
    assert partial_error_msg in msg


def test_create_ref_seq_index_PKHUO():
    index, _, seq_len = _create_ref_seq_index(
        protein_path=f"{TEST_DATA_PATH}/proteins/PKHUO.txt", k=5
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
    index, _, seq_len = _create_ref_seq_index(
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
    index, _, seq_len = _create_ref_seq_index(
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
    index, _, seq_len = _create_ref_seq_index(
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


def test_get_ref_seq_PKHUO():
    ref_seq, seq_len = _get_ref_seq(f"{TEST_DATA_PATH}/proteins/PKHUO.txt")

    planned_ref_seq = "MASRGALRRCLSPGLPRLLHLSRGLA"
    planned_seq_len = 26

    assert ref_seq == planned_ref_seq
    assert seq_len == planned_seq_len


def test_get_ref_seq_test_protein():
    protein_path = f"{TEST_DATA_PATH}/proteins/test_protein.txt"
    ref_seq, seq_len = _get_ref_seq(protein_path)

    planned_ref_seq = "ABCDEGABCDET"
    planned_seq_len = 12

    assert ref_seq == planned_ref_seq
    assert seq_len == planned_seq_len


def test_get_ref_seq_empty_seq():
    protein_path = f"{TEST_DATA_PATH}/proteins/empty_seq.txt"
    error_msg = f"Could not find sequence for protein at path {protein_path}"
    with pytest.raises(ValueError, match=error_msg):
        ref_seq, seq_len = _get_ref_seq(f"{TEST_DATA_PATH}/proteins/empty_seq.txt")


def test_get_ref_seq_no_seq_len():
    protein_path = f"{TEST_DATA_PATH}/proteins/no_seq_len.txt"
    error_msg = f"Could not find lines with Sequence in {protein_path}"
    with pytest.raises(ValueError, match=error_msg):
        ref_seq, seq_len = _get_ref_seq(f"{TEST_DATA_PATH}/proteins/no_seq_len.txt")


def test_match_peptides_k5():
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
    peptide_matches, peptide_mismatches = _match_peptides(
        allowed_mismatches, k, peptides, ref_seq_index, ref_seq
    )

    planned_peptide_matches = {
        "ABCDEGA": [0],
        "BCDET": [7],
    }
    planned_peptide_mismatches = {"CDE"}

    assert peptide_matches == planned_peptide_matches
    assert peptide_mismatches == planned_peptide_mismatches


def test_match_peptides_k3():
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
    peptide_matches, peptide_mismatches = _match_peptides(
        allowed_mismatches, k, peptides, ref_seq_index, ref_seq
    )

    planned_peptide_matches = {
        "ABCDEGA": [0],
        "BCDET": [1, 7],
        "CDE": [2, 8],
    }
    planned_peptide_mismatches = set()

    assert peptide_matches == planned_peptide_matches
    assert peptide_mismatches == planned_peptide_mismatches


def test_match_peptides_k0():
    peptides = [""]
    allowed_mismatches = 2
    k = 0
    ref_seq_index = {}
    ref_seq = "ABCDEGABCDET"
    error_msg = f"k must be positive integer, but is {k}"
    with pytest.raises(ValueError, match=error_msg):
        peptide_matches, peptide_mismatches = _match_peptides(
            allowed_mismatches, k, peptides, ref_seq_index, ref_seq
        )


def test_match_peptides_mismatches_k3():
    peptides = ["ABCDEGA", "BCDET", "BCDETXXX", "BCDETXX", "CDE", "ABDEF"]
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
    peptide_matches, peptide_mismatches = _match_peptides(
        allowed_mismatches, k, peptides, ref_seq_index, ref_seq
    )

    planned_peptide_matches = {
        "ABCDEGA": [0],
        "BCDET": [1, 7],
        "CDE": [2, 8],
    }
    planned_peptide_mismatches = {"ABDEF", "BCDETXXX", "BCDETXX"}

    assert peptide_matches == planned_peptide_matches
    assert peptide_mismatches == planned_peptide_mismatches


def test_match_peptides_k_str():
    peptides = [""]
    allowed_mismatches = 2
    k = "test_str"
    ref_seq_index = {}
    ref_seq = "ABCDEGABCDET"
    error_msg = f"k must be positive integer, but is {k}"
    with pytest.raises(ValueError, match=error_msg) as e:
        peptide_matches, peptide_mismatches = _match_peptides(
            allowed_mismatches, k, peptides, ref_seq_index, ref_seq
        )


def test_match_peptides_allowed_mismatches_negative():
    peptides = [""]
    allowed_mismatches = -1
    k = 5
    ref_seq_index = {}
    ref_seq = "ABCDEGABCDET"
    error_msg = (
        f"allowed_mismatches must be non-negative integer, but is {allowed_mismatches}"
    )
    with pytest.raises(ValueError, match=error_msg):
        peptide_matches, peptide_mismatches = _match_peptides(
            allowed_mismatches, k, peptides, ref_seq_index, ref_seq
        )
