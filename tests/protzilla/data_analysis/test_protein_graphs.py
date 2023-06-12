import networkx as nx
import pytest

from protzilla.constants.paths import TEST_DATA_PATH
from protzilla.data_analysis.protein_graphs import (
    _create_graph_index,
    _create_ref_seq_index,
    _longest_paths,
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


def test_create_ref_seq_index():
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


def test_create_ref_seq_index_own_protein():
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
