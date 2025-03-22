#!/usr/bin/env python3

import argparse
import logging
import os
import pathlib
import shutil
import typing

import networkx as nx

import analyze
import parse

__all__ = ["prepare"]

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        filename=os.environ.get("LOGFILE", None),
        level=os.environ.get("LOGLEVEL", "WARNING").upper(),
    )

    parser = argparse.ArgumentParser(
        description=(
            "Process a graph downloaded from Network Repository to make it ready for the "
            "experiments."
        )
    )
    _ = parser.add_argument(
        "graph_dir",
        type=str,
        help=(
            "Path to the unzipped directory containing the graph data files, or '-' to read the "
            "path from stdin"
        ),
    )

    args = parser.parse_args()

    if args.graph_dir == "-":
        args.graph_dir = input()

    prepare(args.graph_dir)


def prepare(graph_dir: pathlib.Path | os.PathLike[typing.Any] | str):
    """Processes a graph downloaded from Network Repository to make it ready for the experiments."""

    logger.info(f"Processing graph data in the directory '{graph_dir}'.")

    if not os.fspath(graph_dir):
        raise ValueError("Path must not be empty")

    graph_dir = pathlib.Path(graph_dir)

    if not graph_dir.is_dir():
        raise ValueError(f"Not a directory: {graph_dir}")

    for file in graph_dir.iterdir():
        if file.is_file() and file.suffix in (".mtx", ".edges"):
            logger.info(
                f"Taking graph data from file '{file}' and ignoring other files in '{graph_dir}'."
            )

            try:
                g = parse.parse_graph(file)

                logger.info("Removing self-loops if they exist.")
                g.remove_edges_from(nx.selfloop_edges(g))

                logger.info("Relabeling nodes.")
                g = nx.convert_node_labels_to_integers(g)

                logger.info("Computing graph properties.")
                props = analyze.graph_properties(g)

                # delete everything in the directory
                logger.info(f"Deleting everything in '{graph_dir}'.")
                for child in graph_dir.iterdir():
                    if child.is_dir():
                        shutil.rmtree(child)
                    else:
                        child.unlink()

                # write the graph's edge list representation and properties to the directory
                with open(graph_dir / "graph.edges", "wb") as f:
                    logger.info(f"Writing {graph_dir / 'graph.edges'}.")
                    nx.write_edgelist(g, f, data=False)
                with open(graph_dir / "properties.yaml", "w") as f:
                    logger.info(f"Writing {graph_dir / 'properties.yaml'}.")
                    for key, val in props.items():
                        _ = f.write("{}: {}\n".format(key, val))

                return
            except ValueError as e:
                raise ValueError(
                    f"Error reading and processing graph from file '{file}': {e}"
                ) from e
            except RuntimeError as e:
                raise RuntimeError(
                    f"Error reading and processing graph from file '{file}': {e}"
                ) from e
            except Exception as e:
                raise Exception(
                    f"Error reading and processing graph from file '{file}': {e}"
                ) from e

    raise ValueError(f"No graph data files found in '{graph_dir}'")


if __name__ == "__main__":
    main()
