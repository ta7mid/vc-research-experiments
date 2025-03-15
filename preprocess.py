#!/usr/bin/env python3


import io
import pathlib
import sys

import networkx as nx
import scipy


def print_stderr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main():
    assert len(sys.argv) == 2, "USAGE: python3 preprocess.py directory"

    dir = pathlib.Path(sys.argv[1])
    assert dir.exists(), f"directory not found: {dir}"

    for file in dir.iterdir():
        if file.is_file() and file.suffix in ("mtx", "edges"):
            process(file)
            break


def process(graph_filepath: pathlib.Path) -> nx.Graph | None:
    g = read_graph(graph_filepath)
    if g is None:
        sys.exit(1)

    dir = graph_filepath.parent

    # delete everything in the directory
    for file in graph_filepath.parent:
        file.unlink()

    with open(dir / "info.txt", "w") as f:
        print_stderr(f"Writing {dir / 'info.txt'}...")
        max_deg, avg_deg = max_and_avg_degrees(g)
        density = graph_density(g)
        f.write(
            f"nodes: {g.order()}\n"
            f"edges: {g.size()}\n"
            f"max_degree: {max_deg}\n"
            f"avg_degree: {avg_deg}\n"
            f"density: {density}\n"
            f"is_connected: {1 if nx.is_connected(g) else 0}\n"
        )

    if graph_filepath.suffix == ".txt":
        return

    g = relabel(g)

    with open(dir / "graph.txt", "w") as f:
        print_stderr(f"Writing {dir / 'graph.txt'}...")
        text = nx_graph_to_text(g)
        f.write(text)

    return g


def read_graph(graph_filepath: pathlib.Path) -> nx.Graph | None:
    print_stderr(f"Reading {graph_filepath}...")
    g = None

    if graph_filepath.suffix == ".txt":
        with open(graph_filepath) as f:
            g = nx.Graph()
            for line in f.readlines()[2:]:
                if line == "":
                    continue
                u, v = map(int, line.strip().split())
                g.add_edge(u, v)

    elif graph_filepath.suffix == ".mtx":
        text = graph_filepath.read_text()
        for field in ("real", "double", "complex", "integer"):
            if field in text:
                text = text.replace(field, "pattern")
                break

        try:
            matrix = scipy.io.mmread(io.StringIO(text))
        except Exception as err:
            print_stderr(
                "\tskipped due to following error while reading/parsing Matrix Market file: `{}`".format(
                    err
                )
            )

        try:
            g = nx.from_scipy_sparse_array(matrix)
        except Exception as err:
            print_stderr(
                "\tfailed to read as sparse matrix (exception: `{}`), trying square matrix...".format(
                    err
                )
            )
            try:
                g = nx.from_numpy_array(matrix)
            except Exception as err:
                print_stderr(
                    "\t\tfailed to read as square matrix (exception: `{}`); skipping".format(
                        err
                    )
                )

    elif graph_filepath.suffix == ".edges":
        try:
            g = nx.Graph()
            for line in open(graph_filepath).read().split("\n"):
                line = line.split("%", maxsplit=1)[0]
                if line == "":
                    continue
                line = line.replace(",", " ")
                nodes = tuple(map(int, line.split()[:2]))
                if len(nodes) < 2:
                    continue
                g.add_edge(*nodes)
        except Exception as err:
            print_stderr(f"\tskipped because of error: {err}")

    else:
        print_stderr("\tskipped because file extension not recognized")

    return g


def relabel(g: nx.Graph) -> nx.Graph:
    print_stderr("Relabeling nodes...")
    mapping = {}
    v = 0
    for node in g.nodes:
        mapping[node] = v
        v += 1
    return nx.relabel_nodes(g, mapping, copy=True)


def nx_graph_to_text(g: nx.Graph) -> str:
    return f"{g.order()}\n{g.size()}\n" + "\n".join(f"{e[0]} {e[1]}" for e in g.edges())


def max_and_avg_degrees(g: nx.Graph) -> tuple[int, float]:
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
