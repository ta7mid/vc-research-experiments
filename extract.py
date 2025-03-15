import argparse
import os.path
import sys
from os import PathLike
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Unzip a file")
    parser.add_argument(
        "zip_path",
        type=str,
        help="
    )
    parser.add_argument(
        "-o",
        type=str,
        default=None,
        help="
    )
    args = parser.parse_args()

    path, error = unzip(
        args.url,
        dest=args.c,
        filename=args.o,
        overwrite=args.f,
    )

    if error is not None:
        sys.exit(error)

    print(path)


def unzip(
    file: _PathLike,
    destdir: _PathLike = Path(RAW_DATA_ROOT) / "unzipped",
) -> tuple[Path | None, str | None]:
    destdir = Path(destdir) / Path(file).stem
    try:
        with ZipFile(file, mode="r") as zip_file:
            zip_file.extractall(path=destdir)
            return destdir, None
    except Exception as e:
        return None, f"Exception: `{e}`"


if __name__ == "__main__":
    main()
