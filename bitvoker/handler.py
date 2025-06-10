import socketserver

from time import strftime, localtime

from bitvoker.utils import truncate
from bitvoker.logger import setup_logger
from bitvoker.database import insert_notification


logger = setup_logger(__name__)


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            chunks = []
            while True:
                chunk = self.request.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
                if len(chunk) < 4096:
                    break
            data = b"".join(chunks).strip()
        except Exception as e:
            logger.exception(f"error reading socket data: {e}")
            return

        original_message = data.decode("utf-8")

        if not original_message or original_message.strip() == "":
            logger.warning("empty message received, ignoring")
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
                # TODO: maybe let the user decide what it should look like
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
