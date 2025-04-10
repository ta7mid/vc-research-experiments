#!/usr/bin/env python3

import argparse

import download
import extract
import preprocess_graph
import utils

logger = utils.configure_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Download a graph from Network Repository and preprocess it to make it "
            "ready for the experiments."
        )
    )
    _ = parser.add_argument(
        "url",
        help="URL of the ZIP file containing the graph data",
    )

    args = parser.parse_args()

    logger.info(f"Downloading '{args.url}' ...")
    zip_path = download.download(args.url)

    logger.info(f"Extracting '{zip_path}' ...")
    extracted_dir = extract.unzip(zip_path)

    logger.info(f"Parsing and preparing the graph in '{extracted_dir}' ...")
    preprocess_graph.in_extracted_dir(extracted_dir)

    logger.info("Success!")


if __name__ == "__main__":
    main()
