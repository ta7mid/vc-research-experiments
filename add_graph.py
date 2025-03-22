#!/usr/bin/env python3

import argparse
import logging
import os

import download
import extract
import prepare

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        filename=os.environ.get("LOGFILE", None),
        level=os.environ.get("LOGLEVEL", "WARNING").upper(),
    )

    parser = argparse.ArgumentParser(
        description=(
            "Download a graph from Network Repository and preprocess it to make it ready for the "
            "experiments."
        )
    )
    _ = parser.add_argument(
        "url",
        type=str,
        help="URL of the ZIP file containing the graph data",
    )

    args = parser.parse_args()

    print(f"Downloading '{args.url}' ...")
    zip_path = download.download(args.url)

    print(f"Extracting '{zip_path}' ...")
    extracted_dir = extract.unzip(zip_path)

    print(f"Parsing and preparing the graph in '{extracted_dir}' ...")
    prepare.prepare(extracted_dir)

    print("Success!")


if __name__ == "__main__":
    main()
