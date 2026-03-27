import os
import tempfile

import yaml
import pytest

from bitvoker.config import Config


@pytest.fixture
def sample_config():
    return {
        "ai": {
            "provider": "meta_ai",
            "meta_ai": {},
            "ollama": {"url": "http://localhost:11434", "model": "gemma3:1b"},
        },
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
            }
        ],
        "destinations": [
            {"name": "test-dest", "url": "json://localhost", "enabled": True},
        ],
    }


@pytest.fixture
def config_file(sample_config, tmp_path):
    config_path = tmp_path / "config.yaml"
    with open(config_path, "w") as f:
        yaml.safe_dump(sample_config, f)
    return str(config_path)


class TestConfigLoad:
    def test_load_valid_config(self, config_file):
        config = Config(config_path=config_file)
        assert config.config_data is not None
        assert config.config_data["ai"]["provider"] == "meta_ai"

    def test_load_missing_file(self, tmp_path):
        config = Config(config_path=str(tmp_path / "missing.yaml"))
        assert config.config_data == {}

    def test_reload_config(self, config_file, sample_config):
        config = Config(config_path=config_file)
        sample_config["ai"]["provider"] = "ollama"
        with open(config_file, "w") as f:
            yaml.safe_dump(sample_config, f)
        config.reload_config()
        assert config.config_data["ai"]["provider"] == "ollama"


class TestConfigGetters:
    def test_get_ai_config(self, config_file):
        config = Config(config_path=config_file)
        ai = config.get_ai_config()
        assert ai["provider"] == "meta_ai"

    def test_get_rules(self, config_file):
        config = Config(config_path=config_file)
        rules = config.get_rules()
        assert len(rules) == 1
        assert rules[0]["name"] == "default-rule"

    def test_get_destinations(self, config_file):
        config = Config(config_path=config_file)
        dests = config.get_destinations()
        assert len(dests) == 1

    def test_get_enabled_destinations(self, config_file, sample_config):
        sample_config["destinations"].append({"name": "disabled", "url": "json://x", "enabled": False})
        with open(config_file, "w") as f:
            yaml.safe_dump(sample_config, f)
        config = Config(config_path=config_file)
        enabled = config.get_enabled_destinations()
        assert len(enabled) == 1
        assert enabled[0]["name"] == "test-dest"

    def test_get_enabled_rules(self, config_file, sample_config):
        sample_config["rules"].append({
            "name": "disabled-rule",
            "enabled": False,
            "preprompt": "",
            "match": {"sources": [], "og_text_regex": None, "ai_text_regex": None},
            "notify": {
                "destinations": [],
                "send_og_text": {"enabled": False, "og_text_regex": None, "ai_text_regex": None},
                "send_ai_text": {"enabled": False, "og_text_regex": None, "ai_text_regex": None},
            },
        })
        with open(config_file, "w") as f:
            yaml.safe_dump(sample_config, f)
        config = Config(config_path=config_file)
        enabled = config.get_enabled_rules()
        assert len(enabled) == 1

    def test_get_default_rule(self, config_file):
        config = Config(config_path=config_file)
        default = config.get_default_rule()
        assert default is not None
        assert default["name"] == "default-rule"


class TestConfigValidation:
    def test_validate_valid_config(self, config_file, sample_config):
        config = Config(config_path=config_file)
        assert config.validate_config(sample_config) is True

    def test_validate_invalid_root(self, config_file):
        config = Config(config_path=config_file)
        assert config.validate_config("not a dict") is False

    def test_validate_missing_ai_provider(self, config_file, sample_config):
        del sample_config["ai"]["provider"]
        config = Config(config_path=config_file)
        assert config.validate_config(sample_config) is False

    def test_validate_duplicate_rule_names(self, config_file, sample_config):
        sample_config["rules"].append(sample_config["rules"][0].copy())
        config = Config(config_path=config_file)
        assert config.validate_config(sample_config) is False

    def test_validate_duplicate_destination_names(self, config_file, sample_config):
        sample_config["destinations"].append(sample_config["destinations"][0].copy())
        config = Config(config_path=config_file)
        assert config.validate_config(sample_config) is False

    def test_validate_invalid_message_token(self, config_file, sample_config):
        sample_config["message_token"] = 123
        config = Config(config_path=config_file)
        assert config.validate_config(sample_config) is False

    def test_validate_rule_missing_fields(self, config_file):
        config = Config(config_path=config_file)
        assert config.validate_rule({"name": "incomplete"}) is False

    def test_validate_rule_invalid_sources(self, config_file, sample_config):
        sample_config["rules"][0]["match"]["sources"] = 123
        config = Config(config_path=config_file)
        assert config.validate_rule(sample_config["rules"][0]) is False


class TestConfigSave:
    def test_save_config(self, config_file):
        config = Config(config_path=config_file)
        config.config_data["ai"]["provider"] = "ollama"
        assert config.save() is True
        reloaded = Config(config_path=config_file)
        assert reloaded.config_data["ai"]["provider"] == "ollama"

    def test_update_config(self, config_file, sample_config):
        config = Config(config_path=config_file)
        assert config.update_config(sample_config) is True

    def test_update_invalid_config(self, config_file):
        config = Config(config_path=config_file)
        assert config.update_config({"invalid": True}) is False
