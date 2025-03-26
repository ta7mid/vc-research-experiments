#!/usr/bin/env python3

import argparse
import logging
import os
import pathlib
import types
import typing
import zipfile

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        filename=os.environ.get("LOGFILE", None),
        level=os.environ.get("LOGLEVEL", "WARNING").upper(),
    )

    parser = argparse.ArgumentParser(
        description="Unzip a file and print the path of the extracted directory"
    )
    _ = parser.add_argument(
        "zip_filepath",
        type=str,
        help="Path of the ZIP file, or '-' to read the path from stdin",
    )
    _ = parser.add_argument(
        "-dir",
        type=str,
        default=None,
        help=(
            "Parent of the directory into which the contents of the ZIP archive will be extracted "
            "(default: 'data/' in the script's directory).  The extracted contents will reside in "
            "a subdirectory of this directory named after the ZIP file (taking its prefix until "
            "the first '.')."
        ),
    )
    _ = parser.add_argument(
        "-noclobber",
        action="store_true",
        help=(
            "Do not overwrite an existing directory with the same path as the extraction "
            "destination, if it exists"
        ),
    )
    _ = parser.add_argument(
        "-rm",
        action="store_true",
        help="Remove (delete) the ZIP file after extraction",
    )

    args = parser.parse_args()

    if args.zip_filepath == "-":
        args.zip_filepath = input()

    path = unzip(
        args.zip_filepath,
        out_parent=args.dir,
        no_clobber=args.noclobber,
        delete_zip=args.rm,
    )

    print(path)


def unzip(
    zip_filepath: pathlib.Path | os.PathLike[typing.Any] | str,
    out_parent: pathlib.Path | os.PathLike[typing.Any] | str | types.NoneType = None,
    no_clobber: bool = False,
    delete_zip: bool = True,
) -> pathlib.Path:
    if out_parent is None:
        out_parent = pathlib.Path(__file__).parent / "data"
        logger.info(f"Using '{out_parent}' as the default extraction parent directory")
    elif not os.fspath(out_parent):
        raise ValueError(
            (
                "Cannot specify an empty path or string for dir; use '.' for the current directory "
                "or None to use the 'data' directory in the script's directory"
            )
        )
    else:
        out_parent = pathlib.Path(out_parent)

        if not out_parent.exists():
            out_parent.mkdir(parents=True)
            logger.debug(f"Created extraction parent directory '{out_parent}'")
        elif not out_parent.is_dir():
            raise ValueError(
                f"Specified extraction parent '{out_parent}' already exists but is not a directory",
            )

    zip_filepath = pathlib.Path(zip_filepath)

    # the prefix of zip_filepath.name until the first '.'
    filename = zip_filepath.name.split(".", maxsplit=1)[0]

    exdir = out_parent / filename
    logger.info(f"Extracting '{zip_filepath}' to '{exdir}'")

    if exdir.exists() and no_clobber:
        raise FileExistsError(
            f"Extraction destination '{exdir}' already exists, but "
            + ("the -noclobber flag" if __name__ == "__main__" else "no_clobber=True")
            + " was specified"
        )

    with zipfile.ZipFile(zip_filepath, mode="r") as zip_file:
        zip_file.extractall(path=exdir)

        if delete_zip:
            logger.info(f"Deleting '{zip_filepath}'")
            zip_filepath.unlink()

    return exdir


if __name__ == "__main__":
    main()
