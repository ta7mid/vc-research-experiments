#!/usr/bin/env python3

import argparse
import os
import pathlib
import typing

import tabulate
import yaml

__all__ = ["collect_results"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Tabulate the properties of all processed graphs in the data directory."
        )
    )
    _ = parser.add_argument(
        "-f",
        "--format",
        choices=(
            "plain",
            "simple",
            "grid",
            "pipe",
            "orgtbl",
            "rst",
            "mediawiki",
            "latex",
            "latex_raw",
            "latex_booktabs",
            "latex_longtable",
            "tsv",
        ),
        default="simple",
        help=(
            "Name of the format of the output table as used by the python-tabulate "
            "package (default: simple)."
        ),
    )
    _ = parser.add_argument(
        "-d",
        "--data_dir",
        nargs="?",
        help=(
            "Directory containing results for one experiment; each subdirectory of "
            "directory is expected to correspond to a single graph"
        ),
    )
    _ = parser.add_argument(
        "-r",
        "--results_dir",
        nargs="?",
        help=(
            "Directory containing results for one experiment; each subdirectory of "
            "directory is expected to correspond to a single graph"
        ),
    )

    args = parser.parse_args()

    data = collect_results(args.data_dir, args.results_dir)

    table_str = tabulate.tabulate(data, headers=data.keys(), tablefmt=args.format)
    print(table_str)


def collect_results(
    data_dir: pathlib.Path | os.PathLike[typing.Any] | str,
    results_dir: pathlib.Path | os.PathLike[typing.Any] | str,
) -> dict[str, list[str] | list[int] | list[float]]:
    if not os.fspath(data_dir):
        raise ValueError("Cannot specify an empty path or string for data_dir")
    else:
        data_dir = pathlib.Path(data_dir)

    if not os.fspath(results_dir):
        raise ValueError("Cannot specify an empty path or string for results_dir")
    else:
        results_dir = pathlib.Path(results_dir)

    data: dict[str, list[str] | list[int] | list[float]] = {
        "name": [],
        "order": [],
        "size": [],
        "max_degree": [],
        "avg_degree": [],
        "density": [],
        "cvc_size": [],
        "vc_size": [],
        "local_ratio_vc_size": [],
    }

    for path in results_dir.iterdir():
        assert path.is_dir(), f"Expected {path} to be a directory"
        name = path.name
        data["name"].append(name)

        with open(data_dir / name / "properties.yaml") as f:
            for k, v in yaml.load(f, yaml.SafeLoader).items():
                if k not in data:
                    continue
                data[k].append(v)

        for algo in ("cvc", "vc", "local_ratio_vc"):
            with open(path / f"{algo}_cardinality.txt") as f:
                data[f"{algo}_size"].append(int(f.read().strip()))

    return data


if __name__ == "__main__":
    main()
