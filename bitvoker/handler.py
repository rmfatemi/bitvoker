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

        alert_result = (
            self.server.alert.process("tcp_socket", original_message) if hasattr(self.server, "alert") else None
        )

        ai_result = ""

        if alert_result:
            ai_result = alert_result.ai_summary or ""

            message = ""

            if alert_result.should_send_ai and alert_result.should_send_original:
                message = f"[AI Summary]\n{alert_result.ai_summary}\n[Original Message]\n{alert_result.original_text}"
            elif alert_result.should_send_ai:
                message = alert_result.ai_summary
            elif alert_result.should_send_original:
                message = alert_result.original_text

            if message:
                try:
                    if alert_result.destinations:
                        self.server.alert.get_enabled_channels_by_names(alert_result.destinations)
                        self.server.notifier.send_message(message, title=title, channel_names=alert_result.destinations)
                    else:
                        self.server.notifier.send_message(message, title=title)
                except Exception as e:
                    logger.exception(f"Error during notification dispatch: {e}")

        insert_notification(ts, original_message, ai_result, client_ip)
