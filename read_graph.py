#!/usr/bin/env python3

import argparse
import os
import pathlib
import re
import typing
from collections import abc

import networkx as nx
import scipy.io

import utils

__all__ = ["from_edge_list_file", "from_file", "from_mtx_file"]

logger = utils.configure_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Parse a graph from a text file in one of the supported formats and print "
            "an edge-list representation of it."
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
            "filename extension"
        ),
    )
    _ = parser.add_argument(
        "-r",
        "--relabel",
        action="store_true",
        help=(
            "Relabel the vertices of output graph using consecutive non-negative "
            "integers, starting with zero (default: do not relabel)"
        ),
    )

    args = parser.parse_args()

    if not args.graph_filepath:
        args.graph_filepath = input()

    g = from_file(args.graph_filepath, args.format)

    if args.relabel:
        logger.debug("Relabeling nodes.")
        g = nx.convert_node_labels_to_integers(g)

    logger.debug("Printing an edge list representation of the graph.")
    for line in nx.generate_edgelist(g, data=False):
        print(line)


def from_file(
    filepath: pathlib.Path | os.PathLike[typing.Any] | str,
    format: typing.Literal["mtx", "edges"] | str | None = None,
) -> nx.Graph:
    r"""Reads a graph from a file in one of the supported formats."""

    if not os.fspath(filepath):
        raise ValueError("Path must not be empty")

    filepath = pathlib.Path(filepath)

    # if the format is not specified, guess it from the filename extension
    if format is None:
        logger.debug("Guessing the format from the filename suffix.")
        suffix = filepath.suffix
        if suffix == "":
            raise ValueError("Could not determine the format of the input file.")
        format = suffix[1:]

    # otherwise check if the format is valid
    elif format not in ("mtx", "edges"):
        raise ValueError(f"Unrecognized format: {format}")

    match format:
        case "mtx":
            logger.info("Reading as a Matrix Market file.")
            return from_mtx_file(filepath)

        case "edges":
            logger.info("Reading as an edge list file.")
            return from_edge_list_file(filepath)

        case _:
            raise ValueError(f"Unrecognized format: {format}")


def from_mtx_file(filepath: pathlib.Path) -> nx.Graph:
    r"""Reads an adjacency matrix from a file in the Matrix Market format [1]_ and
    : constructs anpy:class:`nx.Graph` from it, following [2]_.

    .. rubric:: References

    .. [1] https://math.nist.gov/MatrixMarket/formats.html#MMformat
    .. [2] https://networkx.org/documentation/stable/reference/readwrite/matrix_market.html
    """

    logger.debug("Reading an adjacency matrix from the Matrix Market data.")
    adj_mat = scipy.io.mmread(filepath)
    dense = scipy.io.mminfo(filepath)[3] == "array"

    if dense:
        logger.debug(
            "Creating nx.Graph from the dense adjacency matrix (all entries given)."
        )
        g = nx.convert_matrix.from_numpy_array(adj_mat)
    else:
        logger.debug(
            "Creating nx.Graph from the sparse adjacency matrix (given like edge list)."
        )
        g = nx.convert_matrix.from_scipy_sparse_array(adj_mat)

    logger.info("Successfully parsed Matrix Market data and created an nx.Graph!")
    return g


def from_edge_list_file(filepath: pathlib.Path) -> nx.Graph:
    r"""Reads a graph represented as a list of edges, one per line, from a file."""

    with open(filepath) as file:
        g = parse_edge_list(file.readlines())

    logger.info("Successfully read as an edge list file and created an nx.Graph!")
    return g


def parse_edge_list(lines: abc.Iterable[str]) -> nx.Graph:
    r"""Parses a graph represented as a list of edges, one per line.

    This implementation is generalized from
    :py:func:`nx.convert_matrix.parse_edgelist` [1]_ to allow both whitespace characters
    (``\s`` in regex) and comma (``,``) to be used as delimiters (to separate the nodes
    of an edge on each line) simultaneously and to allow both ``#`` and ``%`` to be used
    as comment prefixes simultaneously.

    .. rubric:: References

    .. [1] https://networkx.org/documentation/stable/_modules/networkx/readwrite/edgelist.html#parse_edgelist
    """

    g = nx.Graph()
    line_num = 0

    for line in lines:
        line_num += 1

        # ignore comments, which we assume are prefixed by either '#' or '%'
        line = re.split(r"[#%]", line, maxsplit=1)[0]

        # skip if the line is empty after stripping away optional comments
        if line == "":
            logger.debug(f"Skipping line #{line_num}: empty line.")
            continue

        # replace consecutive sequences of whitespace and commas with a single space
        line = re.sub(r"[\s,]+", " ", line)

        # considering space (' ') as the delimiter, take only the first 2 tokens
        # to ignore weights or other edge metadata
        nodes = tuple(map(str, line.split(maxsplit=2)[:2]))
        if len(nodes) < 2:
            logger.warning(f"Skipping line #{line_num}: less than 2 tokens.")
            continue

        g.add_edge(*nodes)

    return g


if __name__ == "__main__":
    main()
