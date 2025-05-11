import socketserver

from bitvoker.ai import AI
from bitvoker.config import Config
from bitvoker.handler import Handler
from bitvoker.notifier import Notifier
from bitvoker.logger import setup_logger

logger = setup_logger("server")


def main():
    config = Config()
    # Pass the list of channel configurations to the Notifier
    notifier = Notifier(config.notification_channels)
    ai = AI(config.preprompt)
    HOST, PORT = config.server_host, config.server_port
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((HOST, PORT), Handler) as server:
        server.ai = ai
        server.config_manager = config  # Store the manager to access full config easily
        server.notifier = notifier
        logger.info("Server listening on %s:%s ...", HOST if HOST else "all interfaces", PORT)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server shutting down due to KeyboardInterrupt...")
        except Exception as e:
            logger.exception(f"Error in server execution: {e}")
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
