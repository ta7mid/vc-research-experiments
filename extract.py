#!/usr/bin/env python3

import argparse
import os
import pathlib
import typing
import zipfile

import utils

logger = utils.configure_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Unzip a file and print the path of the extracted directory"
    )
    _ = parser.add_argument(
        "zip_filepath",
        nargs="?",
        help=(
            "Path of the ZIP file; if this argument is either not provided or provided "
            "as an empty string, the path will be read from stdin"
        ),
    )
    _ = parser.add_argument(
        "-O",
        "--outdir",
        help=(
            "Parent of the directory into which the contents of the ZIP archive will "
            "be extracted (default: the 'data' directory in the script's directory); "
            "the extracted files will reside in a subdirectory of this directory named "
            "after the ZIP file (taking its prefix until the first dot)."
        ),
    )
    _ = parser.add_argument(
        "-n",
        "--noclobber",
        action="store_true",
        help=(
            "Do not overwrite an existing directory with the same path as the "
            "extraction destination if such a file already exists (default: do "
            "overwrite)"
        ),
    )
    _ = parser.add_argument(
        "-k",
        "--keep",
        action="store_true",
        help="Keep the ZIP file after extraction (default: delete it)",
    )

    args = parser.parse_args()

    if not args.zip_filepath:
        args.zip_filepath = input()

    path = unzip(
        args.zip_filepath,
        out_parent=args.outdir,
        no_clobber=args.noclobber,
        keep=args.keep,
    )

    print(path)


def unzip(
    zip_filepath: pathlib.Path | os.PathLike[typing.Any] | str,
    out_parent: pathlib.Path | os.PathLike[typing.Any] | str | None = None,
    no_clobber: bool = False,
    keep: bool = False,
) -> pathlib.Path:
    if out_parent is None:
        out_parent = pathlib.Path(__file__).parent / "data"
        logger.info(f"Using '{out_parent}' as the default extraction parent directory")
    elif not os.fspath(out_parent):
        raise ValueError(
            (
                "Cannot specify an empty string as out_parent; use '.' for the current "
                "directory or None to use the 'data' directory in this script's parent"
            )
        )
    else:
        out_parent = pathlib.Path(out_parent)

        if not out_parent.exists():
            out_parent.mkdir(parents=True)
            logger.debug(f"Created extraction parent directory '{out_parent}'")
        elif not out_parent.is_dir():
            raise ValueError(
                (
                    f"Specified extraction parent '{out_parent}' already exists but is "
                    "not a directory"
                )
            )

    zip_filepath = pathlib.Path(zip_filepath)

    # the prefix of zip_filepath.name until the first '.'
    filename_stem = zip_filepath.name.split(".", maxsplit=1)[0]

    exdir = out_parent / filename_stem
    logger.info(f"Extracting '{zip_filepath}' to '{exdir}'")

    if exdir.exists() and no_clobber:
        raise FileExistsError(
            f"Extraction destination '{exdir}' already exists, but "
            + ("the --noclobber flag" if __name__ == "__main__" else "no_clobber=True")
            + " was specified"
        )

    with zipfile.ZipFile(zip_filepath, mode="r") as zip_file:
        zip_file.extractall(path=exdir)

        if not keep:
            logger.info(f"Deleting '{zip_filepath}'")
            zip_filepath.unlink()

    return exdir


if __name__ == "__main__":
    main()
