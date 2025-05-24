import re
import apprise
from typing import Dict, Any, Optional

from bitvoker.config import Config
from bitvoker.logger import setup_logger
from bitvoker.ai import process_with_ai

logger = setup_logger("alert")


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

    def process(self, source: str, text: str) -> bool:
        """Process an alert from a source with text content"""
        if not text or not source:
            return False

        matched_rule = self._find_matching_rule(source, text)
        if not matched_rule:
            logger.debug(f"no matching rule found for source: {source}")
            return False

        ai_summary = None
        if self._should_process_with_ai(matched_rule):
            ai_summary = self._get_ai_summary(text, matched_rule.get("preprompt", ""))

        self._send_notifications(matched_rule, source, text, ai_summary)
        return True

    def _find_matching_rule(self, source: str, text: str) -> Optional[Dict[str, Any]]:
        for rule in self.config.get_enabled_rules():
            match_config = rule.get("match", {})

            # check source match
            if match_config.get("source") and match_config["source"] != source:
                continue

            # check original text regex match
            og_regex = match_config.get("og_text_regex", "")
            if og_regex and not re.search(og_regex, text, re.DOTALL | re.IGNORECASE):
                continue

            # this rule matches
            return rule

        return None

    def _should_process_with_ai(self, rule: Dict[str, Any]) -> bool:
        ai_config = self.config.get_ai_config()
        if not ai_config.get("enabled", False):
            return False

        # check if ai summary is enabled for this rule's notifications
        notify_config = rule.get("notify", {})
        ai_summary_config = notify_config.get("ai_summary", {})

        return ai_summary_config.get("enabled", False)

    def _get_ai_summary(self, text: str, preprompt: str) -> Optional[str]:
        try:
            return process_with_ai(text, preprompt, self.config.get_ai_config())
        except Exception as e:
            logger.error(f"ai processing failed: {str(e)}")
            return None

    def _send_notifications(self, rule: Dict[str, Any], source: str, original_text: str, ai_summary: Optional[str]):
        notify_config = rule.get("notify", {})
        destinations = notify_config.get("destinations", [])

        if not destinations:
            logger.debug(f"no destinations for rule: {rule.get('name')}")
            return

        self._setup_notification_channels()
        channels = {}
        for channel in self.config.get_enabled_channels():
            if channel["name"] in destinations:
                channels[channel["name"]] = channel

        if not channels:
            logger.debug("no enabled channels match rule destinations")
            return

        # send original message if configured
        if self._should_send_original(notify_config, original_text):
            self._send_message(f"[{source}] {original_text[:2000]}", channels)

        # send ai summary if configured
        if ai_summary and self._should_send_ai_summary(notify_config, ai_summary):
            self._send_message(f"[{source} AI] {ai_summary[:2000]}", channels)

    def _should_send_original(self, notify_config: Dict[str, Any], text: str) -> bool:
        original_config = notify_config.get("original_message", {})
        if not original_config.get("enabled", False):
            return False

        match_regex = original_config.get("match_regex", "")
        if match_regex and not re.search(match_regex, text, re.DOTALL | re.IGNORECASE):
            return False

        return True

    def _should_send_ai_summary(self, notify_config: Dict[str, Any], text: str) -> bool:
        ai_config = notify_config.get("ai_summary", {})
        if not ai_config.get("enabled", False):
            return False

        match_regex = ai_config.get("match_regex", "")
        if match_regex and not re.search(match_regex, text, re.DOTALL | re.IGNORECASE):
            return False

        return True

    def _send_message(self, message: str, channels: Dict[str, Dict[str, Any]]):
        try:
            self.apprise.notify(body=message)
            logger.info(f"sent notification to {len(channels)} channels")
        except Exception as e:
            logger.error(f"failed to send notification: {str(e)}")
