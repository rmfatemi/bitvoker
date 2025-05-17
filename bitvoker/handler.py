import socketserver

from time import strftime, localtime

from bitvoker.ai import AI
from bitvoker.config import Config
from bitvoker.notifier import Notifier
from bitvoker.utils import setup_logger, truncate
from bitvoker.database import insert_notification


logger = setup_logger("handler")


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        current_config_manager = Config()
        self.server.config_manager = current_config_manager
        if current_config_manager.enable_ai:
            if self.server.ai is None or getattr(self.server.ai, "preprompt", None) != current_config_manager.preprompt:
                self.server.ai = AI(current_config_manager.preprompt)
        else:
            self.server.ai = None

        self.server.notifier = Notifier(current_config_manager.notification_channels)
        data = self.request.recv(1024).strip()
        original_message = data.decode("utf-8")

        if not original_message or original_message.strip() == "":
            logger.warning("Empty message received, ignoring")
            return

        logger.debug("Received: %s", truncate(original_message, 120))

        ai_result = ""
        message_body = ""
        config = self.server.config_manager

        if config.enable_ai and self.server.ai is not None:
            try:
                ai_result = self.server.ai.process_message(original_message)
                logger.debug("AI processed message result: %s", truncate(ai_result, 120))
            except Exception as e:
                logger.error(f"AI processing failed after all retries, disabling AI: {e}")
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
                message_body = "Error processing with AI. Original message not shown as per config."
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
                logger.exception("Overall error during notification dispatch: %s", e)
        insert_notification(ts, original_message, ai_result if config.enable_ai else "", client_ip)
