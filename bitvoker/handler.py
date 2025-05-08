import socketserver

from bitvoker.logger import setup_logger

logger = setup_logger("handler")

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        original_message = data.decode("utf-8")
        displayed_message = original_message[:120] + "..." if len(original_message) > 120 else original_message
        logger.info("Received: %s", displayed_message)
        ai_result = ""
        if self.server.config.enable_ai:
            try:
                ai_result = self.server.ai.process_message(original_message)
                display_ai = ai_result[:120] + "..." if len(ai_result) > 120 else ai_result
                logger.debug("AI processed message result: %s", display_ai)
            except Exception as e:
                logger.exception("Error processing message through AI")
        if self.server.config.enable_ai and self.server.config.show_original:
            final_message = f"AI Summary:\n{ai_result}\n\nOriginal Message:\n{original_message}"
        elif self.server.config.enable_ai and not self.server.config.show_original:
            final_message = ai_result
        elif not self.server.config.enable_ai and self.server.config.show_original:
            final_message = original_message
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
