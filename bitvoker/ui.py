import threading
import time
import yaml
import logging
import socketserver
from flask import Flask, render_template, request, redirect, url_for, jsonify
from bitvoker.config import Config
from bitvoker.handler import Handler
from bitvoker.logger import setup_logger
from bitvoker.ai import AI
from bitvoker.telegram import Telegram
from bitvoker.database import get_notifications

logger = setup_logger("ui")
tcp_server_instance = None

def run_tcp_server():
    global tcp_server_instance
    config = Config()
    telegram = Telegram(config.bot_token, config.chat_id)
    ai = AI(config.preprompt)
    HOST, PORT = config.server_host, config.server_port
    socketserver.TCPServer.allow_reuse_address = True
    tcp_server_instance = socketserver.ThreadingTCPServer((HOST, PORT), Handler)
    tcp_server_instance.config = config
    tcp_server_instance.ai = ai
    tcp_server_instance.telegram = telegram
    logger.info("Server listening on %s:%s ...", HOST if HOST else "all interfaces", PORT)
    tcp_server_instance.serve_forever()

class MemoryLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_entries = []
    def emit(self, record):
        self.log_entries.append({"timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created)),
                                 "level": record.levelname,
                                 "message": record.getMessage()})
    def get_logs(self):
        return self.log_entries

mem_handler = MemoryLogHandler()
logging.getLogger().addHandler(mem_handler)

class BitvokerUI:
    def __init__(self):
        self.server_thread = threading.Thread(target=run_tcp_server, daemon=True)
    def start(self):
        self.server_thread.start()
        app.run(debug=True, port=5000, use_reloader=False)

app = Flask(__name__, template_folder="../templates")

@app.route("/", methods=["GET", "POST"])
def index():
    config = Config()
    if request.method == "POST":
        data = request.form
        config.config_data["bot_token"] = data.get("bot_token", config.config_data.get("bot_token"))
        config.config_data["chat_id"] = data.get("chat_id", config.config_data.get("chat_id"))
        preprompt_val = data.get("preprompt", config.config_data.get("preprompt"))
        if len(preprompt_val) > 2048:
            preprompt_val = preprompt_val[:2048]
        config.config_data["preprompt"] = preprompt_val
        if preprompt_val.strip() == "":
            config.config_data["enable_ai"] = False
        else:
            config.config_data["enable_ai"] = True if data.get("enable_ai") == "on" else False
        config.config_data["server_host"] = data.get("server_host", config.config_data.get("server_host"))
        config.config_data["server_port"] = int(data.get("server_port", config.config_data.get("server_port")))
        config.config_data["show_original"] = True if data.get("show_original") == "on" else False
        with open(config.filename, "w", encoding="utf-8") as f:
            yaml.safe_dump(config.config_data, f)
        return redirect(url_for("index", active="settings") + "#settings")
    return render_template("index.html", config=config.config_data, notifications=[], logs=mem_handler.get_logs())

@app.route("/get_notifications")
def get_notifications_endpoint():
    limit = request.args.get("limit", default=20, type=int)
    date_filter = request.args.get("date", default="", type=str)
    notifs = get_notifications(limit, date_filter)
    return jsonify(notifications=notifs)

@app.route("/get_logs")
def get_logs_endpoint():
    return jsonify(logs=mem_handler.get_logs())

if __name__ == "__main__":
    ui = BitvokerUI()
    ui.start()
