import threading
import time
import yaml
import logging
import socketserver
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from bitvoker.config import Config
from bitvoker.handler import Handler
from bitvoker.logger import setup_logger
from bitvoker.ai import AI
from bitvoker.notifier import Notifier
from bitvoker.database import get_notifications
from bitvoker.constants import TCP_SERVER_PORT, UI_SERVER_PORT, SERVER_HOST
 
logger = setup_logger("ui")
tcp_server_instance = None
 
 
def run_tcp_server():
    global tcp_server_instance
    try:
        config_manager = Config()
        notifier = Notifier(config_manager.notification_channels)
        ai = AI(config_manager.preprompt) if config_manager.enable_ai else None
        socketserver.TCPServer.allow_reuse_address = True
 
        class CustomThreadingTCPServer(socketserver.ThreadingTCPServer):
            def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True,
                         config_manager_instance=None,
                         ai_instance=None, notifier_instance=None):
                super().__init__(server_address, RequestHandlerClass, bind_and_activate)
                self.config_manager = config_manager_instance
                self.ai = ai_instance
                self.notifier = notifier_instance
 
        tcp_server_instance = CustomThreadingTCPServer((SERVER_HOST, TCP_SERVER_PORT), Handler,
                                                       config_manager_instance=config_manager,
                                                       ai_instance=ai, notifier_instance=notifier)
        logger.info("TCP Server listening on %s:%s ...", SERVER_HOST, TCP_SERVER_PORT)
        tcp_server_instance.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start TCP server: {str(e)}")
 
 
class MemoryLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_entries = []
 
    def emit(self, record):
        self.log_entries.append({"timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created)),
                                 "level": record.levelname,
                                 "message": record.getMessage()})
        if len(self.log_entries) > 200:
            self.log_entries.pop(0)
 
    def get_logs(self):
        return self.log_entries
 
 
mem_handler = MemoryLogHandler()
logging.getLogger().addHandler(mem_handler)
 
 
class BitvokerUI:
    def __init__(self):
        self.server_thread = threading.Thread(target=run_tcp_server, daemon=True)
 
    def start(self):
        self.server_thread.start()
        app.run(debug=False, port=UI_SERVER_PORT, use_reloader=False, host=SERVER_HOST)
 
    def shutdown(self):
        global tcp_server_instance
        if tcp_server_instance:
            tcp_server_instance.shutdown()
            logger.info("TCP Server shutdown complete.")
 
 
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
 
 
@app.route("/", methods=["GET", "POST"])
def index():
    config_manager = Config()
    if request.method == "POST":
        try:
            new_config_data = config_manager.config_data.copy()
 
            preprompt_val = request.form.get("preprompt", new_config_data.get("preprompt", ""))
            if len(preprompt_val) > 2048:
                preprompt_val = preprompt_val[:2048]
            new_config_data["preprompt"] = preprompt_val
            new_config_data["enable_ai"] = True if request.form.get("enable_ai") == "on" else False
 
            if not new_config_data["enable_ai"]:
                new_config_data["show_original"] = True
            else:
                new_config_data["show_original"] = True if request.form.get("show_original") == "on" else False
 
            new_config_data["gui_theme"] = request.form.get("gui_theme", new_config_data.get("gui_theme", "dark"))
 
            for channel in ["telegram", "slack", "discord", "gotify"]:
                channel_enabled = True if request.form.get(f"channel_{channel}_enabled") == "on" else False
                if channel not in new_config_data:
                    new_config_data[channel] = {}
                new_config_data[channel]["enabled"] = channel_enabled
 
                if channel == "telegram":
                    new_config_data[channel]["bot_token"] = request.form.get(f"channel_{channel}_config_bot_token",
                                                                             new_config_data.get(channel, {}).get(
                                                                                 "bot_token", ""))
                    new_config_data[channel]["chat_id"] = request.form.get(f"channel_{channel}_config_chat_id",
                                                                           new_config_data.get(channel, {}).get(
                                                                               "chat_id", ""))
                elif channel == "slack":
                    new_config_data[channel]["webhook_url"] = request.form.get(f"channel_{channel}_config_webhook_url",
                                                                               new_config_data.get(channel, {}).get(
                                                                                   "webhook_url", ""))
                    new_config_data[channel]["token"] = request.form.get(f"channel_{channel}_config_token",
                                                                         new_config_data.get(channel, {}).get("token",
                                                                                                              ""))
                elif channel == "discord":
                    new_config_data[channel]["webhook_url"] = request.form.get(f"channel_{channel}_config_webhook_url",
                                                                               new_config_data.get(channel, {}).get(
                                                                                   "webhook_url", ""))
                    new_config_data[channel]["token"] = request.form.get(f"channel_{channel}_config_token",
                                                                         new_config_data.get(channel, {}).get("token",
                                                                                                              ""))
                elif channel == "gotify":
                    new_config_data[channel]["server_url"] = request.form.get(f"channel_{channel}_config_server_url",
                                                                              new_config_data.get(channel, {}).get(
                                                                                  "server_url", ""))
                    new_config_data[channel]["app_token"] = request.form.get(f"channel_{channel}_config_app_token",
                                                                             new_config_data.get(channel, {}).get(
                                                                                 "app_token", ""))
 
            try:
                with open(config_manager.filename, "w", encoding="utf-8") as f:
                    yaml.safe_dump(new_config_data, f, sort_keys=False)
 
                if tcp_server_instance and hasattr(tcp_server_instance, 'config_manager'):
                    fresh_config_manager = Config()
                    tcp_server_instance.config_manager = fresh_config_manager
                    if fresh_config_manager.enable_ai:
                        tcp_server_instance.ai = AI(fresh_config_manager.preprompt)
                    else:
                        tcp_server_instance.ai = None
                    tcp_server_instance.notifier = Notifier(fresh_config_manager.notification_channels)
                    logger.info("TCP Server configuration dynamically updated.")
                else:
                    logger.warning("Could not dynamically update TCP server config instance.")
            except Exception as e:
                logger.error(f"Failed to save configuration: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing form: {str(e)}")
 
        return redirect(url_for("index", active="settings") + "#settings-notifications")
 
    return render_template("index.html", config=config_manager.config_data, notifications=[],
                           logs=mem_handler.get_logs())
 
 
@app.route("/get_notifications")
def get_notifications_route():
    try:
        limit = request.args.get("limit", default=20, type=int)
        start_date = request.args.get("startDate", default="", type=str)
        end_date = request.args.get("endDate", default="", type=str)
        notifs = get_notifications(limit, start_date, end_date)
        return jsonify(notifications=notifs)
    except Exception as e:
        logger.error(f"Error retrieving notifications: {str(e)}")
        return jsonify(notifications=[], error=str(e)), 500
 
 
@app.route("/get_logs")
def get_logs():
    level = request.args.get("level", default="", type=str)
    logs = mem_handler.get_logs()
 
    if level and level != "ALL":
        logs = [log for log in logs if log["level"] == level]
 
    return jsonify(logs=logs)
 
 
if __name__ == "__main__":
    ui = BitvokerUI()
    try:
        ui.start()
    except KeyboardInterrupt:
        ui.shutdown()
        logger.info("Application shutdown complete.")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
 