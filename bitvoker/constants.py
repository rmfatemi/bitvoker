import os


WEB_SERVER_PORT = 8085
SECURE_TCP_SERVER_PORT = 8084
PLAIN_TCP_SERVER_PORT = 8083
SERVER_HOST = "0.0.0.0"  # listen on all interfaces

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CERT_PATH = os.path.join(DATA_DIR, "server.crt")
KEY_PATH = os.path.join(DATA_DIR, "server.key")

DB_FILENAME = os.path.join(DATA_DIR, "database.db")
