#!/usr/bin/env python3

import argparse
from collections import abc
import logging
import os
import pathlib
import re
import types
import typing

import networkx as nx
import scipy.io

__all__ = ["from_file", "from_mtx_file", "from_edge_list_file"]

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        filename=os.environ.get("LOGFILE", None),
        level=os.environ.get("LOGLEVEL", "WARNING").upper(),
    )

    parser = argparse.ArgumentParser(
        description=(
            "Parse a graph from a text file in one of the supported formats and print an edge-"
            "list representation of it."
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
    _ = parser.add_argument(
        "-relabel",
        action="store_true",
        help="Relabel the vertices of output graph using integers starting from 0",
    )

    args = parser.parse_args()

    if args.graph_filepath == "-":
        args.graph_filepath = input()

    g = from_file(args.graph_filepath, args.format)

    if args.relabel:
        logger.debug("Relabeling nodes.")
        g = nx.convert_node_labels_to_integers(g)

    logger.debug("Printing the edge list representation of the graph.")
    for line in nx.generate_edgelist(g, data=False):
        print(line)


def from_file(
    filepath: pathlib.Path | os.PathLike[typing.Any] | str,
    format: typing.Literal["mtx", "edges"] | str | types.NoneType = None,
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
            try:
                g = from_mtx_file(filepath)
            except ValueError as error:
                logger.warning(f"Failed to read graph as Matrix Market file: {error}")
                logger.info("Trying to read as an edge list file instead.")

                try:
                    g = from_edge_list_file(filepath)
                except ValueError as e:
                    raise ValueError("Could not read graph as edge list either.") from e

        case "edges":
            logger.info("Reading as an edge list file.")
            return from_edge_list_file(filepath)

        case _:
            raise ValueError(f"Unrecognized format: {format}")

    return g


def from_mtx_file(filepath: pathlib.Path) -> nx.Graph:
    r"""Reads an adjacency matrix from a file in the Matrix Market format [1]_ and constructs an
    :py:class:`nx.Graph` from it, following [2]_.

    .. rubric:: References

    .. [1] https://math.nist.gov/MatrixMarket/formats.html#MMformat
    .. [2] https://networkx.org/documentation/stable/reference/readwrite/matrix_market.html
    """

    logger.debug("Reading an adjacency matrix from the Matrix Market data.")
    adjmat = scipy.io.mmread(filepath)

    if scipy.io.mminfo(filepath)[3] == "array":
        logger.debug("Constructing nx.Graph from the dense adjacency matrix.")
        g = nx.convert_matrix.from_numpy_array(adjmat)
    else:
        logger.debug(
            "Constructing nx.Graph from the sparse adjacency matrix given as a coordinate list."
        )
        g = nx.convert_matrix.from_scipy_sparse_array(adjmat)

    logger.info("Successfully parsed Matrix Market data and created an nx.Graph!")
    return g


def from_edge_list_file(filepath: pathlib.Path) -> nx.Graph:
    r"""Reads a graph represented as a list of edges, one per line, from a file."""

    with open(filepath) as file:
        g = parse_edge_list(file.readlines())

    logger.info("Successfully read as an edge list file and created an nx.Graph!")
    return g


def parse_edge_list(lines: abc.Iterable[str]) -> nx.Graph:
    r""""Parses a graph represented as a list of edges, one per line.

    This implementation is generalized from :py:func:`nx.convert_matrix.parse_edgelist` [1]_ to
    allow both whitespace characters (``\s`` in regex) and comma (``,``) to be used as delimiters
    (to separate the nodes of an edge on each line) simultaneously and to allow both ``#`` and
    ``%`` to be used as comment prefixes simultaneously.

    .. rubric:: References

    .. [1] https://networkx.org/documentation/stable/_modules/networkx/readwrite/edgelist.html#parse_edgelist
    """

    g = nx.Graph()

    for line in lines:
        # ignore comments, which we assume are prefixed by either '#' or '%'
        line = re.split(r"[#%]", line, maxsplit=1)[0]

        # skip if the line is empty after stripping away optional comments
        if line == "":
            logger.debug("Skipping empty line.")
            continue

        # replace consecutive sequences of whitespace and commas with a single space
        line = re.sub(r"[\s,]+", " ", line)

        # considering space (' ') as the delimiter, take only the first 2 tokens
        # to ignore weights or other edge metadata
        nodes = tuple(map(str, line.split(maxsplit=2)[:2]))
        if len(nodes) < 2:
            logger.debug("Skipping line with less than 2 nodes.")
            continue

        g.add_edge(*nodes)

    return g


if __name__ == "__main__":
    main()
