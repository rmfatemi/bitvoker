import re
import apprise
from typing import Dict, Any, Optional, List

from bitvoker.config import Config
from bitvoker.logger import setup_logger
from bitvoker.ai import process_with_ai

logger = setup_logger("alert")


class AlertResult:
    def __init__(self):
        self.original_text = ""
        self.ai_processed = ""
        self.destinations = []
        self.should_send_original = False
        self.should_send_ai = False
        self.source = ""
        self.matched_rule_name = ""


class Alert:
    def __init__(self, config: Config):
        self.config = config
        self.apprise = apprise.Apprise()
        self._setup_notification_channels()

    def _setup_notification_channels(self):
        self.apprise.clear()
        for channel in self.config.get_enabled_channels():
            try:
                if channel.get("url"):
                    self.apprise.add(channel["url"])
                    logger.debug(f"added notification channel: {channel['name']}")
            except Exception as e:
                logger.error(f"failed to add channel {channel.get('name', 'unknown')}: {str(e)}")

    def process(self, source: str, text: str) -> Optional[AlertResult]:
        if not text or not source:
            return None

        matched_rule = self._find_matching_rule(source, text)
        if not matched_rule:
            logger.debug(f"no matching rule found for source: {source}")
            return None

        result = AlertResult()
        result.original_text = text
        result.source = source
        result.matched_rule_name = matched_rule.get("name", "unnamed")

        if self._should_process_with_ai(matched_rule):
            result.ai_processed = self._get_ai_processed(text, matched_rule.get("preprompt", ""))

        notify_config = matched_rule.get("notify", {})
        result.should_send_original = self._should_send_original(notify_config, text)
        result.should_send_ai = result.ai_processed and self._should_send_ai_processed(
            notify_config, result.ai_processed
        )

        result.destinations = notify_config.get("destinations", [])

        return result

    def _find_matching_rule(self, source: str, text: str) -> Optional[Dict[str, Any]]:
        for rule in self.config.get_enabled_rules():
            match_config = rule.get("match", {})

            if match_config.get("source") and match_config["source"] != source:
                continue

            og_regex = match_config.get("og_text_regex", "")
            if og_regex and not re.search(og_regex, text, re.DOTALL | re.IGNORECASE):
                continue

            return rule

        return None

    def _should_process_with_ai(self, rule: Dict[str, Any]) -> bool:
        ai_config = self.config.get_ai_config()
        if not ai_config.get("enabled", False):
            return False

        notify_config = rule.get("notify", {})
        ai_processed_config = notify_config.get("ai_processed", {})

        return ai_processed_config.get("enabled", False)

    def _get_ai_processed(self, text: str, preprompt: str) -> Optional[str]:
        try:
            return process_with_ai(text, preprompt, self.config.get_ai_config())
        except Exception as e:
            logger.error(f"ai processing failed: {str(e)}")
            return None

    def _should_send_original(self, notify_config: Dict[str, Any], text: str) -> bool:
        original_config = notify_config.get("original_message", {})
        if not original_config.get("enabled", False):
            return False

        match_regex = original_config.get("match_regex", "")
        if match_regex and not re.search(match_regex, text, re.DOTALL | re.IGNORECASE):
            return False

        return True

    def _should_send_ai_processed(self, notify_config: Dict[str, Any], text: str) -> bool:
        ai_config = notify_config.get("ai_processed", {})
        if not ai_config.get("enabled", False):
            return False

        match_regex = ai_config.get("match_regex", "")
        if match_regex and not re.search(match_regex, text, re.DOTALL | re.IGNORECASE):
            return False

        return True

    def get_enabled_channels_by_names(self, channel_names: List[str]) -> Dict[str, Dict[str, Any]]:
        channels = {}
        for channel in self.config.get_enabled_channels():
            if channel["name"] in channel_names:
                channels[channel["name"]] = channel
        return channels
