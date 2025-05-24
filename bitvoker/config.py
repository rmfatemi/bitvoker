import os
import yaml

from typing import Dict, Any, List, Optional

from bitvoker.logger import setup_logger
from bitvoker.constants import CONFIG_FILENAME


logger = setup_logger("config")


class Config:
    def __init__(self):
        self.config_data = {}
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILENAME):
                with open(CONFIG_FILENAME, "r", encoding="utf-8") as f:
                    self.config_data = yaml.safe_load(f) or {}
                logger.info(f"Configuration loaded from {CONFIG_FILENAME}")
            else:
                logger.warning(f"Config file {CONFIG_FILENAME} not found, using empty configuration")
                self.config_data = {}
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            self.config_data = {}

    def save(self):
        try:
            os.makedirs(os.path.dirname(CONFIG_FILENAME), exist_ok=True)
            with open(CONFIG_FILENAME, "w", encoding="utf-8") as f:
                yaml.safe_dump(self.config_data, f, sort_keys=False)
            logger.info("Configuration saved")
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")

    def get_ai_config(self) -> Dict[str, Any]:
        return self.config_data.get("ai", {})

    def update_ai_config(self, config: Dict[str, Any]) -> None:
        self.config_data["ai"] = config
        default_rule = self.get_default_rule()
        if default_rule:
            default_rule["enabled"] = config.get("enabled", False)
            self.update_default_rule(default_rule)
        self.save()

    def get_rules(self) -> List[Dict[str, Any]]:
        return self.config_data.get("rules", [])

    def update_rule(self, rule_id: int, rule_data: Dict[str, Any]) -> bool:
        rules = self.get_rules()
        if 0 <= rule_id < len(rules):
            rules[rule_id] = rule_data
            self.config_data["rules"] = rules
            self.save()
            return True
        return False

    def add_rule(self, rule_data: Dict[str, Any]) -> int:
        rules = self.get_rules()
        rules.append(rule_data)
        self.config_data["rules"] = rules
        self.save()
        return len(rules) - 1

    def delete_rule(self, rule_id: int) -> bool:
        rules = self.get_rules()
        if 0 <= rule_id < len(rules):
            if rules[rule_id]["name"] == "default-rule":
                logger.error("Cannot delete default rule")
                return False
            del rules[rule_id]
            self.config_data["rules"] = rules
            self.save()
            return True
        return False

    def get_channels(self) -> List[Dict[str, Any]]:
        return self.config_data.get("notification_channels", [])

    def update_channel(self, channel_id: int, channel_data: Dict[str, Any]) -> bool:
        channels = self.get_channels()
        if 0 <= channel_id < len(channels):
            channels[channel_id] = channel_data
            self.config_data["notification_channels"] = channels
            self.save()
            return True
        return False

    def add_channel(self, channel_data: Dict[str, Any]) -> int:
        channels = self.get_channels()
        channels.append(channel_data)
        self.config_data["notification_channels"] = channels
        self.save()
        return len(channels) - 1

    def delete_channel(self, channel_id: int) -> bool:
        channels = self.get_channels()
        if 0 <= channel_id < len(channels):
            del channels[channel_id]
            self.config_data["notification_channels"] = channels
            self.save()
            return True
        return False

    def get_enabled_channels(self) -> List[Dict[str, Any]]:
        return [c for c in self.get_channels() if c.get("enabled", False)]

    def get_enabled_rules(self) -> List[Dict[str, Any]]:
        return [r for r in self.get_rules() if r.get("enabled", False)]

    def get_default_rule(self) -> Optional[Dict[str, Any]]:
        rules = self.get_rules()
        if not rules:
            logger.warning("No rules found")
            return None

        for rule in rules:
            if rule.get("name") == "default-rule":
                return rule

        logger.warning("Default rule not found")
        return None

    def update_default_rule(self, rule_data: Dict[str, Any]) -> bool:
        rules = self.get_rules()
        default_rule_index = None

        for i, rule in enumerate(rules):
            if rule.get("name") == "default-rule":
                default_rule_index = i
                break

        if default_rule_index is not None:
            rule_data["name"] = "default-rule"
            rules[default_rule_index] = rule_data
            self.config_data["rules"] = rules
            self.save()
            return True

        # If no default rule exists, add it
        if rules:  # Only add if there are already some rules
            rule_data["name"] = "default-rule"
            rules.insert(0, rule_data)
            self.config_data["rules"] = rules
            self.save()
            return True

        return False

    def update_default_rule_fields(self, fields: Dict[str, Any]) -> bool:
        default_rule = self.get_default_rule()
        if not default_rule:
            return False

        if "enabled" in fields:
            default_rule["enabled"] = fields["enabled"]
            ai_config = self.get_ai_config()
            ai_config["enabled"] = fields["enabled"]
            self.config_data["ai"] = ai_config

        if "preprompt" in fields:
            default_rule["preprompt"] = fields["preprompt"]

        if "show_original" in fields:
            if "notify" not in default_rule:
                default_rule["notify"] = {}
            if "original_message" not in default_rule["notify"]:
                default_rule["notify"]["original_message"] = {}
            default_rule["notify"]["original_message"]["enabled"] = fields["show_original"]

        return self.update_default_rule(default_rule)
