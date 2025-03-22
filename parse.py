#!/usr/bin/env python3

import argparse
import io
import logging
import os
import pathlib
import re
import types
import typing

import networkx as nx
import scipy

__all__ = ["parse_graph", "parse_as_mtx", "parse_as_edge_list"]

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

    g = parse_graph(args.graph_filepath, args.format)

    if args.relabel:
        logger.debug("Relabeling nodes.")
        g = nx.convert_node_labels_to_integers(g)

    logger.debug("Printing the edge list representation of the graph.")
    for line in nx.generate_edgelist(g, data=False):
        print(line)


def parse_graph(
    filepath: pathlib.Path | os.PathLike[typing.Any] | str,
    format: typing.Literal["mtx", "edges"] | str | types.NoneType = None,
) -> nx.Graph:
    """Reads a graph from a file in one of the supported formats."""

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
                g = parse_as_mtx(filepath)
            except ValueError as error:
                logger.warning(f"Failed to read graph as Matrix Market file: {error}")
                logger.info("Trying to read as an edge list file.")

                try:
                    g = parse_as_edge_list(filepath)
                except ValueError as e:
                    raise ValueError("Could not read graph as edge list either.") from e

        case "edges":
            logger.info("Reading as an edge list file.")
            try:
                g = parse_as_edge_list(filepath)
            except ValueError as error:
                logger.warning(f"Failed to read graph as edge list: {error}")
                logger.info("Trying to read as a Matrix Market file.")

                try:
                    g = parse_as_mtx(filepath)
                except ValueError as e:
                    raise ValueError(
                        "Could not read as Matrix Market file either."
                    ) from e

        case _:
            raise ValueError(f"Unrecognized format: {format}")

    return g


def parse_as_mtx(filepath: pathlib.Path) -> nx.Graph:
    """Reads a graph from a file in the Matrix Market format.

    Relevant: https://networkx.org/documentation/stable/reference/readwrite/matrix_market.html
    """

    text = filepath.read_text()

    for field in ("real", "double", "complex", "integer"):
        if field in text:
            logger.debug(f"Replacing '{field}' with 'pattern' in the file.")
            text = text.replace(field, "pattern")

    try:
        logger.debug(
            "Reading an adjacency matrix from the Matrix Market data using `scipy.io.mmread`."
        )
        adjmat = scipy.io.mmread(io.StringIO(text), spmatrix=False)
    except Exception as ex:
        raise ValueError(
            f"Error reading or parsing as Matrix Market file: {ex}"
        ) from ex

    try:
        logger.debug(
            (
                "Trying to create an nx.Graph from the adjacency matrix using "
                "`nx.convert_matrix.from_scipy_sparse_array`."
            )
        )
        g = nx.convert_matrix.from_scipy_sparse_array(
            adjmat, create_using=nx.Graph[int]
        )

        logger.info(
            "Successfully read as Matrix Market and created an nx.Graph from the adjacency matrix."
        )
        return g
    except Exception as ex:
        logger.warning(
            (
                "Failed to create an nx.Graph assuming the adjacency matrix is a SciPy sparse "
                f'array; exception raised: "{ex}".'
            )
        )

        try:
            logger.debug(
                (
                    "Trying to create an nx.Graph assuming the adjacency matrix is a square NumPy "
                    "array, using `nx.convert_matrix.from_numpy_array`."
                )
            )
            g = nx.convert_matrix.from_numpy_array(adjmat, create_using=nx.Graph[int])

            logger.info(
                (
                    "Successfully read as Matrix Market and created an nx.Graph from the adjacency "
                    "matrix."
                )
            )
            return g
        except Exception as ex:
            raise ValueError(f"Error creating nx.Graph from NumPy array: {ex}") from ex


def parse_as_edge_list(filepath: pathlib.Path) -> nx.Graph:
    r"""Reads a graph from a file in the edge list format.

    This implementation is adapted from :py:func:`nx.parse_edgelist` [1]_ to allow multiple
    simultaneous delimiters (``\s`` and ``,``) and multiple simultaneous comment prefixes (``#``
    and ``%``) using regex.

    .. [1] https://networkx.org/documentation/stable/_modules/networkx/readwrite/edgelist.html#parse_edgelist
    """

    g = nx.Graph()

    with open(filepath) as file:
        for line in file.readlines():
            # ignore comments, which we assume are prefixed by either '#' or '%'
            line = re.split(r"[#%]", line, maxsplit=1)[0]

            # skip if the line is empty after stripping away optional comments
            if line == "":
                logger.debug("Skipping empty line.")
                continue

            # consider both whitespace characters and commas as delimiters and
            # replace consecutive sequences of delimiters with a single space
            line = re.sub(r"[\s,]+", " ", line)

            # considering space as the delimiter, take only the first 2 tokens
            # to ignore weights or other edge metadata
            nodes = tuple(map(str, line.split(maxsplit=2)[:2]))
            if len(nodes) < 2:
                logger.debug("Skipping line with less than 2 nodes.")
                continue

            g.add_edge(*nodes)

    logger.info("Successfully read as an edge list file and created an nx.Graph.")
    return g


if __name__ == "__main__":
    main()
