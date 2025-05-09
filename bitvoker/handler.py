import socketserver
from time import strftime, localtime
from bitvoker.store import notifications
from bitvoker.logger import setup_logger
from bitvoker.config import Config
from bitvoker.ai import AI
from bitvoker.telegram import Telegram

logger = setup_logger("handler")


def truncate(text, max_length=80):
    single_line = text.replace("\n", " ").strip()
    if len(single_line) <= max_length:
        return single_line
    else:
        return single_line[:max_length] + "..."


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        updated_config = Config()
        self.server.config = updated_config
        if updated_config.enable_ai:
            self.server.ai = AI(updated_config.preprompt)
        else:
            self.server.ai = None
        self.server.telegram = Telegram(updated_config.bot_token, updated_config.chat_id)

        data = self.request.recv(1024).strip()
        original_message = data.decode("utf-8")
        displayed_message = truncate(original_message, 80)
        logger.info("Received: %s", displayed_message)

        ai_result = ""
        if self.server.config.enable_ai and self.server.ai is not None:
            try:
                ai_result = self.server.ai.process_message(original_message)
                display_ai = truncate(ai_result, 80)
                logger.debug("AI processed message result: %s", display_ai)
            except Exception as e:
                logger.exception("Error processing message through AI")

        # Build final_message based on configuration:
        if self.server.config.enable_ai:
            truncated_ai = truncate(ai_result, 80)
            if self.server.config.show_original:
                final_message = f"AI Summary: {truncated_ai}\nOriginal Message: {truncate(original_message, 80)}"
            else:
                final_message = f"AI Summary: {truncated_ai}"
        else:
            if self.server.config.show_original:
                final_message = truncate(original_message, 80)
            else:
                final_message = ""

        if len(final_message) > 4096:
            final_message = final_message[:4096]
            logger.warning("Final message truncated to meet Telegram's 4096 character limit.")

        if final_message:
            try:
                self.server.telegram.send_message(final_message)
                logger.info("Successfully sent message to Telegram.")
            except Exception as e:
                logger.exception("Error sending Telegram message")

        ts = strftime('%Y-%m-%d %H:%M:%S', localtime())
        client_ip = self.client_address[0]
        notification = {"timestamp": ts, "original": original_message, "ai": ai_result, "client": client_ip}
        notifications.append(notification)
