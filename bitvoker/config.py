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
                logger.info(f"configuration loaded from {CONFIG_FILENAME}")
            else:
                logger.warning(f"config file {CONFIG_FILENAME} not found, using empty configuration")
                self.config_data = {}
        except Exception as e:
            logger.error(f"failed to load configuration: {str(e)}")
            self.config_data = {}

    def save(self):
        try:
            os.makedirs(os.path.dirname(CONFIG_FILENAME), exist_ok=True)
            with open(CONFIG_FILENAME, "w", encoding="utf-8") as f:
                yaml.safe_dump(self.config_data, f, sort_keys=False)
            logger.info("configuration saved")
        except Exception as e:
            logger.error(f"failed to save configuration: {str(e)}")

    def get_ai_config(self) -> Dict[str, Any]:
        return self.config_data.get("ai", {})

    def get_rules(self) -> List[Dict[str, Any]]:
        return self.config_data.get("rules", [])

    def get_channels(self) -> List[Dict[str, Any]]:
        return self.config_data.get("notification_channels", [])

    def get_enabled_channels(self) -> List[Dict[str, Any]]:
        return [c for c in self.get_channels() if c.get("enabled", False)]

    def get_enabled_rules(self) -> List[Dict[str, Any]]:
        return [r for r in self.get_rules() if r.get("enabled", False)]

    def get_default_rule(self) -> Optional[Dict[str, Any]]:
        rules = self.get_rules()
        if not rules:
            logger.warning("no rules found")
            return None

        for rule in rules:
            if rule.get("name") == "default-rule":
                return rule

        logger.warning("default rule not found")
        return None

    def validate_config(self, config: Dict[str, Any]) -> bool:
        if not isinstance(config, dict):
            logger.error("invalid config: root must be a dictionary")
            return False

        ai = config.get("ai", {})
        if not isinstance(ai, dict):
            logger.error("invalid config: ai section must be a dictionary")
            return False

        if "provider" not in ai:
            logger.error("invalid config: ai section must have provider field")
            return False

        if "meta_ai" not in ai or "ollama" not in ai:
            logger.error("invalid config: ai section must have meta_ai and ollama sections")
            return False

        if not isinstance(ai.get("ollama", {}), dict):
            logger.error("invalid config: ollama section must be a dictionary")
            return False

        if "url" not in ai.get("ollama", {}) or "model" not in ai.get("ollama", {}):
            logger.error("invalid config: ollama section must have url and model fields")
            return False

        rules = config.get("rules", [])
        if not isinstance(rules, list):
            logger.error("invalid config: rules section must be a list")
            return False

        for rule in rules:
            if not isinstance(rule, dict):
                logger.error("invalid config: each rule must be a dictionary")
                return False

            required_fields = ["name", "enabled", "preprompt", "match", "notify"]
            for field in required_fields:
                if field not in rule:
                    logger.error(f"invalid config: each rule must have {field} field")
                    return False

            match = rule.get("match", {})
            if (
                not isinstance(match, dict)
                or "source" not in match
                or "og_text_regex" not in match
                or "ai_text_regex" not in match
            ):
                logger.error("invalid config: rule match must contain source, og_text_regex, and ai_text_regex")
                return False

            notify = rule.get("notify", {})
            if (
                not isinstance(notify, dict)
                or "destinations" not in notify
                or "original_message" not in notify
                or "ai_processed" not in notify
            ):
                logger.error(
                    "invalid config: rule notify must contain destinations, original_message, and ai_processed"
                )
                return False

            for msg_type in ["original_message", "ai_processed"]:
                msg_config = notify.get(msg_type, {})
                if not isinstance(msg_config, dict) or "enabled" not in msg_config or "match_regex" not in msg_config:
                    logger.error(f"invalid config: {msg_type} must contain enabled and match_regex")
                    return False

        channels = config.get("notification_channels", [])
        if not isinstance(channels, list):
            logger.error("invalid config: notification_channels section must be a list")
            return False

        for channel in channels:
            if not isinstance(channel, dict):
                logger.error("invalid config: each channel must be a dictionary")
                return False

            if "name" not in channel or "url" not in channel or "enabled" not in channel:
                logger.error("invalid config: each channel must have a name, url, and enabled field")
                return False

        return True

    def update_config(self, new_config: Dict[str, Any]) -> bool:
        if self.validate_config(new_config):
            self.config_data = new_config
            self.save()
            return True
        else:
            logger.error("invalid configuration detected, keeping previous configuration")
            return False
