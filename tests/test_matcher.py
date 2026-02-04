"""Unit tests for matcher.py module."""

import pytest
from unittest.mock import Mock, patch
from bitvoker.matcher import Match, MatchResults
from bitvoker.config import Config


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    config = Mock(spec=Config)
    config.get_ai_config.return_value = {"provider": "ollama"}
    config.get_enabled_rules.return_value = [
        {
            "name": "test-rule",
            "enabled": True,
            "preprompt": "Summarize",
            "match": {
                "sources": ["192.168.1.1"],
                "og_text_regex": "ERROR",
                "ai_text_regex": ""
            },
            "notify": {
                "destinations": ["Test"],
                "send_og_text": {
                    "enabled": True,
                    "og_text_regex": "",
                    "ai_text_regex": ""
                },
                "send_ai_text": {
                    "enabled": False,
                    "og_text_regex": "",
                    "ai_text_regex": ""
                }
            }
        }
    ]
    config.get_enabled_destinations.return_value = [
        {"name": "Test", "url": "apprise://test", "enabled": True}
    ]
    return config


class TestMatchResults:
    """Test cases for MatchResults class."""

    def test_init(self):
        """Test MatchResults initialization."""
        result = MatchResults()
        assert result.source == ""
        assert result.destinations == []
        assert result.ai_processed == ""
        assert result.original_text == ""
        assert result.matched_rule_name == ""
        assert result.should_send_ai is False
        assert result.should_send_original is False


class TestMatch:
    """Test cases for Match class."""

    def test_init(self, mock_config):
        """Test Match initialization."""
        matcher = Match(mock_config)
        assert matcher.config == mock_config

    def test_is_source_match_empty_list(self, mock_config):
        """Test source matching with empty source list."""
        matcher = Match(mock_config)
        assert matcher._is_source_match("192.168.1.1", []) is True

    def test_is_source_match_exact_match(self, mock_config):
        """Test source matching with exact IP match."""
        matcher = Match(mock_config)
        assert matcher._is_source_match("192.168.1.1", ["192.168.1.1"]) is True

    def test_is_source_match_no_match(self, mock_config):
        """Test source matching with no match."""
        matcher = Match(mock_config)
        assert matcher._is_source_match("192.168.1.2", ["192.168.1.1"]) is False

    @patch('socket.gethostbyname_ex')
    def test_is_source_match_hostname_resolution(self, mock_gethostbyname, mock_config):
        """Test source matching with hostname resolution."""
        mock_gethostbyname.return_value = ("test.local", [], ["192.168.1.1"])
        matcher = Match(mock_config)
        assert matcher._is_source_match("192.168.1.1", ["test.local"]) is True

    def test_find_matching_rule_no_match(self, mock_config):
        """Test finding matching rule when no rules match."""
        matcher = Match(mock_config)
        result = matcher._find_matching_rule("192.168.1.2", "INFO: All good")
        assert result is None

    def test_find_matching_rule_with_match(self, mock_config):
        """Test finding matching rule when rule matches."""
        matcher = Match(mock_config)
        result = matcher._find_matching_rule("192.168.1.1", "ERROR: Something failed")
        assert result is not None
        assert result["name"] == "test-rule"

    def test_find_matching_rule_specificity_ordering(self, mock_config):
        """Test that rules with higher specificity are preferred."""
        mock_config.get_enabled_rules.return_value = [
            {
                "name": "generic-rule",
                "enabled": True,
                "preprompt": "Summarize",
                "match": {
                    "sources": [],
                    "og_text_regex": "",
                    "ai_text_regex": ""
                },
                "notify": {
                    "destinations": [],
                    "send_og_text": {"enabled": True, "og_text_regex": "", "ai_text_regex": ""},
                    "send_ai_text": {"enabled": False, "og_text_regex": "", "ai_text_regex": ""}
                }
            },
            {
                "name": "specific-rule",
                "enabled": True,
                "preprompt": "Summarize",
                "match": {
                    "sources": ["192.168.1.1"],
                    "og_text_regex": "ERROR",
                    "ai_text_regex": ""
                },
                "notify": {
                    "destinations": [],
                    "send_og_text": {"enabled": True, "og_text_regex": "", "ai_text_regex": ""},
                    "send_ai_text": {"enabled": False, "og_text_regex": "", "ai_text_regex": ""}
                }
            }
        ]
        matcher = Match(mock_config)
        result = matcher._find_matching_rule("192.168.1.1", "ERROR: Something failed")
        assert result["name"] == "specific-rule"

    def test_should_process_with_ai_no_config(self, mock_config):
        """Test AI processing decision when no AI config."""
        mock_config.get_ai_config.return_value = {}
        matcher = Match(mock_config)
        rule = {"match": {"ai_text_regex": ""}, "notify": {"send_ai_text": {"enabled": False}}}
        assert matcher._should_process_with_ai(rule) is False

    def test_should_process_with_ai_enabled(self, mock_config):
        """Test AI processing decision when enabled."""
        matcher = Match(mock_config)
        rule = {"match": {"ai_text_regex": ""}, "notify": {"send_ai_text": {"enabled": True}}}
        assert matcher._should_process_with_ai(rule) is True

    def test_should_send_message_enabled(self, mock_config):
        """Test should send message when enabled."""
        matcher = Match(mock_config)
        config_section = {"enabled": True, "og_text_regex": "", "ai_text_regex": ""}
        assert matcher._should_send_message(config_section, "test text") is True

    def test_should_send_message_disabled(self, mock_config):
        """Test should send message when disabled."""
        matcher = Match(mock_config)
        config_section = {"enabled": False, "og_text_regex": "", "ai_text_regex": ""}
        assert matcher._should_send_message(config_section, "test text") is False

    def test_should_send_message_with_og_regex_match(self, mock_config):
        """Test should send message with matching og_text_regex."""
        matcher = Match(mock_config)
        config_section = {"enabled": True, "og_text_regex": "ERROR", "ai_text_regex": ""}
        assert matcher._should_send_message(config_section, "ERROR: Failed") is True

    def test_should_send_message_with_og_regex_no_match(self, mock_config):
        """Test should send message with non-matching og_text_regex."""
        matcher = Match(mock_config)
        config_section = {"enabled": True, "og_text_regex": "ERROR", "ai_text_regex": ""}
        assert matcher._should_send_message(config_section, "INFO: Success") is False

    def test_should_send_message_with_ai_regex_match(self, mock_config):
        """Test should send message with matching ai_text_regex."""
        matcher = Match(mock_config)
        config_section = {"enabled": True, "og_text_regex": "", "ai_text_regex": "CRITICAL"}
        assert matcher._should_send_message(config_section, "test", "CRITICAL: Issue") is True

    def test_should_send_message_with_ai_regex_no_match(self, mock_config):
        """Test should send message with non-matching ai_text_regex."""
        matcher = Match(mock_config)
        config_section = {"enabled": True, "og_text_regex": "", "ai_text_regex": "CRITICAL"}
        assert matcher._should_send_message(config_section, "test", "WARNING: Issue") is False

    def test_should_send_message_with_ai_regex_no_ai_text(self, mock_config):
        """Test should send message with ai_regex but no ai_text."""
        matcher = Match(mock_config)
        config_section = {"enabled": True, "og_text_regex": "", "ai_text_regex": "CRITICAL"}
        assert matcher._should_send_message(config_section, "test", None) is False

    def test_get_enabled_destinations_by_names(self, mock_config):
        """Test getting enabled destinations by names."""
        matcher = Match(mock_config)
        destinations = matcher.get_enabled_destinations_by_names(["Test"])
        assert "Test" in destinations
        assert destinations["Test"]["url"] == "apprise://test"

    def test_get_enabled_destinations_by_names_no_match(self, mock_config):
        """Test getting enabled destinations by names with no match."""
        matcher = Match(mock_config)
        destinations = matcher.get_enabled_destinations_by_names(["NonExistent"])
        assert destinations == {}

    def test_process_empty_text(self, mock_config):
        """Test processing with empty text."""
        matcher = Match(mock_config)
        result = matcher.process("192.168.1.1", "")
        assert result is None

    def test_process_empty_source(self, mock_config):
        """Test processing with empty source."""
        matcher = Match(mock_config)
        result = matcher.process("", "test text")
        assert result is None

    def test_process_no_matching_rule(self, mock_config):
        """Test processing when no rule matches."""
        matcher = Match(mock_config)
        result = matcher.process("192.168.1.2", "INFO: All good")
        assert result is None

    @patch('bitvoker.matcher.process_with_ai')
    def test_process_with_matching_rule(self, mock_ai, mock_config):
        """Test processing with matching rule."""
        mock_ai.return_value = None
        matcher = Match(mock_config)
        result = matcher.process("192.168.1.1", "ERROR: Something failed")
        assert result is not None
        assert result.source == "192.168.1.1"
        assert result.original_text == "ERROR: Something failed"
        assert result.matched_rule_name == "test-rule"
        assert result.should_send_original is True

    @patch('bitvoker.matcher.process_with_ai')
    def test_process_with_ai_processing(self, mock_ai, mock_config):
        """Test processing with AI enabled."""
        mock_ai.return_value = "AI processed text"
        mock_config.get_enabled_rules.return_value = [
            {
                "name": "ai-rule",
                "enabled": True,
                "preprompt": "Summarize",
                "match": {
                    "sources": ["192.168.1.1"],
                    "og_text_regex": "ERROR",
                    "ai_text_regex": ""
                },
                "notify": {
                    "destinations": ["Test"],
                    "send_og_text": {
                        "enabled": True,
                        "og_text_regex": "",
                        "ai_text_regex": ""
                    },
                    "send_ai_text": {
                        "enabled": True,
                        "og_text_regex": "",
                        "ai_text_regex": ""
                    }
                }
            }
        ]
        matcher = Match(mock_config)
        result = matcher.process("192.168.1.1", "ERROR: Something failed")
        assert result is not None
        assert result.ai_processed == "AI processed text"
        assert result.should_send_ai is True

    def test_process_no_content_to_send(self, mock_config):
        """Test processing when no content should be sent."""
        mock_config.get_enabled_rules.return_value = [
            {
                "name": "no-send-rule",
                "enabled": True,
                "preprompt": "Summarize",
                "match": {
                    "sources": ["192.168.1.1"],
                    "og_text_regex": "ERROR",
                    "ai_text_regex": ""
                },
                "notify": {
                    "destinations": ["Test"],
                    "send_og_text": {
                        "enabled": False,
                        "og_text_regex": "",
                        "ai_text_regex": ""
                    },
                    "send_ai_text": {
                        "enabled": False,
                        "og_text_regex": "",
                        "ai_text_regex": ""
                    }
                }
            }
        ]
        matcher = Match(mock_config)
        result = matcher.process("192.168.1.1", "ERROR: Something failed")
        assert result is None
