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
            "rules": [self._create_default_rule()],
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

    def _create_default_rule(self):
        return {
            "name": "default-rule",
            "enabled": False,
            "preprompt": "summarize this technical message briefly and clearly",
            "match": {"source": "", "og_text_regex": "", "ai_text_regex": ""},
            "notify": {
                "destinations": [],
                "original_message": {"enabled": True, "match_regex": ""},
                "ai_summary": {"enabled": True, "match_regex": ""},
            },
        }

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
        # Sync AI enabled state with default rule
        default_rule = self.get_default_rule()
        if default_rule:
            default_rule["enabled"] = config.get("enabled", False)
            self.update_default_rule(default_rule)
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
            # Don't allow deleting default rule
            if rules[rule_id]["name"] == "default-rule":
                logger.error("cannot delete default rule")
                return False
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

    def get_default_rule(self):
        rules = self.get_rules()
        if not rules:
            logger.warning("no rules found, creating default rule")
            default_rule = self._create_default_rule()
            self.add_rule(default_rule)
            return default_rule

        # Find default rule by name
        for i, rule in enumerate(rules):
            if rule.get("name") == "default-rule":
                return rule

        # Create default rule if not found
        logger.warning("default rule not found, creating it")
        default_rule = self._create_default_rule()

        # Insert as first rule
        rules.insert(0, default_rule)
        self.config_data["rules"] = rules
        self.save()
        return default_rule

    def update_default_rule(self, rule_data):
        rules = self.get_rules()
        default_rule_index = None

        for i, rule in enumerate(rules):
            if rule.get("name") == "default-rule":
                default_rule_index = i
                break

        if default_rule_index is not None:
            # Preserve the name
            rule_data["name"] = "default-rule"
            rules[default_rule_index] = rule_data
            self.config_data["rules"] = rules
            self.save()
            return True

        # If default rule not found, add it
        rule_data["name"] = "default-rule"
        rules.insert(0, rule_data)
        self.config_data["rules"] = rules
        self.save()
        return True

    def update_default_rule_fields(self, fields):
        default_rule = self.get_default_rule()
        if not default_rule:
            return False

        # Handle top-level fields
        if "enabled" in fields:
            default_rule["enabled"] = fields["enabled"]
            # Sync with AI settings
            ai_config = self.get_ai_config()
            ai_config["enabled"] = fields["enabled"]
            self.config_data["ai"] = ai_config

        if "preprompt" in fields:
            default_rule["preprompt"] = fields["preprompt"]

        # Handle nested fields
        if "show_original" in fields:
            if "notify" not in default_rule:
                default_rule["notify"] = {}
            if "original_message" not in default_rule["notify"]:
                default_rule["notify"]["original_message"] = {}
            default_rule["notify"]["original_message"]["enabled"] = fields["show_original"]

        # Save changes to the rule
        self.update_default_rule(default_rule)
        return True
