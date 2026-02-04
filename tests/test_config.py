"""Unit tests for config.py module."""

import os
import tempfile
import yaml
import pytest
from bitvoker.config import Config


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def sample_config():
    """Return a sample valid configuration."""
    return {
        "ai": {"provider": "ollama", "ollama": {"url": "http://localhost:11434", "model": "gemma:2b"}},
        "rules": [
            {
                "name": "default-rule",
                "enabled": True,
                "preprompt": "Summarize",
                "match": {"sources": [], "og_text_regex": "", "ai_text_regex": ""},
                "notify": {
                    "destinations": [],
                    "send_og_text": {"enabled": True, "og_text_regex": "", "ai_text_regex": ""},
                    "send_ai_text": {"enabled": False, "og_text_regex": "", "ai_text_regex": ""},
                },
            }
        ],
        "destinations": [{"name": "Test", "url": "apprise://test", "enabled": True}],
    }


class TestConfig:
    """Test cases for Config class."""

    def test_init_with_nonexistent_file(self, temp_config_file):
        """Test Config initialization with non-existent file."""
        os.remove(temp_config_file)
        config = Config(temp_config_file)
        assert config.config_data == {}

    def test_init_with_existing_file(self, temp_config_file, sample_config):
        """Test Config initialization with existing file."""
        with open(temp_config_file, "w") as f:
            yaml.safe_dump(sample_config, f)
        config = Config(temp_config_file)
        assert config.config_data == sample_config

    def test_load_config(self, temp_config_file, sample_config):
        """Test loading configuration from file."""
        with open(temp_config_file, "w") as f:
            yaml.safe_dump(sample_config, f)
        config = Config(temp_config_file)
        config.load_config()
        assert config.config_data == sample_config

    def test_reload_config(self, temp_config_file, sample_config):
        """Test reloading configuration."""
        config = Config(temp_config_file)
        with open(temp_config_file, "w") as f:
            yaml.safe_dump(sample_config, f)
        reloaded = config.reload_config()
        assert reloaded == sample_config

    def test_save_config(self, temp_config_file, sample_config):
        """Test saving configuration."""
        config = Config(temp_config_file)
        config.config_data = sample_config
        assert config.save() is True
        with open(temp_config_file, "r") as f:
            saved = yaml.safe_load(f)
        assert saved == sample_config

    def test_get_ai_config(self, temp_config_file, sample_config):
        """Test getting AI configuration."""
        config = Config(temp_config_file)
        config.config_data = sample_config
        ai_config = config.get_ai_config()
        assert ai_config == sample_config["ai"]

    def test_get_rules(self, temp_config_file, sample_config):
        """Test getting rules."""
        config = Config(temp_config_file)
        config.config_data = sample_config
        rules = config.get_rules()
        assert rules == sample_config["rules"]

    def test_get_destinations(self, temp_config_file, sample_config):
        """Test getting destinations."""
        config = Config(temp_config_file)
        config.config_data = sample_config
        destinations = config.get_destinations()
        assert destinations == sample_config["destinations"]

    def test_get_enabled_destinations(self, temp_config_file, sample_config):
        """Test getting enabled destinations only."""
        config = Config(temp_config_file)
        config.config_data = sample_config
        enabled = config.get_enabled_destinations()
        assert len(enabled) == 1
        assert enabled[0]["name"] == "Test"

    def test_get_enabled_rules(self, temp_config_file, sample_config):
        """Test getting enabled rules only."""
        config = Config(temp_config_file)
        config.config_data = sample_config
        enabled = config.get_enabled_rules()
        assert len(enabled) == 1
        assert enabled[0]["name"] == "default-rule"

    def test_get_default_rule(self, temp_config_file, sample_config):
        """Test getting default rule."""
        config = Config(temp_config_file)
        config.config_data = sample_config
        default_rule = config.get_default_rule()
        assert default_rule is not None
        assert default_rule["name"] == "default-rule"

    def test_get_default_rule_missing(self, temp_config_file):
        """Test getting default rule when it doesn't exist."""
        config = Config(temp_config_file)
        config.config_data = {"rules": []}
        default_rule = config.get_default_rule()
        assert default_rule is None

    def test_update_specific_config(self, temp_config_file, sample_config):
        """Test updating specific config section."""
        config = Config(temp_config_file)
        config.config_data = sample_config
        result = config.update_specific_config("ai", "provider", "meta")
        assert result is True
        assert config.config_data["ai"]["provider"] == "meta"

    def test_validate_rule_valid(self, temp_config_file, sample_config):
        """Test validating a valid rule."""
        config = Config(temp_config_file)
        rule = sample_config["rules"][0]
        assert config.validate_rule(rule) is True

    def test_validate_rule_missing_field(self, temp_config_file):
        """Test validating a rule with missing field."""
        config = Config(temp_config_file)
        rule = {"name": "test", "enabled": True}
        assert config.validate_rule(rule) is False

    def test_validate_rule_invalid_sources(self, temp_config_file, sample_config):
        """Test validating a rule with invalid sources."""
        config = Config(temp_config_file)
        rule = sample_config["rules"][0].copy()
        rule["match"]["sources"] = 123  # Invalid type
        assert config.validate_rule(rule) is False

    def test_validate_config_valid(self, temp_config_file, sample_config):
        """Test validating a valid configuration."""
        config = Config(temp_config_file)
        assert config.validate_config(sample_config) is True

    def test_validate_config_invalid_ai(self, temp_config_file, sample_config):
        """Test validating configuration with invalid AI section."""
        config = Config(temp_config_file)
        invalid_config = sample_config.copy()
        invalid_config["ai"] = "invalid"
        assert config.validate_config(invalid_config) is False

    def test_validate_config_missing_provider(self, temp_config_file, sample_config):
        """Test validating configuration with missing provider."""
        config = Config(temp_config_file)
        invalid_config = sample_config.copy()
        invalid_config["ai"] = {}
        assert config.validate_config(invalid_config) is False

    def test_validate_config_duplicate_rule_names(self, temp_config_file, sample_config):
        """Test validating configuration with duplicate rule names."""
        config = Config(temp_config_file)
        invalid_config = sample_config.copy()
        invalid_config["rules"].append(sample_config["rules"][0].copy())
        assert config.validate_config(invalid_config) is False

    def test_validate_config_duplicate_destination_names(self, temp_config_file, sample_config):
        """Test validating configuration with duplicate destination names."""
        config = Config(temp_config_file)
        invalid_config = sample_config.copy()
        invalid_config["destinations"].append(sample_config["destinations"][0].copy())
        assert config.validate_config(invalid_config) is False

    def test_update_config_valid(self, temp_config_file, sample_config):
        """Test updating configuration with valid data."""
        config = Config(temp_config_file)
        result = config.update_config(sample_config)
        assert result is True
        assert config.config_data == sample_config

    def test_update_config_invalid(self, temp_config_file):
        """Test updating configuration with invalid data."""
        config = Config(temp_config_file)
        original = config.config_data.copy()
        result = config.update_config({"invalid": "config"})
        assert result is False
        assert config.config_data == original

    def test_get_all_destinations_if_empty(self, temp_config_file, sample_config):
        """Test getting all destinations when list is empty."""
        config = Config(temp_config_file)
        config.config_data = sample_config
        destinations = config.get_all_destinations_if_empty([])
        assert len(destinations) == 1

    def test_get_all_destinations_if_empty_with_names(self, temp_config_file, sample_config):
        """Test getting specific destinations by name."""
        config = Config(temp_config_file)
        config.config_data = sample_config
        destinations = config.get_all_destinations_if_empty(["Test"])
        assert len(destinations) == 1
        assert destinations[0]["name"] == "Test"
