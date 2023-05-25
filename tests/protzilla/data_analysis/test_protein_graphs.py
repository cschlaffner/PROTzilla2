import networkx as nx
import pytest

from protzilla.data_analysis.protein_graphs import _longest_paths


def test_longest_paths_simple():
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
    longest_paths = _longest_paths(G, start_node)

    assert longest_paths["0"] == 0
    assert longest_paths["1"] == 0
    assert longest_paths["2"] == 7


def test_longest_paths_multiple_paths():
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
    longest_paths = _longest_paths(G, start_node)

    assert longest_paths["0"] == 0
    assert longest_paths["1"] == 0
    assert longest_paths["2"] == 3
    assert longest_paths["3"] == 3
    assert longest_paths["4"] == 4
    assert longest_paths["5"] == 6


def test_longest_paths_multiple_shortcut():
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
    longest_paths = _longest_paths(G, start_node)

    assert longest_paths["0"] == 0
    assert longest_paths["1"] == 0
    assert longest_paths["2"] == 3
    assert longest_paths["3"] == 3
    assert longest_paths["4"] == 4
    assert longest_paths["5"] == 6


def test_longest_paths_shortcut():
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
    longest_paths = _longest_paths(G, start_node)

    assert longest_paths["0"] == 0
    assert longest_paths["1"] == 0
    assert longest_paths["2"] == 3
    assert longest_paths["3"] == 4
    assert longest_paths["4"] == 5


def test_longest_paths_multi_route():
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
    longest_paths = _longest_paths(G, start_node)

    assert longest_paths["0"] == 0
    assert longest_paths["1"] == 0
    assert longest_paths["2"] == 3
    assert longest_paths["3"] == 3
    assert longest_paths["4"] == 4
    assert longest_paths["5"] == 4
    assert longest_paths["6"] == 4
    assert longest_paths["7"] == 5
    assert longest_paths["8"] == 6
    assert longest_paths["9"] == 8


@pytest.mark.dependency(
    depends=[
        "test_longest_paths_simple",
        "test_longest_paths_multiple_paths",
        "test_longest_paths_multiple_shortcut",
        "test_longest_paths_shortcut",
        "test_longest_paths_multi_route",
    ]
)
def test_create_graph_index():
    pass
