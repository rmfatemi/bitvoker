import ssl
import uvicorn
import threading
import socketserver

import bitvoker.constants as constants

from bitvoker.api import app
from bitvoker.handler import Handler
from bitvoker.logger import setup_logger
from bitvoker.utils import generate_ssl_cert
from bitvoker.components import refresh_server_components


logger = setup_logger("server")


def run_secure_tcp_server():
    socketserver.TCPServer.allow_reuse_address = True

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=constants.CERT_PATH, keyfile=constants.KEY_PATH)

    with socketserver.ThreadingTCPServer((constants.SERVER_HOST, constants.SECURE_TCP_SERVER_PORT), Handler) as server:
        server = refresh_server_components(server, force_new_config=True)
        # store the secure tcp server instance in app.state for dynamic updates
        app.state.secure_tcp_server = server
        server.socket = ssl_context.wrap_socket(server.socket, server_side=True)
        logger.info(f"Secure TCP Server (TLS) listening on <HOST IP>:{constants.SECURE_TCP_SERVER_PORT} ...")
        try:
            server.serve_forever()
        except Exception as e:
            logger.exception("Error in Secure TCP Server: %s", e)
        finally:
            server.server_close()


def run_plain_tcp_server():
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.ThreadingTCPServer((constants.SERVER_HOST, constants.PLAIN_TCP_SERVER_PORT), Handler) as server:
        server = refresh_server_components(server, force_new_config=True)
        # store the plain tcp server instance in app.state for dynamic updates
        app.state.plain_tcp_server = server
        logger.info(f"Plain TCP Server listening on <HOST IP>:{constants.PLAIN_TCP_SERVER_PORT} ...")
        try:
            server.serve_forever()
        except Exception as e:
            logger.exception("Error in Plain TCP Server: %s", e)
        finally:
            server.server_close()


def start_web_server():
    logger.info(f"Starting web server at https://<HOST IP>:{constants.WEB_SERVER_PORT} ...")
    uvicorn.run(
        app,
        host=constants.SERVER_HOST,
        port=constants.WEB_SERVER_PORT,
        ssl_keyfile=str(constants.KEY_PATH),
        ssl_certfile=str(constants.CERT_PATH),
    )
    logger.info("Web server started.")


def main():
    generate_ssl_cert()
    logger.info("Starting TCP servers in background threads ...")
    tcp_thread = threading.Thread(target=run_secure_tcp_server, daemon=True)
    tcp_thread.start()
    logger.info(
        f"Secure TCP server thread started on port {constants.SECURE_TCP_SERVER_PORT} - Usage (e.g., echo "
        f'"message" | openssl s_client -connect <HOST IP>:{constants.SECURE_TCP_SERVER_PORT})'
    )
    netcat_thread = threading.Thread(target=run_plain_tcp_server, daemon=True)
    netcat_thread.start()
    logger.info(
        f"Plain TCP server thread started on port {constants.PLAIN_TCP_SERVER_PORT} - Usage (e.g., echo "
        f'"message" | nc <HOST IP>:{constants.PLAIN_TCP_SERVER_PORT})'
    )
    logger.info("Starting the FastAPI HTTPS web server now.")
    start_web_server()


if __name__ == "__main__":
    main()
