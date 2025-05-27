import re
import socket

from typing import Dict, Any, Optional, List

from bitvoker.config import Config
from bitvoker.logger import setup_logger
from bitvoker.ai import process_with_ai


logger = setup_logger("matcher")


class MatchResults:
    def __init__(self):
        self.source = ""
        self.destinations = []
        self.ai_processed = ""
        self.original_text = ""
        self.matched_rule_name = ""
        self.should_send_ai = False
        self.should_send_original = False


class Match:
    def __init__(self, config: Config):
        self.config = config

    def _is_source_match(self, client_source: str, rule_source_list: List[str]) -> bool:
        if not rule_source_list:
            return True

        if client_source in rule_source_list:
            return True

        for src in rule_source_list:
            try:
                ips = socket.gethostbyname_ex(src)[2]
                if client_source in ips:
                    logger.debug(
                        f"hostname translation successful: '{src}' resolved to {ips}, matched client ip {client_source}"
                    )
                    return True
            except (socket.gaierror, socket.herror):
                logger.debug(f"hostname translation failed: could not resolve '{src}' to ip address, skipping")
                continue
        return False

    def _find_matching_rule(self, source: str, text: str) -> Optional[Dict[str, Any]]:
        matching_rules = []

        for rule in self.config.get_enabled_rules():
            match_config = rule.get("match", {})

            source_list = match_config.get("source", [])
            if not self._is_source_match(source, source_list):
                continue

            og_regex = match_config.get("og_text_regex", "")
            if og_regex and not re.search(og_regex, text, re.DOTALL | re.IGNORECASE):
                continue

            specificity = 0
            if match_config.get("source"):
                specificity += 1
            if match_config.get("og_text_regex"):
                specificity += 2
            if match_config.get("ai_text_regex"):
                specificity += 1

            matching_rules.append((rule, specificity))

        matching_rules.sort(key=lambda x: x[1], reverse=True)

        return matching_rules[0][0] if matching_rules else None

    def _should_process_with_ai(self, rule: Dict[str, Any]) -> bool:
        ai_config = self.config.get_ai_config()
        if not ai_config:
            logger.warning(f"ai processing disabled - ai_config is empty or None: {ai_config}")
            return False

        notify_config = rule.get("notify", {})
        ai_processed_config = notify_config.get("ai_processed", {})

        ai_enabled = ai_processed_config.get("enabled", False)
        logger.debug(f"ai processing enabled: {ai_enabled} for rule: {rule.get('name')}")
        return ai_enabled

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

    def get_enabled_destinations_by_names(self, destination_names: List[str]) -> Dict[str, Dict[str, Any]]:
        destinations = {}
        for destination in self.config.get_enabled_destinations():
            if destination["name"] in destination_names:
                destinations[destination["name"]] = destination
        return destinations

    def process(self, source: str, text: str) -> Optional[MatchResults]:
        if not text or not source:
            return None

        matched_rule = self._find_matching_rule(source, text)
        if not matched_rule:
            logger.debug(f"no matching rule found for source: {source}")
            return None

        logger.info(f"rule '{matched_rule.get('name')}' matched for source: {source}")

        result = MatchResults()
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

        dest_list = notify_config.get("destinations", [])

        if not dest_list:
            logger.debug("empty destinations array - will send to all enabled destinations")
            dest_list = [d["name"] for d in self.config.get_enabled_destinations()]

        result.destinations = dest_list

        logger.debug(f"rule {result.matched_rule_name}: using destinations: {result.destinations}")
        logger.debug(
            f"rule {result.matched_rule_name}: should_send_original={result.should_send_original},"
            f" should_send_ai={result.should_send_ai}"
        )

        return result
