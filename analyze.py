import argparse
import logging
import os
import pathlib
import types
import typing

import networkx as nx

import parse

__all__ = [
    "analyze_graph",
    "graph_properties",
    "graph_max_and_avg_degrees",
    "graph_density",
]

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        filename=os.environ.get("LOGFILE", None),
        level=os.environ.get("LOGLEVEL", "WARNING").upper(),
    )

    parser = argparse.ArgumentParser(
        description=(
            "Read a graph from a text file in one of the supported formats and print its "
            "properties in YAML format."
        )
    )
    _ = parser.add_argument(
        "graph_filepath",
        type=str,
        help=(
            "Path to the file containing the graph representation, or '-' to read the path from "
            "stdin"
        ),
    )
    _ = parser.add_argument(
        "-format",
        choices=("mtx", "edges"),
        default=None,
        help=(
            "Representation format of the input graph (default: guess from the filename extension)"
        ),
    )

    args = parser.parse_args()

    if args.graph_filepath == "-":
        args.graph_filepath = input()

    analysis = analyze_graph(args.graph_filepath, args.format)

    logger.debug("Printing analysis results.")
    for key, val in analysis.items():
        print("{}: {}\n".format(key, val))


def analyze_graph(
    filepath: pathlib.Path | os.PathLike[typing.Any] | str,
    format: typing.Literal["mtx", "edges"] | str | types.NoneType = None,
) -> dict[str, int | float]:
    """Reads a graph from a file in one of the supported formats."""

    g = parse.parse_graph(filepath, format)
    return graph_properties(g)


def graph_properties(g: nx.Graph) -> dict[str, int | float]:
    max_deg, avg_deg = graph_max_and_avg_degrees(g)
    return {
        "nodes": g.order(),
        "edges": g.size(),
        "max_degree": max_deg,
        "avg_degree": avg_deg,
        "density": graph_density(g),
        "is_connected": int(nx.is_connected(g)),
    }


def graph_max_and_avg_degrees(g: nx.Graph) -> tuple[int, float]:
    max_deg = 0
    total_deg = 0
    for _, deg in g.degree:
        d = int(deg)
        max_deg = max(max_deg, d)
        total_deg += d
    return max_deg, total_deg / g.order()


def graph_density(g: nx.Graph) -> float:
    return 2 * g.size() / (g.order() * (g.order() - 1))


if __name__ == "__main__":
    main()
