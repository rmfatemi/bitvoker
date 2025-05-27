import socketserver
from time import strftime, localtime

from bitvoker.utils import truncate
from bitvoker.logger import setup_logger
from bitvoker.database import insert_notification
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

        ts = strftime("%Y-%m-%d %H:%M:%S", localtime())
        client_ip = self.client_address[0]
        title = f"[{ts} - Notification from {client_ip}]"

        alert_result = self.server.alert.process(client_ip, original_message) if hasattr(self.server, "alert") else None

        ai_result = ""

        if alert_result:
            ai_result = alert_result.ai_processed or ""

            message = ""

            if alert_result.should_send_ai and alert_result.should_send_original:
                message = (
                    f"[AI Processed]\n{alert_result.ai_processed}\n[Original Message]\n{alert_result.original_text}"
                )
            elif alert_result.should_send_ai:
                message = alert_result.ai_processed
            elif alert_result.should_send_original:
                message = alert_result.original_text

            if message:
                try:
                    if alert_result.destinations:
                        self.server.alert.get_enabled_destinations_by_names(alert_result.destinations)
                        self.server.notifier.send_message(
                            message, title=title, destination_names=alert_result.destinations
                        )
                    else:
                        self.server.notifier.send_message(message, title=title)
                except Exception as e:
                    logger.exception(f"Error during notification dispatch: {e}")

        insert_notification(ts, original_message, ai_result, client_ip)
