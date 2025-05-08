import socketserver

from ai import AI
from config import Config
from handler import Handler
from telegram import Telegram
from bitvoker.logger import setup_logger

logger = setup_logger("server")

def main():
    config = Config()
    telegram = Telegram(config.bot_token, config.chat_id)
    ai = AI(config.preprompt)
    HOST, PORT = config.server_host, config.server_port
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((HOST, PORT), Handler) as server:
        server.ai = ai
        server.config = config
        server.telegram = telegram
        logger.info("Server listening on %s:%s ...", HOST if HOST else "all interfaces", PORT)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server shutting down due to KeyboardInterrupt...")
        except Exception as e:
            logger.exception("Error in server execution")
        finally:
            server.server_close()

if __name__ == "__main__":
    main()
