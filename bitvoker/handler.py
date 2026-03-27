import hmac
import socketserver

from time import strftime, localtime

from bitvoker.utils import truncate
from bitvoker.logger import setup_logger
from bitvoker.database import insert_notification


logger = setup_logger(__name__)

TOKEN_PREFIX = "TOKEN:"


class Handler(socketserver.BaseRequestHandler):
    def _verify_token(self, message):
        config = getattr(self.server, "config", None)
        if not config:
            return message
        expected_token = config.config_data.get("message_token", "")
        if not expected_token:
            return message
        if not message.startswith(TOKEN_PREFIX):
            logger.warning(f"message rejected: missing token prefix from {self.client_address[0]}")
            return None
        rest = message[len(TOKEN_PREFIX):]
        sep_idx = rest.find(":")
        if sep_idx == -1:
            logger.warning(f"message rejected: malformed token from {self.client_address[0]}")
            return None
        provided_token = rest[:sep_idx]
        if not hmac.compare_digest(provided_token, expected_token):
            logger.warning(f"message rejected: invalid token from {self.client_address[0]}")
            return None
        return rest[sep_idx + 1:]

    def handle(self):
        try:
            self.request.settimeout(2.0)
            chunks = []
            while True:
                try:
                    chunk = self.request.recv(4096)
                    if not chunk:
                        break
                    chunks.append(chunk)
                except (TimeoutError, OSError):
                    break
            data = b"".join(chunks).strip()
        except Exception as e:
            logger.exception(f"error reading socket data: {e}")
            return

        try:
            original_message = data.decode("utf-8")
        except UnicodeDecodeError:
            logger.warning("received non-utf8 data, ignoring")
            return

        if not original_message or original_message.strip() == "":
            logger.warning("empty message received, ignoring")
            return

        original_message = self._verify_token(original_message)
        if original_message is None:
            return

        logger.debug(f"received: {truncate(original_message, 120)}")

        ts = strftime("%Y-%m-%d %H:%M:%S", localtime())
        client_ip = self.client_address[0]
        title = f"[{ts} - Notification from {client_ip}]"

        match_result = self.server.match.process(client_ip, original_message) if hasattr(self.server, "match") else None

        ai_result = ""
        if match_result:
            ai_result = match_result.ai_processed or ""

            message = ""
            if match_result.should_send_ai and match_result.should_send_original:
                message = (
                    f"\n~~~~~~~~~[AI Processed]~~~~~~~~~\n{match_result.ai_processed}\n~~~~~~~[Original"
                    f" Message]~~~~~~~\n{match_result.original_text}"
                )
            elif match_result.should_send_ai:
                message = match_result.ai_processed
            elif match_result.should_send_original:
                message = match_result.original_text

            if message:
                try:
                    if match_result.destinations:
                        self.server.notifier.send_message(
                            message, title=title, destination_names=match_result.destinations
                        )
                    else:
                        self.server.notifier.send_message(message, title=title)
                except Exception as e:
                    logger.exception(f"error during notification dispatch: {e}")

        insert_notification(ts, original_message, ai_result, client_ip)
