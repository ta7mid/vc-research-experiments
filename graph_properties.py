import argparse
import os
import pathlib
import typing

import networkx as nx

import read_graph
import utils

__all__ = [
    "compute",
    "compute_from_file",
    "density",
    "max_and_avg_degrees",
]

logger = utils.configure_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Read a graph from a text file in one of the supported formats and print "
            "its properties in YAML format (`<key>: <value>` pairs on separate lines)."
        )
    )
    _ = parser.add_argument(
        "graph_filepath",
        nargs="?",
        help=(
            "Path to the file containing the graph representation; if this argument is "
            "either not provided or provided as an empty string, the path will be read "
            "from stdin"
        ),
    )
    _ = parser.add_argument(
        "-f",
        "--format",
        choices=("mtx", "edges"),
        help=(
            "Representation format of the input graph (default: guess from the "
            "filename extension)"
        ),
    )

    args = parser.parse_args()

    if not args.graph_filepath:
        args.graph_filepath = input()

    props = compute_from_file(args.graph_filepath, args.format)

    logger.debug("Printing analysis results.")
    for key, val in props.items():
        print(f"{key}: {format(val)}\n")


def compute_from_file(
    filepath: pathlib.Path | os.PathLike[typing.Any] | str,
    format: typing.Literal["mtx", "edges"] | str | None = None,
) -> dict[str, int | float | bool]:
    """Reads a graph from a file in one of the supported formats and computes its
    properties that are relevant for our experiments."""

    g = read_graph.from_file(filepath, format)
    return compute(g)


def compute(g: nx.Graph) -> dict[str, int | float | bool]:
    r"""Computes the following metadata and statistical properties of a graph:

    * ``"order"``: number of nodes in the graph
    * ``"size"``: number of edges in the graph
    * ``"max_degree"``: maximum degree of any node in the graph
    * ``"avg_degree"``: average degree of nodes in the graph
    * ``"density"``: density of the graph
    * ``"connected"``: whether the graph is connected or not

    :return: a dictionary containing the properties of the graph with the keys
        described above
    """

    max_deg, avg_deg = max_and_avg_degrees(g)
    return {
        "order": g.order(),
        "size": g.size(),
        "max_degree": max_deg,
        "avg_degree": avg_deg,
        "density": density(g),
        "connected": nx.is_connected(g),
    }


def max_and_avg_degrees(g: nx.Graph) -> tuple[int, float]:
    max_deg = 0
    total_deg = 0
    for _, deg in g.degree:
        d = int(deg)
        max_deg = max(max_deg, d)
        total_deg += d
    return max_deg, total_deg / g.order()


def density(g: nx.Graph) -> float:
    return 2 * g.size() / (g.order() * (g.order() - 1))


def format_value(val: int | float | bool) -> str:
    match val:
        case bool():
            return "yes" if val else "no"
        case _:
            return str(val)


if __name__ == "__main__":
    main()
