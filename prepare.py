#!/usr/bin/env python3

import argparse
import os
import pathlib
import shutil
import typing

import networkx as nx

import graph_properties
import read_graph
import utils

__all__ = ["prepare"]

logger = utils.configure_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Process a Network Repository graph to make it ready for the experiments."
        )
    )
    _ = parser.add_argument(
        "graph_dir",
        nargs="?",
        help=(
            "Path to the unzipped directory containing the graph data files; if this "
            "argument is either not provided or provided as an empty string, the path "
            "will be read from stdin"
        ),
    )

    args = parser.parse_args()

    if not args.graph_dir:
        args.graph_dir = input()

    prepare(args.graph_dir)


def prepare(graph_dir: pathlib.Path | os.PathLike[typing.Any] | str):
    """Processes a Network Repository graph to make it ready for the experiments."""

    logger.info(f"Processing graph data in the directory '{graph_dir}'")

    if not os.fspath(graph_dir):
        raise ValueError("Path must not be empty")

    graph_dir = pathlib.Path(graph_dir)

    if not graph_dir.is_dir():
        raise ValueError(f"Not a directory: {graph_dir}")

    for path in graph_dir.iterdir():
        if path.is_file() and path.suffix in (".mtx", ".edges"):
            logger.debug(
                (
                    f"Taking graph data from the file '{path}' and ignoring other "
                    f"files in '{graph_dir}'"
                )
            )

            try:
                g = read_graph.from_file(path)

                logger.info("Removing self-loops if they exist.")
                g.remove_edges_from(nx.selfloop_edges(g))

                logger.info("Relabeling nodes.")
                g = nx.convert_node_labels_to_integers(g)

                logger.info("Computing graph properties.")
                props = graph_properties.compute(g)

                # delete everything in the directory
                logger.info(f"Deleting everything in '{graph_dir}'")
                for child in graph_dir.iterdir():
                    if child.is_dir():
                        shutil.rmtree(child)
                    else:
                        child.unlink()

                # write the graph's edge list representation and properties to the dir
                with open(graph_dir / "graph.edges", "wb") as f:
                    logger.info(f"Writing '{f.name}'")
                    nx.write_edgelist(g, f, data=False)
                with open(graph_dir / "properties.yaml", "w") as f:
                    logger.info(f"Writing '{f.name}'")
                    for key, val in props.items():
                        _ = f.write(f"{key}: {graph_properties.format_value(val)}\n")
                return

            except ValueError as e:
                raise ValueError(
                    f"Error reading and processing graph from file '{path}': {e}"
                ) from e
            except RuntimeError as e:
                raise RuntimeError(
                    f"Error reading and processing graph from file '{path}': {e}"
                ) from e
            except Exception as e:
                raise Exception(
                    f"Error reading and processing graph from file '{path}': {e}"
                ) from e

    raise ValueError(f"No graph data files found in '{graph_dir}'")


if __name__ == "__main__":
    main()
