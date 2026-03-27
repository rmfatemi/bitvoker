import pytest
from unittest.mock import MagicMock, patch

from bitvoker.config import Config
from bitvoker.matcher import Match, MatchResults


@pytest.fixture
def base_config(tmp_path):
    import yaml
    config_data = {
        "ai": {"provider": "meta_ai", "meta_ai": {}, "ollama": {"url": "http://localhost:11434", "model": "gemma3:1b"}},
        "message_token": "",
        "rules": [
            {
                "name": "default-rule",
                "enabled": True,
                "preprompt": "analyze this",
                "match": {"sources": [], "og_text_regex": None, "ai_text_regex": None},
                "notify": {
                    "destinations": [],
                    "send_og_text": {"enabled": True, "og_text_regex": None, "ai_text_regex": None},
                    "send_ai_text": {"enabled": False, "og_text_regex": None, "ai_text_regex": None},
                },
            },
        ],
        "destinations": [{"name": "test-dest", "url": "json://localhost", "enabled": True}],
    }
    config_path = tmp_path / "config.yaml"
    with open(config_path, "w") as f:
        yaml.safe_dump(config_data, f)
    return Config(config_path=str(config_path))


class TestSourceMatch:
    def test_empty_sources_matches_all(self, base_config):
        match = Match(base_config)
        assert match._is_source_match("192.168.1.1", []) is True

    def test_exact_ip_match(self, base_config):
        match = Match(base_config)
        assert match._is_source_match("192.168.1.1", ["192.168.1.1"]) is True

    def test_ip_not_in_list(self, base_config):
        match = Match(base_config)
        assert match._is_source_match("10.0.0.1", ["192.168.1.1"]) is False


class TestFindMatchingRule:
    def test_default_rule_matches_everything(self, base_config):
        match = Match(base_config)
        rule = match._find_matching_rule("10.0.0.1", "test message")
        assert rule is not None
        assert rule["name"] == "default-rule"

    def test_no_match_when_all_disabled(self, base_config):
        for rule in base_config.config_data["rules"]:
            rule["enabled"] = False
        match = Match(base_config)
        assert match._find_matching_rule("10.0.0.1", "test") is None

    def test_specific_rule_wins_over_default(self, base_config):
        base_config.config_data["rules"].append({
            "name": "specific-rule",
            "enabled": True,
            "preprompt": "",
            "match": {"sources": ["10.0.0.1"], "og_text_regex": "error", "ai_text_regex": None},
            "notify": {
                "destinations": [],
                "send_og_text": {"enabled": True, "og_text_regex": None, "ai_text_regex": None},
                "send_ai_text": {"enabled": False, "og_text_regex": None, "ai_text_regex": None},
            },
        })
        match = Match(base_config)
        rule = match._find_matching_rule("10.0.0.1", "there was an error")
        assert rule["name"] == "specific-rule"

    def test_regex_match(self, base_config):
        base_config.config_data["rules"][0]["match"]["og_text_regex"] = "CRITICAL"
        match = Match(base_config)
        assert match._find_matching_rule("10.0.0.1", "CRITICAL error") is not None
        assert match._find_matching_rule("10.0.0.1", "normal log") is None


class TestProcess:
    def test_empty_text_returns_none(self, base_config):
        match = Match(base_config)
        assert match.process("10.0.0.1", "") is None

    def test_empty_source_returns_none(self, base_config):
        match = Match(base_config)
        assert match.process("", "test message") is None

    def test_basic_process_returns_result(self, base_config):
        match = Match(base_config)
        result = match.process("10.0.0.1", "test message")
        assert result is not None
        assert result.original_text == "test message"
        assert result.should_send_original is True
        assert result.should_send_ai is False

    def test_no_content_to_send_returns_none(self, base_config):
        base_config.config_data["rules"][0]["notify"]["send_og_text"]["enabled"] = False
        match = Match(base_config)
        assert match.process("10.0.0.1", "test") is None


class TestMatchResults:
    def test_default_values(self):
        result = MatchResults()
        assert result.source == ""
        assert result.destinations == []
        assert result.ai_processed == ""
        assert result.original_text == ""
        assert result.should_send_ai is False
        assert result.should_send_original is False
