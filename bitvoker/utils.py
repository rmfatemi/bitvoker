import sys
import logging


def setup_logger(name=__name__, level=logging.DEBUG):
    formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger


def truncate(text, max_length=80, preserve_newlines=False, suffix="..."):
    if not preserve_newlines:
        text = text.replace("\n", " ").strip()

    if len(text) <= max_length:
        return text
    else:
        return text[: max_length - len(suffix)] + suffix
