import os
import time
import hmac
import hashlib
import secrets

from bitvoker.logger import setup_logger


logger = setup_logger(__name__)

TOKEN_EXPIRY = 86400
_secret_key = secrets.token_hex(32)


def get_credentials():
    username = os.environ.get("BITVOKER_USERNAME", "")
    password = os.environ.get("BITVOKER_PASSWORD", "")
    return username, password


def is_auth_enabled():
    username, password = get_credentials()
    return bool(username and password)


def verify_credentials(username, password):
    expected_user, expected_pass = get_credentials()
    if not expected_user or not expected_pass:
        return False
    return hmac.compare_digest(username, expected_user) and hmac.compare_digest(password, expected_pass)


def create_token(username):
    timestamp = str(int(time.time()))
    payload = f"{username}:{timestamp}"
    signature = hmac.new(_secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"


def verify_token(token):
    if not token:
        return False
    parts = token.split(":")
    if len(parts) != 3:
        return False
    username, timestamp, signature = parts
    try:
        token_time = int(timestamp)
    except ValueError:
        return False
    if time.time() - token_time > TOKEN_EXPIRY:
        return False
    expected = hmac.new(_secret_key.encode(), f"{username}:{timestamp}".encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)
