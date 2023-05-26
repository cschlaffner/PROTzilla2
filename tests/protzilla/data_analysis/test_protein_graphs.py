import networkx as nx
import pytest

from protzilla.data_analysis.protein_graphs import _create_graph_index, _longest_paths


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

    return G, start_node


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
    return G, start_node


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

    return G, start_node


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
    return G, start_node


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
    return G, start_node


def test_longest_paths_simple(simple_graph):
    G, start_node = simple_graph
    longest_paths = _longest_paths(G, start_node)

    planned = {"0": 0, "1": 0, "2": 7}
    assert longest_paths == planned


def test_longest_paths_multiple_paths(multi_route):
    G, start_node = multi_route
    longest_paths = _longest_paths(G, start_node)

    planned = {"0": 0, "1": 0, "2": 3, "3": 3, "4": 4, "5": 6}
    assert longest_paths == planned


def test_longest_paths_multiple_shortcut(multi_route_shortcut):
    G, start_node = multi_route_shortcut
    longest_paths = _longest_paths(G, start_node)

    planned = {"0": 0, "1": 0, "2": 3, "3": 3, "4": 4, "5": 6}
    assert longest_paths == planned


def test_longest_paths_shortcut(shortcut):
    G, start_node = shortcut
    longest_paths = _longest_paths(G, start_node)

    planned = {"0": 0, "1": 0, "2": 3, "3": 4, "4": 5}
    assert longest_paths == planned


def test_longest_paths_multi_route(complex_route):
    G, start_node = complex_route
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
    G, start_node = simple_graph
    index = _create_graph_index(G, start_node)

    planned = [["1"], ["1"], ["1"], ["1"], ["1"], ["1"], ["1"]]
    assert index == planned


def test_create_graph_index_shortcut(shortcut):
    G, start_node = shortcut
    index = _create_graph_index(G, start_node)

    planned = [["1"], ["1"], ["1"], ["2"], ["3"]]
    assert index == planned


def test_create_graph_index_multiple(multi_route):
    G, start_node = multi_route
    index = _create_graph_index(G, start_node)

    planned = [["1"], ["1"], ["1"], ["2", "3"], ["4"], ["4"]]
    assert index == planned


def test_create_graph_index_multiple_shortcut(multi_route_shortcut):
    G, start_node = multi_route_shortcut
    index = _create_graph_index(G, start_node)

    planned = [["1"], ["1"], ["1"], ["2", "3"], ["4"], ["4"]]
    assert index == planned


def test_create_graph_index_multi_route(complex_route):
    G, start_node = complex_route
    index = _create_graph_index(G, start_node)

    planned = [["1"], ["1"], ["1"], ["2", "3"], ["4", "5", "6"], ["7"], ["8"], ["8"]]
    assert index == planned
