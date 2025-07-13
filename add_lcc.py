#!/usr/bin/env python3

import argparse
import os
import pathlib
import typing

import networkx as nx
import yaml

import graph_properties

__all__ = ["for_graph", "for_graphs_in_root"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Add the largest connected component (LCC) of a graph (or all graphs) to "
            "the dataset."
        )
    )
    _ = parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Process all graph data points that are subdirectories of the given path",
    )
    _ = parser.add_argument(
        "path",
        nargs="?",
        help=(
            "Directory for the graph or the parent directory for all graphs if `--all` "
            "is specified; if the graphs are already connected, the operation will be "
            "skipped sliently; if this argument is either not provided or provided as "
            "an empty string, the path will be read from stdin"
        ),
    )

    args = parser.parse_args()

    if not args.path:
        args.path = input()

    if args.all:
        for_graphs_in_root(args.path)
    else:
        for_graph(args.path)


def for_graphs_in_root(
    rootdir: pathlib.Path | os.PathLike[typing.Any] | str = "./data/graphs/",
) -> None:
    if not os.fspath(rootdir):
        raise ValueError("Cannot specify an empty path or string for path")
    else:
        rootdir = pathlib.Path(rootdir)

    for dir in rootdir.iterdir():
        if not dir.is_dir:
            continue

        for_graph(dir)


def for_graph(dir: pathlib.Path | os.PathLike[typing.Any] | str) -> None:
    if not os.fspath(dir):
        raise ValueError("Cannot specify an empty path or string for dir")
    else:
        dir = pathlib.Path(dir)

    print(f"{dir} => ", end="")

    with open(dir / "properties.yaml") as f:
        props = yaml.load(f, yaml.SafeLoader)
        if props["connected"]:
            print("skipped")
            return

    # check if the LCC graph already exists
    lcc_dir = dir.parent / f"{dir.name}_lcc"
    if lcc_dir.exists():
        print("skipped")
        return

    # read
    g_path = dir / "graph.edges"
    g: nx.Graph[int] = nx.read_edgelist(g_path, nodetype=int)

    # get LCC and node mapping
    lcc_nodes = max(nx.connected_components(g), key=len)
    lcc_nodes = sorted(lcc_nodes)
    lcc = g.subgraph(lcc_nodes)
    mapping = dict(zip(lcc_nodes, range(len(lcc_nodes)), strict=False))
    lcc = nx.relabel_nodes(lcc, mapping)

    # write
    lcc_dir.mkdir()
    with open(lcc_dir / "graph.edges", "wb") as f:
        nx.write_edgelist(lcc, f, data=False)
    with open(lcc_dir / "properties.yaml", "w") as f:
        for key, val in graph_properties.compute(lcc).items():
            _ = f.write(f"{key}: {graph_properties.format_value(val)}\n")
    with open(lcc_dir / "node_mapping.txt", "w") as f:
        for orig, new in mapping.items():
            _ = f.write(f"{new} {orig}\n")

    print(lcc_dir)


if __name__ == "__main__":
    main()
