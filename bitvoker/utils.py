import os

import bitvoker.constants as constants

from bitvoker.logger import setup_logger

logger = setup_logger("utils")


def truncate(text, max_length=80, preserve_newlines=False, suffix="..."):
    if not preserve_newlines:
        text = text.replace("\n", " ").strip()
    if len(text) <= max_length:
        return text
    else:
        return text[: max_length - len(suffix)] + suffix


def generate_ssl_cert():
    if os.path.exists(constants.CERT_PATH) and os.path.exists(constants.KEY_PATH):
        logger.info("using existing certificates")
        return

    logger.info("generating self-signed certificate ...")
    os.makedirs(constants.DATA_DIR, exist_ok=True)
    cmd = (
        f"openssl req -x509 -newkey rsa:4096 -keyout {constants.KEY_PATH} -out {constants.CERT_PATH} "
        f'-days 365 -nodes -subj "/CN=bitvoker" -addext "subjectAltName=DNS:{constants.SERVER_HOST}"'
    )
    result = os.system(cmd)
    if result != 0:
        logger.error("failed to generate self-signed certificate")
        raise RuntimeError("failed to generate self-signed certificate")
    logger.info(f"self-signed certificates created in {constants.DATA_DIR}")
