#!/usr/bin/env python3

import argparse
import os
import os.path
import pathlib
import tempfile
import typing
from urllib import request

import utils

__all__ = ["download"]

logger = utils.configure_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Download a file from a URL and print the path of the downloaded file."
        )
    )
    _ = parser.add_argument(
        "url",
        nargs="?",
        help=(
            "URL of the file to download; if this argument is either not provided or "
            "provided as an empty string, the URL will be read from stdin"
        ),
    )
    _ = parser.add_argument(
        "-O",
        "--destdir",
        help=(
            "Destination directory to save the file (default: a randomly named "
            "temporary directory)"
        ),
    )
    _ = parser.add_argument(
        "-o",
        "--filename",
        help="Filename to save the file as (default: guessed from the URL)",
    )
    _ = parser.add_argument(
        "-n",
        "--noclobber",
        action="store_true",
        help=(
            "Do not overwrite an existing file with the same path as the download's "
            "destination path if such a file already exists (default: do overwrite)"
        ),
    )
    args = parser.parse_args()

    if not args.url:
        args.url = input()

    path = download(
        args.url,
        destdir=args.destdir,
        filename=args.filename,
        no_clobber=args.noclobber,
    )

    print(path)


def download(
    url: str,
    *,
    destdir: pathlib.Path | os.PathLike[typing.Any] | str | None = None,
    filename: str | None = None,
    no_clobber: bool = False,
) -> str:
    """Downloads a file from a URL.

    :param url: URL of the file to download
    :param destdir: Destination directory to save the file; if None, a temporary
        directory is used, otherwise it must not be an empty string or path
    :param filename: Filename to save the file as; if None, it is guessed from the URL,
        otherwise it must not contain path separators and must not be an empty string
    :param no_clobber: Do not overwrite an existing file with the same path as the
        download's destination path, if it exists
    :return: Path to the downloaded file
    """

    if destdir is None:
        destdir = pathlib.Path(tempfile.mkdtemp())
        logger.info(f"Using temporary directory '{destdir}' for download")
    elif not os.fspath(destdir):
        raise ValueError(
            (
                "Cannot specify an empty path or string for destdir; use '.' for the "
                "current directory or None to create and use a temporary directory"
            )
        )
    else:
        destdir = pathlib.Path(destdir)

        if not destdir.exists():
            destdir.mkdir(parents=True)
            logger.debug(f"Created download destination directory '{destdir}'")
        elif not destdir.is_dir():
            raise ValueError(
                (
                    f"Download destination '{destdir}' already exists but is not a "
                    "directory"
                )
            )

    if filename is None:
        filename = url.split("/")[-1]
        logger.info(f"Guessed the filename to be '{filename}'")
    elif not os.fspath(filename):
        raise ValueError(
            "Filename must not be an empty string; use None to guess from the URL"
        )
    elif os.path.sep in str(filename):
        raise ValueError(
            f"Filename cannot contain path separators: '{filename}' specified"
        )

    destpath = destdir / filename
    logger.info(f"Downloading from '{url}' to '{destpath}'")

    if destpath.exists():
        arg = (
            "the -noclobber flag"
            if __name__ == "__main__"
            else "the argument no_clobber=True"
        )

        if no_clobber:
            raise FileExistsError(
                f"Destination file '{destpath}' already exists, but {arg} was specified"
            )

        logger.warning(
            (
                f"Destination file '{destpath}' already exists; overwriting as {arg} "
                "was NOT specified."
            )
        )

    path, headers = request.urlretrieve(url, filename=destpath)
    logger.debug(f"Downloaded to '{path}' with headers: {headers}")

    return path


if __name__ == "__main__":
    main()
