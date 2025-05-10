import os
import yaml
from bitvoker.logger import setup_logger
from bitvoker.constants import TCP_SERVER_PORT, SERVER_HOST

logger = setup_logger("config")


class Config:
    def __init__(self, filename=None):
        self.filename = filename or os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
        self.config_data = {}
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.config_data = yaml.safe_load(f) or {}
            else:
                self.create_default_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            self.create_default_config()

    def create_default_config(self):
        self.config_data = {
            "preprompt": "You are an assistant that summarizes technical logs and alerts. Be concise but informative.",
            "enable_ai": False,
            "show_original": True,
            "gui_theme": "dark",
            "telegram": {"enabled": False, "bot_token": "", "chat_id": ""},
            "discord": {"enabled": False, "webhook_url": "", "token": ""},
            "slack": {"enabled": False, "webhook_url": "", "token": ""},
            "gotify": {"enabled": False, "server_url": "", "app_token": ""}
        }

        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                yaml.safe_dump(self.config_data, f, sort_keys=False)
            logger.info(f"Created default configuration at {self.filename}")
        except Exception as e:
            logger.error(f"Failed to create default configuration: {str(e)}")

    @property
    def preprompt(self):
        return self.config_data.get("preprompt", "")

    @property
    def enable_ai(self):
        return self.config_data.get("enable_ai", False)

    @property
    def show_original(self):
        return self.config_data.get("show_original", True)

    @property
    def gui_theme(self):
        return self.config_data.get("gui_theme", "dark")

    # Server host/port properties now use constants
    @property
    def server_host(self):
        return SERVER_HOST

    @property
    def server_port(self):
        return TCP_SERVER_PORT

    @property
    def notification_channels(self):
        channels = []
        for channel_type in ["telegram", "discord", "slack", "gotify"]:
            if channel_type in self.config_data and self.config_data[channel_type].get("enabled", False):
                channel_config = self.config_data[channel_type].copy()
                channels.append({
                    'type': channel_type,
                    'enabled': True,
                    'name': f"{channel_type.capitalize()} Notification",
                    'config': {k: v for k, v in channel_config.items() if k != 'enabled'}
                })
        return channels
