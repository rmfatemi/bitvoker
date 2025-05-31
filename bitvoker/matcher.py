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
            logger.debug("empty sources list - matching all sources")
            return True

        if client_source in rule_source_list:
            return True

        for src_item in rule_source_list:
            if not src_item:
                continue
            try:
                ips = socket.gethostbyname_ex(src_item)[2]
                if client_source in ips:
                    logger.debug(
                        f"hostname translation successful: '{src_item}' resolved to {ips}, matched client ip"
                        f" {client_source}"
                    )
                    return True
            except (socket.gaierror, socket.herror):
                logger.debug(f"hostname translation failed: could not resolve '{src_item}' to ip address, skipping")
                continue
        return False

    def _find_matching_rule(self, source: str, text: str) -> Optional[Dict[str, Any]]:
        matching_rules = []

        for rule in self.config.get_enabled_rules():
            rule_name_for_log = rule.get("name", "unnamed_rule")
            match_config = rule.get("match", {})

            source_list = match_config.get("sources", [])
            if not self._is_source_match(source, source_list):
                logger.debug(
                    f"rule '{rule_name_for_log}' rejected: source '{source}' not in rule's sources list {source_list}"
                )
                continue

            og_regex = match_config.get("og_text_regex", "")
            if og_regex and not re.search(og_regex, text, re.DOTALL | re.IGNORECASE):
                logger.debug(
                    f"rule '{rule_name_for_log}' rejected: original text does not match og_text_regex '{og_regex}'"
                )
                continue

            ai_regex_in_match = match_config.get("ai_text_regex", "")

            specificity = 0
            if source_list:
                specificity += 1
            if og_regex:
                specificity += 2
            if ai_regex_in_match:
                specificity += 1

            matching_rules.append((rule, specificity))

        matching_rules.sort(key=lambda x: x[1], reverse=True)

        if matching_rules:
            logger.debug(f"matched rule '{matching_rules[0][0].get('name')}' with specificity {matching_rules[0][1]}")
            return matching_rules[0][0]

        logger.debug("no matching rule found after evaluating all enabled rules")
        return None

    def _should_process_with_ai(self, rule: Dict[str, Any]) -> bool:
        ai_config = self.config.get_ai_config()
        if not ai_config or not ai_config.get("provider"):
            logger.warning("ai processing disabled - ai_config is empty or provider not set")
            return False

        match_config = rule.get("match", {})
        ai_text_regex_in_match = match_config.get("ai_text_regex", "")
        notify_config = rule.get("notify", {})
        send_ai_text_config = notify_config.get("send_ai_text", {})
        send_ai_text_enabled = send_ai_text_config.get("enabled", False)

        should_process_ai = bool(ai_text_regex_in_match) or send_ai_text_enabled
        logger.debug(
            f"ai processing decision for rule '{rule.get('name')}': {should_process_ai} (ai_text_regex_in_match:"
            f" {bool(ai_text_regex_in_match)}, send_ai_text_enabled: {send_ai_text_enabled})"
        )
        return should_process_ai

    def _get_ai_processed(self, text: str, preprompt: str) -> Optional[str]:
        try:
            return process_with_ai(text, preprompt, self.config.get_ai_config())
        except Exception as e:
            logger.error(f"ai processing failed: {str(e)}")
            return None

    def _should_send_message(
        self, config_section: Dict[str, Any], original_text: str, ai_text: Optional[str] = None
    ) -> bool:
        if not config_section.get("enabled", False):
            return False

        og_text_regex = config_section.get("og_text_regex", "")
        if og_text_regex and not re.search(og_text_regex, original_text, re.DOTALL | re.IGNORECASE):
            return False

        ai_text_regex = config_section.get("ai_text_regex", "")
        if ai_text_regex:
            if ai_text is None:
                return False
            if not re.search(ai_text_regex, ai_text, re.DOTALL | re.IGNORECASE):
                return False
        return True

    def _should_send_original(self, notify_config: Dict[str, Any], text: str, ai_text: Optional[str] = None) -> bool:
        return self._should_send_message(notify_config.get("send_og_text", {}), text, ai_text)

    def _should_send_ai_processed(self, notify_config: Dict[str, Any], text: str, ai_text: str) -> bool:
        return self._should_send_message(notify_config.get("send_ai_text", {}), text, ai_text)

    def get_enabled_destinations_by_names(self, destination_names: List[str]) -> Dict[str, Dict[str, Any]]:
        destinations = {}
        enabled_destinations_from_config = self.config.get_enabled_destinations()
        for dest_name in destination_names:
            for conf_dest in enabled_destinations_from_config:
                if conf_dest["name"] == dest_name:
                    destinations[dest_name] = conf_dest
                    break
        return destinations

    def process(self, source: str, text: str) -> Optional[MatchResults]:
        if not text or not source:
            logger.debug("processing aborted: empty text or source")
            return None

        matched_rule = self._find_matching_rule(source, text)
        if not matched_rule:
            logger.debug(f"no matching rule found for source: {source} and text snippet: {text[:100]}")
            return None

        rule_name = matched_rule.get("name", "unnamed_rule")
        logger.info(f"rule '{rule_name}' matched for source: {source}")

        result = MatchResults()
        result.original_text = text
        result.source = source
        result.matched_rule_name = rule_name
        result.ai_processed = None

        if self._should_process_with_ai(matched_rule):
            ai_output = self._get_ai_processed(text, matched_rule.get("preprompt", ""))
            if ai_output is not None:
                result.ai_processed = ai_output
            else:
                logger.warning(f"ai processing returned none for rule '{rule_name}'")

            match_config = matched_rule.get("match", {})
            ai_text_regex_in_match = match_config.get("ai_text_regex", "")
            if ai_text_regex_in_match:
                if result.ai_processed is None:
                    logger.debug(
                        f"rule '{rule_name}' rejected: ai_text_regex ('{ai_text_regex_in_match}') set in match"
                        " conditions, but ai_processed text is not available"
                    )
                    return None
                if not re.search(ai_text_regex_in_match, result.ai_processed, re.DOTALL | re.IGNORECASE):
                    logger.debug(
                        f"rule '{rule_name}' rejected: ai processed text does not match ai_text_regex"
                        f" ('{ai_text_regex_in_match}') in match conditions"
                    )
                    return None

        notify_config = matched_rule.get("notify", {})
        result.should_send_original = self._should_send_original(notify_config, text, result.ai_processed)

        if result.ai_processed is not None:
            result.should_send_ai = self._should_send_ai_processed(notify_config, text, result.ai_processed)
        else:
            result.should_send_ai = False

        dest_list_names = notify_config.get("destinations", [])
        if not dest_list_names:
            logger.debug(
                f"rule '{rule_name}': empty destinations array in rule - will send to all configured and enabled global"
                " destinations"
            )
            dest_list_names = [d["name"] for d in self.config.get_enabled_destinations()]

        result.destinations = dest_list_names

        logger.debug(f"rule '{rule_name}': using destination names: {result.destinations}")
        logger.debug(
            f"rule '{rule_name}': should_send_original={result.should_send_original},"
            f" should_send_ai={result.should_send_ai}"
        )

        if not result.should_send_original and not result.should_send_ai:
            logger.info(
                f"rule '{rule_name}': no content to send (original and ai text sending disabled or conditions not met)"
            )
            return None

        return result
