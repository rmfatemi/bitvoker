import os
import yaml

class Config:
    def __init__(self, filename="config.yaml"):
        self.filename = filename
        self.config_data = self._load_config()

    def _load_config(self):
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(pkg_dir, os.pardir))
        config_path = os.path.join(root_dir, self.filename)

        default_config = {
            "preprompt": "Just summarize what you see after colon \":\" - do not say anything extra",
            "enable_ai": True,
            "show_original": True,
            "server_host": "",
            "server_port": 9090,
            "gui_theme": "dark",
            "ntfy": {
                "enabled": True,
                "server_url": "https://ntfy.sh",
                "topic": "bitvoker_notifications"
            },
            "telegram": {
                "enabled": False,
                "bot_token": "",
                "chat_id": ""
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "token": ""
            },
            "discord": {
                "enabled": False,
                "webhook_url": "",
                "token": ""
            },
            "gotify": {
                "enabled": False,
                "server_url": "",
                "app_token": ""
            }
        }

        if not os.path.exists(config_path):
            with open(config_path, "w", encoding="utf-8") as config_file:
                yaml.safe_dump(default_config, config_file, sort_keys=False)
            return default_config

        with open(config_path, "r", encoding="utf-8") as config_file:
            try:
                data = yaml.safe_load(config_file) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing config file: {e}") from e

        for key, value in default_config.items():
            if key not in data:
                data[key] = value
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if subkey not in data[key]:
                        data[key][subkey] = subvalue

        return data

    @property
    def preprompt(self):
        return self.config_data.get("preprompt", "Summarize: ")

    @property
    def enable_ai(self):
        return self.config_data.get("enable_ai", True)

    @property
    def show_original(self):
        return self.config_data.get("show_original", True)

    @property
    def server_host(self):
        return self.config_data.get("server_host", "")

    @property
    def server_port(self):
        return self.config_data.get("server_port", 9090)

    @property
    def gui_theme(self):
        return self.config_data.get("gui_theme", "dark")

    @property
    def ntfy(self):
        return self.config_data.get("ntfy", {})

    @property
    def telegram(self):
        return self.config_data.get("telegram", {})

    @property
    def slack(self):
        return self.config_data.get("slack", {})

    @property
    def discord(self):
        return self.config_data.get("discord", {})

    @property
    def gotify(self):
        return self.config_data.get("gotify", {})

    @property
    def notification_channels(self):
        channels = []
        for channel in ["ntfy", "telegram", "slack", "discord", "gotify"]:
            channels.append(self.config_data.get(channel, {}))
        return channels
