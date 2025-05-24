import socketserver
from time import strftime, localtime

from bitvoker.utils import truncate
from bitvoker.logger import setup_logger
from bitvoker.database import insert_notification
from bitvoker.alert import Alert
from bitvoker.ai import process_with_ai
from bitvoker.refresher import refresh_components

logger = setup_logger("handler")


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        app = self.server.app
        refresh_components(app)

        data = self.request.recv(1024).strip()
        original_message = data.decode("utf-8")

        if not original_message or original_message.strip() == "":
            logger.warning("empty message received, ignoring")
            return

        logger.debug(f"received: {truncate(original_message, 120)}")

        ai_result = ""
        message_body = ""
        config = self.server.config

        # process with alert system first
        alert = Alert(config)
        if alert.process("socket", original_message):
            logger.info("message processed by alert system")
            return

        # fallback to legacy processing
        ai_config = config.get_ai_config()
        ai_enabled = ai_config.get("enabled", False)

        if ai_enabled:
            try:
                ai_result = process_with_ai(original_message, "summarize this message", ai_config)
            except Exception as e:
                logger.error(f"ai processing failed after all retries, disabling ai: {e}")
                ai_config["enabled"] = False
                config.update_ai_config(ai_config)

            if ai_result:
                message_body = f"[AI Summary]\n{ai_result}\n[Original Message]\n{original_message}"
            else:
                message_body = original_message
        else:
            message_body = original_message

        ts = strftime("%Y-%m-%d %H:%M:%S", localtime())
        client_ip = self.client_address[0]
        title = f"[{ts} - Notification from {client_ip}]"

        if message_body:
            try:
                self.server.notifier.send_message(message_body, title=title)
            except Exception as e:
                logger.exception(f"overall error during notification dispatch: {e}")

        insert_notification(ts, original_message, ai_result if ai_enabled else "", client_ip)
