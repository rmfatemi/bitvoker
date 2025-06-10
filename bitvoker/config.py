import os
import yaml

from typing import Dict, Any, List, Optional

from bitvoker.logger import logger
from bitvoker.constants import CONFIG_FILENAME


logger = logger(__name__)


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
        rule_name_for_log = rule.get("name", "unnamed_rule")
        if not isinstance(rule, dict):
            logger.error(f"invalid rule '{rule_name_for_log}': must be a dictionary")
            return False

        required_fields = ["name", "enabled", "preprompt", "match", "notify"]
        for field in required_fields:
            if field not in rule:
                logger.error(f"invalid rule '{rule_name_for_log}': must have {field} field")
                return False

        match_config = rule.get("match", {})
        if not isinstance(match_config, dict):
            logger.error(f"invalid rule '{rule_name_for_log}': match must be a dictionary")
            return False

        if "sources" not in match_config or "og_text_regex" not in match_config or "ai_text_regex" not in match_config:
            logger.error(
                f"invalid rule '{rule_name_for_log}': match must contain sources, og_text_regex, and ai_text_regex"
            )
            return False

        sources = match_config.get("sources")
        if sources is None:
            match_config["sources"] = []
        elif isinstance(sources, str):
            match_config["sources"] = [] if not sources else [sources]
        elif isinstance(sources, list):
            if not all(isinstance(item, str) for item in sources):
                logger.error(f"invalid rule '{rule_name_for_log}': all items in sources list must be strings")
                return False
        else:
            logger.error(
                f"invalid rule '{rule_name_for_log}': sources must be empty (null), a string, or a list of strings"
            )
            return False

        og_text_regex_match = match_config.get("og_text_regex")
        if not (og_text_regex_match is None or isinstance(og_text_regex_match, str)):
            logger.error(f"invalid rule '{rule_name_for_log}': match.og_text_regex must be a string or empty (null)")
            return False

        ai_text_regex_match = match_config.get("ai_text_regex")
        if not (ai_text_regex_match is None or isinstance(ai_text_regex_match, str)):
            logger.error(f"invalid rule '{rule_name_for_log}': match.ai_text_regex must be a string or empty (null)")
            return False

        notify_config = rule.get("notify", {})
        if (
            not isinstance(notify_config, dict)
            or "destinations" not in notify_config
            or "send_og_text" not in notify_config
            or "send_ai_text" not in notify_config
        ):
            logger.error(
                f"invalid rule '{rule_name_for_log}': notify must contain destinations, send_og_text, and send_ai_text"
            )
            return False

        destinations = notify_config.get("destinations")
        if destinations is None:
            notify_config["destinations"] = []
        elif isinstance(destinations, str):
            notify_config["destinations"] = [] if not destinations else [destinations]
        elif isinstance(destinations, list):
            if not all(isinstance(item, str) for item in destinations):
                logger.error(f"invalid rule '{rule_name_for_log}': all items in destinations list must be strings")
                return False
        else:
            logger.error(
                f"invalid rule '{rule_name_for_log}': destinations must be empty (null), a string, or a list of strings"
            )
            return False

        for msg_type in ["send_og_text", "send_ai_text"]:
            msg_config = notify_config.get(msg_type, {})
            if not isinstance(msg_config, dict) or "enabled" not in msg_config:
                logger.error(
                    f"invalid rule '{rule_name_for_log}': {msg_type} must be a dictionary and contain enabled field"
                )
                return False

            for field_name in ["og_text_regex", "ai_text_regex"]:
                if field_name not in msg_config:
                    logger.error(f"invalid rule '{rule_name_for_log}': {msg_type} must contain {field_name} field")
                    return False
                field_value = msg_config.get(field_name)
                if not (field_value is None or isinstance(field_value, str)):
                    logger.error(
                        f"invalid rule '{rule_name_for_log}': {msg_type}.{field_name} must be a string or empty (null)"
                        f" found type: {type(field_value)}"
                    )
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

        if "ollama" in ai and not isinstance(ai.get("ollama", {}), dict):
            logger.error("invalid config: ollama section must be a dictionary")
            return False

        if "ollama" in ai and ("url" not in ai.get("ollama", {}) or "model" not in ai.get("ollama", {})):
            logger.error("invalid config: ollama section must have url and model fields")
            return False

        rules = config.get("rules", [])
        if not isinstance(rules, list):
            logger.error("invalid config: rules section must be a list")
            return False

        rule_names = set()
        for rule_idx, rule in enumerate(rules):
            rule_name = rule.get("name")
            if rule_name in rule_names:
                logger.error(f"invalid config: duplicate rule name '{rule_name}' found")
                return False
            rule_names.add(rule_name)

            if not self.validate_rule(rule):
                logger.error(
                    f"invalid config: validation failed for rule index {rule_idx} (name: {rule.get('name', 'unnamed')})"
                )
                return False

        destinations_config = config.get("destinations", [])
        if not isinstance(destinations_config, list):
            logger.error("invalid config: destinations section must be a list")
            return False

        dest_names = set()
        for dest_idx, destination in enumerate(destinations_config):
            if not isinstance(destination, dict):
                logger.error(f"invalid config: destination at index {dest_idx} must be a dictionary")
                return False

            dest_name = destination.get("name")
            if dest_name in dest_names:
                logger.error(f"invalid config: duplicate destination name '{dest_name}' found")
                return False
            dest_names.add(dest_name)

            required_dest_fields = ["name", "url", "enabled"]
            for field in required_dest_fields:
                if field not in destination:
                    logger.error(
                        f"invalid config: destination at index {dest_idx} (name: {destination.get('name', 'unnamed')})"
                        f" must have {field} field"
                    )
                    return False
        return True

    def update_config(self, new_config: Dict[str, Any]) -> bool:
        if self.validate_config(new_config):
            self.config_data = new_config
            return self.save()
        else:
            logger.error("invalid configuration detected, keeping previous configuration")
            return False
