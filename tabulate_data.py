#!/usr/bin/env python3

import argparse
import pathlib

import tabulate
import yaml

__all__ = ["collect_data"]


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

    args = parser.parse_args()

    data = collect_data()

    table_str = tabulate.tabulate(data, headers=data.keys(), tablefmt=args.format)
    print(table_str)


def collect_data() -> dict[str, list[str] | list[int] | list[float] | list[bool]]:
    data: dict[str, list[str] | list[int] | list[float] | list[bool]] = {
        "name": [],
        "order": [],
        "size": [],
        "max_degree": [],
        "avg_degree": [],
        "density": [],
        "connected": [],
    }

    for path in pathlib.Path("data/").glob("*/properties.yaml"):
        data["name"].append(path.parent.name)
        with open(path) as f:
            for k, v in yaml.load(f, yaml.SafeLoader).items():
                data[k].append(v)

    return data


if __name__ == "__main__":
    main()
