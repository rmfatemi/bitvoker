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
            "ai": {
                "enabled": False,
                "provider": "meta_ai",
                "meta_ai": {},
                "ollama": {"url": "http://{server_ip}:11434", "model": "gemma3:1b"},
            },
            "rules": [
                {
                    "name": "default-rule",
                    "enabled": True,
                    "preprompt": "summarize this technical message briefly and clearly",
                    "match": {"source": "", "og_text_regex": "", "ai_text_regex": ""},
                    "notify": {
                        "destinations": [],
                        "original_message": {"enabled": True, "match_regex": ""},
                        "ai_summary": {"enabled": True, "match_regex": ""},
                    },
                }
            ],
            "notification_channels": [
                {"name": "telegram", "enabled": False, "url": "tgram://{token}/{chat_id}"},
                {"name": "slack", "enabled": False, "url": "slack://{token}/{channel}"},
                {"name": "discord", "enabled": False, "url": "discord://{webhook_id}/{webhook_token}"},
                {"name": "ntfy", "enabled": False, "url": "ntfy://{topic}"},
                {"name": "pushover", "enabled": False, "url": "pover://{user_key}/{token}"},
                {"name": "gotify", "enabled": False, "url": "gotify://{host}/{token}"},
            ],
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

    def get_ai_config(self):
        return self.config_data.get(
            "ai",
            {
                "enabled": False,
                "provider": "meta_ai",
                "meta_ai": {},
                "ollama": {"url": "http://{server_ip}:11434", "model": "gemma3:1b"},
            },
        )

    def update_ai_config(self, config):
        self.config_data["ai"] = config
        self.save()

    def get_rules(self):
        return self.config_data.get("rules", [])

    def update_rule(self, rule_id, rule_data):
        rules = self.get_rules()
        if 0 <= rule_id < len(rules):
            rules[rule_id] = rule_data
            self.config_data["rules"] = rules
            self.save()
            return True
        return False

    def add_rule(self, rule_data):
        rules = self.get_rules()
        rules.append(rule_data)
        self.config_data["rules"] = rules
        self.save()
        return len(rules) - 1

    def delete_rule(self, rule_id):
        rules = self.get_rules()
        if 0 <= rule_id < len(rules):
            del rules[rule_id]
            self.config_data["rules"] = rules
            self.save()
            return True
        return False

    def get_channels(self):
        return self.config_data.get("notification_channels", [])

    def update_channel(self, channel_id, channel_data):
        channels = self.get_channels()
        if 0 <= channel_id < len(channels):
            channels[channel_id] = channel_data
            self.config_data["notification_channels"] = channels
            self.save()
            return True
        return False

    def add_channel(self, channel_data):
        channels = self.get_channels()
        channels.append(channel_data)
        self.config_data["notification_channels"] = channels
        self.save()
        return len(channels) - 1

    def delete_channel(self, channel_id):
        channels = self.get_channels()
        if 0 <= channel_id < len(channels):
            del channels[channel_id]
            self.config_data["notification_channels"] = channels
            self.save()
            return True
        return False

    def get_enabled_channels(self):
        return [c for c in self.get_channels() if c.get("enabled", False)]

    def get_enabled_rules(self):
        return [r for r in self.get_rules() if r.get("enabled", False)]
