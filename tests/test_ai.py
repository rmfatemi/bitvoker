import pytest
from unittest.mock import patch, MagicMock

from bitvoker.ai import MetaAIProvider, OllamaProvider, get_provider, process_with_ai


class TestGetProvider:
    def test_meta_ai_default(self):
        provider = get_provider({"provider": "meta_ai"})
        assert isinstance(provider, MetaAIProvider)

    @patch("bitvoker.ai.OllamaProvider")
    def test_ollama_provider(self, mock_ollama):
        mock_ollama.return_value = MagicMock()
        provider = get_provider({
            "provider": "ollama",
            "ollama": {"url": "http://localhost:11434", "model": "gemma3:1b"},
        })
        mock_ollama.assert_called_once()


class TestProcessWithAi:
    def test_no_config_returns_none(self):
        assert process_with_ai("msg", "prompt", None) is None

    def test_empty_config_returns_none(self):
        assert process_with_ai("msg", "prompt", {}) is None
