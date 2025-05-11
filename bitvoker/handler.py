import socketserver
from time import strftime, localtime
from bitvoker.ai import AI
from bitvoker.config import Config
from bitvoker.notifier import Notifier
from bitvoker.logger import setup_logger
from bitvoker.database import insert_notification

logger = setup_logger("handler")


def truncate(text, max_length=80):
    single_line = text.replace("\n", " ").strip()
    if len(single_line) <= max_length:
        return single_line
    else:
        return single_line[:max_length] + "..."


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        current_config_manager = Config()
        self.server.config_manager = current_config_manager
        if current_config_manager.enable_ai:
            self.server.ai = AI(current_config_manager.preprompt)
        else:
            self.server.ai = None
        self.server.notifier = Notifier(current_config_manager.notification_channels)
        data = self.request.recv(1024).strip()
        original_message = data.decode("utf-8")
        displayed_message = original_message[:120] + "..." if len(original_message) > 120 else original_message
        logger.info("Received: %s", displayed_message)
        ai_result = ""
        message_body = ""
        config = self.server.config_manager
        if config.enable_ai and self.server.ai is not None:
            try:
                ai_result = self.server.ai.process_message(original_message)
                display_ai = ai_result[:120] + "..." if len(ai_result) > 120 else ai_result
                logger.debug("AI processed message result: %s", display_ai)
                if config.show_original:
                    message_body = f"[AI Summary]\n{ai_result}\n[Original Message]\n{original_message}"
                else:
                    message_body = ai_result
            except Exception:
                logger.exception("Error processing message through AI: {e}")
                if config.show_original:
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
