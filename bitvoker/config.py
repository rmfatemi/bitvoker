import os
import yaml

from bitvoker.logger import setup_logger

logger = setup_logger("config")


class Config:
    def __init__(self):
        self.filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "config.yaml")
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
            logger.error(f"failed to load configuration: {str(e)}")
            self.create_default_config()

    def create_default_config(self):
        self.config_data = {
            "preprompt": "You are an assistant that summarizes technical logs and alerts. Be concise but informative",
            "enable_ai": False,
            "show_original": True,
            "gui_theme": "dark",
            "ai_provider": {"type": "meta_ai", "url": "http://<server-ip>:11434", "model": "gemma3:1b"},
            "telegram": {"enabled": False, "chat_id": "", "token": ""},
            "discord": {"enabled": False, "webhook_id": "", "token": ""},
            "slack": {"enabled": False, "webhook_id": "", "token": ""},
            "gotify": {"enabled": False, "server_url": "", "token": ""},
        }

        try:
            self.save()
            logger.info(f"created default configuration at {self.filename}")
        except Exception as e:
            logger.error(f"failed to create default configuration: {str(e)}")

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            with open(self.filename, "w", encoding="utf-8") as f:
                yaml.safe_dump(self.config_data, f, sort_keys=False)
            logger.info("configuration saved")
        except Exception as e:
            logger.error(f"failed to save configuration: {str(e)}")

    def get_preprompt(self):
        return self.config_data.get("preprompt", "")

    def set_preprompt(self, value):
        self.config_data["preprompt"] = value[:2048]
        self.save()

    def get_ai_provider_config(self):
        return self.config_data.get("ai_provider", {"type": "meta_ai"})

    def set_ai_provider_config(self, value):
        self.config_data["ai_provider"] = value
        self.save()

    def get_enable_ai(self):
        return self.config_data.get("enable_ai", False)

    def set_enable_ai(self, value):
        self.config_data["enable_ai"] = value
        if not value:
            self.config_data["show_original"] = True
        self.save()

    def get_show_original(self):
        return self.config_data.get("show_original", True)

    def set_show_original(self, value):
        if self.config_data.get("enable_ai", False):
            self.config_data["show_original"] = value
            self.save()

    def get_gui_theme(self):
        return self.config_data.get("gui_theme", "dark")

    def set_gui_theme(self, value):
        self.config_data["gui_theme"] = value
        self.save()

    def get_notification_channels(self):
        channels = []
        for channel_type in ["telegram", "discord", "slack", "gotify"]:
            if channel_type in self.config_data and self.config_data[channel_type].get("enabled", False):
                channel_config = self.config_data[channel_type].copy()
                channels.append(
                    {
                        "type": channel_type,
                        "enabled": True,
                        "name": f"{channel_type.capitalize()} Notification",
                        "config": {k: v for k, v in channel_config.items() if k != "enabled"},
                    }
                )
        return channels

    def update_channel_config(self, channel_type, enabled=None, **kwargs):
        if channel_type not in ["telegram", "discord", "slack", "gotify"]:
            logger.error(f"invalid channel type: {channel_type}")
            return

        if channel_type not in self.config_data:
            self.config_data[channel_type] = {}

        if enabled is not None:
            self.config_data[channel_type]["enabled"] = enabled

        for key, value in kwargs.items():
            self.config_data[channel_type][key] = value

        self.save()
