import logging
import os


def configure_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        filename=os.environ.get("LOGFILE", None),
        level=os.environ.get("LOGLEVEL", "WARNING").upper(),
    )

    return logging.getLogger(name)
