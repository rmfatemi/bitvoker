import uvicorn
import threading
import socketserver

from bitvoker.ai import AI
from bitvoker.api import app
from bitvoker.config import Config
from bitvoker.handler import Handler
from bitvoker.notifier import Notifier
from bitvoker.utils import setup_logger
from bitvoker.constants import TCP_SERVER_PORT, UI_SERVER_PORT, SERVER_HOST

logger = setup_logger("server")


def run_tcp_server():
    config = Config()
    notifier = Notifier(config.notification_channels)
    ai = AI(config.preprompt) if config.config_data.get("enable_ai", False) else None
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((SERVER_HOST, TCP_SERVER_PORT), Handler) as server:
        # store tcp server instance for dynamic updates
        app.state.tcp_server = server
        server.ai = ai
        server.config_manager = config
        server.notifier = notifier
        logger.info("TCP Server listening on %s:%s ...", SERVER_HOST, TCP_SERVER_PORT)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("TCP Server shutting down due to KeyboardInterrupt.")
        except Exception as e:
            logger.exception("Error in TCP Server: %s", e)
        finally:
            server.server_close()


def start_web_server():
    logger.info(f"Starting web server at http://{SERVER_HOST}:{UI_SERVER_PORT} ...")
    uvicorn.run(app, host=SERVER_HOST, port=UI_SERVER_PORT)


def main():
    logger.info("Starting TCP server in a background thread ...")
    tcp_thread = threading.Thread(target=run_tcp_server, daemon=True)
    tcp_thread.start()
    logger.info("TCP server thread started.")

    logger.info("Starting the FastAPI web server now.")
    start_web_server()


if __name__ == "__main__":
    main()
