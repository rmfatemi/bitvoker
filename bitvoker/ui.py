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
<<<<<<< Updated upstream
from bitvoker.telegram import Telegram
from bitvoker.store import notifications
=======
from bitvoker.notifier import Notifier
from bitvoker.database import get_notifications
>>>>>>> Stashed changes

logger = setup_logger("ui")
tcp_server_instance = None

def run_tcp_server():
    global tcp_server_instance
    config_manager = Config()
    notifier = Notifier(config_manager.notification_channels)
    ai = AI(config_manager.preprompt)
    HOST, PORT = config_manager.server_host, config_manager.server_port
    socketserver.TCPServer.allow_reuse_address = True

    class CustomThreadingTCPServer(socketserver.ThreadingTCPServer):
        def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True, config_manager_instance=None,
                     ai_instance=None, notifier_instance=None):
            super().__init__(server_address, RequestHandlerClass, bind_and_activate)
            self.config_manager = config_manager_instance
            self.ai = ai_instance
            self.notifier = notifier_instance

    tcp_server_instance = CustomThreadingTCPServer((HOST, PORT), Handler, config_manager_instance=config_manager,
                                                    ai_instance=ai, notifier_instance=notifier)
    logger.info("TCP Server listening on %s:%s ...", HOST if HOST else "all interfaces", PORT)
    tcp_server_instance.serve_forever()

class MemoryLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_entries = []

    def emit(self, record):
<<<<<<< Updated upstream
        self.log_entries.append({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created)),
            "level": record.levelname,
            "message": record.getMessage()
        })
=======
        self.log_entries.append({"timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created)),
                                 "level": record.levelname,
                                 "message": record.getMessage()})
        if len(self.log_entries) > 200:
            self.log_entries.pop(0)

>>>>>>> Stashed changes
    def get_logs(self):
        return self.log_entries

mem_handler = MemoryLogHandler()
logging.getLogger().addHandler(mem_handler)

class BitvokerUI:
    def __init__(self):
        self.server_thread = threading.Thread(target=run_tcp_server, daemon=True)

    def start(self):
        self.server_thread.start()
        app.run(debug=False, port=5000, use_reloader=False, host="0.0.0.0")

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)

@app.route("/", methods=["GET", "POST"])
def index():
    config_manager = Config()
    if request.method == "POST":
<<<<<<< Updated upstream
        data = request.form
        config.config_data["bot_token"] = data.get("bot_token", config.config_data.get("bot_token"))
        config.config_data["chat_id"] = data.get("chat_id", config.config_data.get("chat_id"))
        preprompt_val = data.get("preprompt", config.config_data.get("preprompt"))
        if len(preprompt_val) > 1000:
            preprompt_val = preprompt_val[:1000]
        config.config_data["preprompt"] = preprompt_val
        # Automatically disable AI if preprompt is empty
        if preprompt_val.strip() == "":
            config.config_data["enable_ai"] = False
        else:
            config.config_data["enable_ai"] = True if data.get("enable_ai") == "on" else False
        config.config_data["server_host"] = data.get("server_host", config.config_data.get("server_host"))
        config.config_data["server_port"] = int(data.get("server_port", config.config_data.get("server_port")))
        config.config_data["show_original"] = True if data.get("show_original") == "on" else False
        with open(config.filename, "w", encoding="utf-8") as f:
            yaml.safe_dump(config.config_data, f)
        return redirect(url_for("index"))
    return render_template("index.html", config=config.config_data, notifications=notifications, logs=mem_handler.get_logs())
=======
        new_config_data = config_manager.config_data.copy()

        # Update general settings
        preprompt_val = request.form.get("preprompt", new_config_data.get("preprompt"))
        if len(preprompt_val) > 2048:
            preprompt_val = preprompt_val[:2048]
        new_config_data["preprompt"] = preprompt_val
        new_config_data["enable_ai"] = True if request.form.get("enable_ai") == "on" else False
        new_config_data["server_host"] = request.form.get("server_host", new_config_data.get("server_host"))
        new_config_data["server_port"] = int(request.form.get("server_port", new_config_data.get("server_port")))
        new_config_data["show_original"] = True if request.form.get("show_original") == "on" else False
        new_config_data["gui_theme"] = request.form.get("gui_theme", new_config_data.get("gui_theme", "dark"))

        # Update notification channel settings for each channel type
        for channel in ["ntfy", "telegram", "slack", "discord", "gotify"]:
            channel_data = {}
            channel_data["type"] = channel
            channel_data["enabled"] = True if request.form.get(f"channel_{channel}_enabled") == "on" else False
            channel_config = {}
            prefix = f"channel_{channel}_config_"
            for key, value in request.form.items():
                if key.startswith(prefix):
                    config_key = key[len(prefix):]
                    channel_config[config_key] = value
            channel_data["config"] = channel_config
            new_config_data[channel] = channel_data

        with open(config_manager.filename, "w", encoding="utf-8") as f:
            yaml.safe_dump(new_config_data, f, sort_keys=False)

        # Dynamically update the running TCP server config
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

        return redirect(url_for("index", active="settings") + "#settings-notifications")

    return render_template("index.html", config=config_manager.config_data, notifications=[], logs=mem_handler.get_logs())
>>>>>>> Stashed changes

@app.route("/get_notifications")
def get_notifications():
    limit = request.args.get("limit", default=20, type=int)
<<<<<<< Updated upstream
    date_filter = request.args.get("date", default="", type=str)
    if date_filter:
        filtered = [n for n in notifications if n['timestamp'].startswith(date_filter)]
    else:
        filtered = notifications[:]
    filtered = list(reversed(filtered))
    return jsonify(notifications=filtered[:limit])
=======
    start_date = request.args.get("startDate", default="", type=str)
    end_date = request.args.get("endDate", default="", type=str)
    notifs = get_notifications(limit, start_date, end_date)
    return jsonify(notifications=notifs)
>>>>>>> Stashed changes

@app.route("/get_logs")
def get_logs():
    return jsonify(logs=mem_handler.get_logs())

if __name__ == "__main__":
    ui = BitvokerUI()
    ui.start()
