from pathlib import Path


SERVER_HOST = "0.0.0.0"  # listen on all interfaces

HTTP_WEB_SERVER_PORT = 8086
HTTPS_WEB_SERVER_PORT = 8085
SECURE_TCP_SERVER_PORT = 8084
PLAIN_TCP_SERVER_PORT = 8083

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
KEY_PATH = DATA_DIR / "server.key"
CERT_PATH = DATA_DIR / "server.crt"
DB_FILENAME = DATA_DIR / "database.db"
CONFIG_FILENAME = DATA_DIR / "config.yaml"

REACT_BUILD_DIR = PROJECT_ROOT / "web" / "build"

MAX_META_PROMPT_LENGTH = 20000
