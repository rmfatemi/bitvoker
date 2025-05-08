import sys
import logging

def setup_logger(name=__name__, level=logging.DEBUG):
    formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s][%(name)s] - %(message)s")

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger
