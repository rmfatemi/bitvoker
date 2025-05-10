import socketserver

from time import strftime, localtime
<<<<<<< Updated upstream
from bitvoker.store import notifications
from bitvoker.logger import setup_logger
from bitvoker.config import Config
from bitvoker.ai import AI
from bitvoker.telegram import Telegram

logger = setup_logger("handler")

=======

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


>>>>>>> Stashed changes
class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        # Reload config on each request to pick up changes
        current_config_manager = Config()
        self.server.config_manager = current_config_manager

        # Re-initialize AI and Notifier based on potentially updated config
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
        title = "Bitvoker Alert"
        message_body = ""

        config = self.server.config_manager

        if config.enable_ai and self.server.ai is not None:
            try:
                ai_result = self.server.ai.process_message(original_message)
                display_ai = ai_result[:120] + "..." if len(ai_result) > 120 else ai_result
                logger.debug("AI processed message result: %s", display_ai)

                if config.show_original:
                    title = "AI Summary & Original"
                    message_body = f"AI Summary:\n{ai_result}\n\n---\nOriginal Message:\n{original_message}"
                else:
                    title = "AI Summary"
                    message_body = ai_result
            except Exception as e:
                logger.exception("Error processing message through AI")
<<<<<<< Updated upstream
        if self.server.config.enable_ai and self.server.config.show_original:
            final_message = f"AI Summary:\n{ai_result}\n\nOriginal Message:\n{original_message}"
        elif self.server.config.enable_ai and not self.server.config.show_original:
            final_message = f"AI Summary:\n{ai_result}"
        elif not self.server.config.enable_ai and self.server.config.show_original:
            final_message = original_message
        else:
            final_message = ""
        if len(final_message) > 4096:
            final_message = final_message[:4096]
            logger.warning("Final message truncated to meet Telegram's 4096 character limit.")
        if final_message:
=======
                title = "Notification (AI Processing Error)"
                if config.show_original:
                    message_body = original_message
                else:
                    message_body = "Error processing with AI. Original message not shown as per config."
        else:
            if config.show_original:
                title = "Notification"
                message_body = original_message
            else:
                message_body = ""

        if message_body:
>>>>>>> Stashed changes
            try:
                self.server.notifier.send_message(message_body, title=title)
            except Exception as e:
                logger.exception("Overall error during notification dispatch: %s", e)

        ts = strftime('%Y-%m-%d %H:%M:%S', localtime())
        client_ip = self.client_address[0]
<<<<<<< Updated upstream
        notification = {"timestamp": ts, "original": original_message, "ai": ai_result, "client": client_ip}
        notifications.append(notification)
=======
        insert_notification(ts, original_message, ai_result if config.enable_ai else "", client_ip)
>>>>>>> Stashed changes
