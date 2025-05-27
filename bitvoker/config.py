import os
import yaml
from typing import Dict, Any, List, Optional

from bitvoker.logger import setup_logger
from bitvoker.constants import CONFIG_FILENAME


logger = setup_logger("config")


class Config:
    def __init__(self, config_path=None):
        self.config_path = config_path or CONFIG_FILENAME
        self.config_data = {}
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config_data = yaml.safe_load(f) or {}
                logger.info(f"configuration loaded from {self.config_path}")
            else:
                logger.warning(f"config file {self.config_path} not found, using empty configuration")
                self.config_data = {}
        except (yaml.YAMLError, IOError) as e:
            logger.error(f"failed to load configuration: {str(e)}")
            self.config_data = {}

    def reload_config(self):
        self.load_config()
        return self.config_data

    def save(self) -> bool:
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(self.config_data, f, sort_keys=False)
            logger.info("configuration saved")
            return True
        except (yaml.YAMLError, IOError) as e:
            logger.error(f"failed to save configuration: {str(e)}")
            return False

    def _normalize_to_list(self, value):
        if isinstance(value, str):
            return [value]
        return value or []

    def get_ai_config(self) -> Dict[str, Any]:
        return self.config_data.get("ai", {})

    def get_rules(self) -> List[Dict[str, Any]]:
        return self.config_data.get("rules", [])

    def get_destinations(self) -> List[Dict[str, Any]]:
        return self.config_data.get("destinations", [])

    def get_enabled_destinations(self) -> List[Dict[str, Any]]:
        return [c for c in self.get_destinations() if c.get("enabled", False)]

    def get_all_destinations_if_empty(self, destination_names: List[str]) -> List[Dict[str, Any]]:
        if not destination_names:
            return self.get_enabled_destinations()
        return [d for d in self.get_enabled_destinations() if d["name"] in destination_names]

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

    def update_specific_config(self, section: str, key: str, value: Any) -> bool:
        if section not in self.config_data:
            self.config_data[section] = {}
        self.config_data[section][key] = value
        return self.save()

    def validate_rule(self, rule: Dict[str, Any]) -> bool:
        if not isinstance(rule, dict):
            logger.error("invalid rule: must be a dictionary")
            return False

        required_fields = ["name", "enabled", "preprompt", "match", "notify"]
        for field in required_fields:
            if field not in rule:
                logger.error(f"invalid rule: must have {field} field")
                return False

        match = rule.get("match", {})
        if not isinstance(match, dict):
            logger.error("invalid rule: match must be a dictionary")
            return False

        if "source" not in match or "og_text_regex" not in match or "ai_text_regex" not in match:
            logger.error("invalid rule: match must contain source, og_text_regex, and ai_text_regex")
            return False

        source = match.get("source")
        if source and not (isinstance(source, str) or isinstance(source, list)):
            logger.error("invalid rule: source must be a string or a list of strings")
            return False

        if isinstance(source, list):
            if not all(isinstance(item, str) for item in source):
                logger.error("invalid rule: all items in source list must be strings")
                return False
        elif isinstance(source, str):
            match["source"] = [source]

        notify = rule.get("notify", {})
        if (
            not isinstance(notify, dict)
            or "destinations" not in notify
            or "original_message" not in notify
            or "ai_processed" not in notify
        ):
            logger.error("invalid rule: notify must contain destinations, original_message, and ai_processed")
            return False

        destinations = notify.get("destinations")
        if isinstance(destinations, str):
            notify["destinations"] = [destinations]

        for msg_type in ["original_message", "ai_processed"]:
            msg_config = notify.get(msg_type, {})
            if not isinstance(msg_config, dict) or "enabled" not in msg_config or "match_regex" not in msg_config:
                logger.error(f"invalid rule: {msg_type} must contain enabled and match_regex")
                return False

        return True

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
            if not self.validate_rule(rule):
                return False

        destinations = config.get("destinations", [])
        if not isinstance(destinations, list):
            logger.error("invalid config: destinations section must be a list")
            return False

        for destination in destinations:
            if not isinstance(destination, dict):
                logger.error("invalid config: each destination must be a dictionary")
                return False

            if "name" not in destination or "url" not in destination or "enabled" not in destination:
                logger.error("invalid config: each destination must have a name, url, and enabled field")
                return False

        return True

    def update_config(self, new_config: Dict[str, Any]) -> bool:
        if self.validate_config(new_config):
            self.config_data = new_config
            return self.save()
        else:
            logger.error("invalid configuration detected, keeping previous configuration")
            return False
