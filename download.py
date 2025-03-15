import argparse
import os.path
import sys
from os import PathLike
from pathlib import Path
import tempfile
from urllib import request


def main():
    parser = argparse.ArgumentParser(description="Download a file from a URL")
    parser.add_argument("url", type=str, help="URL of the file to download")
    parser.add_argument(
        "-c",
        type=str,
        default=None,
        help="Destination directory to save the file (default: temporary directory); must not be used with -o",
    )
    parser.add_argument(
        "-o",
        type=str,
        default=None,
        help="Filename to save the file as (default: guessed from the URL); must not be used with -c",
    )
    parser.add_argument(
        "-f",
        action="store_false",
        help="Force overwrite existing file if exists",
    )
    args = parser.parse_args()

    path, error = download(
        args.url,
        dest=args.c,
        filename=args.o,
        overwrite=args.f,
    )

    if error is not None:
        sys.exit(error)

    print(path)


def download(
    url: str,
    *,
    dest: str | PathLike | None = None,
    filename: str | PathLike | None = None,
    overwrite: bool = False,
) -> tuple[str | None, str | None]:
    """
    Download a file from a URL.
    :param url: URL of the file to download
    :param dest: Destination directory to save the file
    :param filename: Filename to save the file as
    :param overwrite: Overwrite existing file if exists
    :return:
    """
    if dest is not None and filename is not None:
        return None, "Cannot specify both dest and filename"

    if dest is not None:
        dest = Path(dest)
        if not dest.exists():
            dest.mkdir(parents=True)
        elif not dest.is_dir():
            return (
                None,
                f'Download destination "{dest}" already exists and is not a directory',
            )

        filename = url.split("/")[-1]

    elif filename is not None:
        if os.path.sep in str(filename):
            return None, f"Filename cannot contain path separators: {filename}"

        dest = Path(tempfile.gettempdir())

    else:
        filename = url.split("/")[-1]
        dest = Path(tempfile.gettempdir())

    dest = dest / filename
    if dest.exists() and not overwrite:
        return None, f"File {dest} already exists"

    path, _ = request.urlretrieve(url, dest)
    return path, None


if __name__ == "__main__":
    main()
