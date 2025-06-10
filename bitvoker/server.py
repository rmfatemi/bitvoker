import ssl
import asyncio
import uvicorn
import threading
import socketserver

import bitvoker.constants as constants

from bitvoker.api import app
from bitvoker.handler import Handler
from bitvoker.logger import setup_logger
from bitvoker.utils import generate_ssl_cert
from bitvoker.refresher import refresh_components


logger = setup_logger(__name__)


def run_plain_tcp_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((constants.SERVER_HOST, constants.PLAIN_TCP_SERVER_PORT), Handler) as server:
        server.app = app
        app.state.plain_tcp_server = server
        logger.info(
            f"plain tcp server listening on {constants.SERVER_HOST}:{constants.PLAIN_TCP_SERVER_PORT} ... e.g., echo"
            f' "message" | nc {constants.SERVER_HOST} {constants.PLAIN_TCP_SERVER_PORT}'
        )
        server.serve_forever()


def run_secure_tcp_server():
    socketserver.TCPServer.allow_reuse_address = True
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=constants.CERT_PATH, keyfile=constants.KEY_PATH)
    with socketserver.ThreadingTCPServer((constants.SERVER_HOST, constants.SECURE_TCP_SERVER_PORT), Handler) as server:
        server.app = app
        app.state.secure_tcp_server = server
        server.socket = ssl_context.wrap_socket(server.socket, server_side=True)
        logger.info(
            f"secure tcp server listening on {constants.SERVER_HOST}:{constants.SECURE_TCP_SERVER_PORT} ... e.g., echo"
            f" 'message' | openssl s_client -connect {constants.SERVER_HOST}:{constants.SECURE_TCP_SERVER_PORT}"
        )
        server.serve_forever()


async def start_http_server():
    config = uvicorn.Config(app, host=constants.SERVER_HOST, port=constants.HTTP_WEB_SERVER_PORT, log_level="info")
    server = uvicorn.Server(config)
    logger.info(f"http webui listening on http://{constants.SERVER_HOST}:{constants.HTTP_WEB_SERVER_PORT}")
    await server.serve()


async def start_https_server():
    config = uvicorn.Config(
        app,
        host=constants.SERVER_HOST,
        port=constants.HTTPS_WEB_SERVER_PORT,
        ssl_keyfile=str(constants.KEY_PATH),
        ssl_certfile=str(constants.CERT_PATH),
        log_level="info",
    )
    server = uvicorn.Server(config)
    logger.info(f"https webui listening on https://{constants.SERVER_HOST}:{constants.HTTPS_WEB_SERVER_PORT}")
    await server.serve()


async def async_main():
    generate_ssl_cert()

    logger.info("starting tcp servers in background threads...")
    threading.Thread(target=run_plain_tcp_server, daemon=True).start()
    threading.Thread(target=run_secure_tcp_server, daemon=True).start()

    await asyncio.sleep(1)
    refresh_components(app)

    logger.info("starting web servers...")
    await asyncio.gather(
        start_http_server(),
        start_https_server(),
    )


def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("application shutting down.")


if __name__ == "__main__":
    main()
