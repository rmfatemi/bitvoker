import socketserver

from time import strftime, localtime

from bitvoker.utils import truncate
from bitvoker.logger import setup_logger
from bitvoker.database import insert_notification
from bitvoker.components import refresh_server_components


logger = setup_logger("handler")


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        refresh_server_components(self.server, force_new_config=True)
        data = self.request.recv(1024).strip()
        original_message = data.decode("utf-8")

        if not original_message or original_message.strip() == "":
            logger.warning("Empty message received, ignoring")
            return

        logger.debug(f"received: {truncate(original_message, 120)}")

        ai_result = ""
        message_body = ""
        config = self.server.config_manager

        if config.enable_ai and self.server.ai is not None:
            try:
                ai_result = self.server.ai.process_message(original_message)
            except Exception as e:
                logger.error(f"ai processing failed after all retries, disabling ai: {e}")
                config.enable_ai = False
                self.server.ai = None

            if ai_result:
                if config.show_original:
                    message_body = f"[AI Summary]\n{ai_result}\n[Original Message]\n{original_message}"
                else:
                    message_body = ai_result
            elif config.show_original:
                message_body = original_message
            else:
                message_body = "error processing with ai. original message not shown as per config."
        else:
            if config.show_original:
                message_body = original_message
            else:
                message_body = ""

        ts = strftime("%Y-%m-%d %H:%M:%S", localtime())
        client_ip = self.client_address[0]
        title = f"[{ts} - Notification from {client_ip}]"
        if message_body:
            try:
                self.server.notifier.send_message(message_body, title=title)
            except Exception as e:
                logger.exception(f"overall error during notification dispatch: {e}")

        insert_notification(ts, original_message, ai_result if config.enable_ai else "", client_ip)
