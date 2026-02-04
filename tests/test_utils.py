"""Unit tests for utils.py module."""

from bitvoker.utils import truncate


class TestTruncate:
    """Test cases for truncate function."""

    def test_truncate_short_text(self):
        """Test truncating text that is shorter than max_length."""
        text = "Short text"
        result = truncate(text, max_length=80)
        assert result == "Short text"

    def test_truncate_long_text(self):
        """Test truncating text that exceeds max_length."""
        text = "This is a very long text that should be truncated because it exceeds the maximum length"
        result = truncate(text, max_length=50)
        assert len(result) <= 50
        assert result.endswith("...")

    def test_truncate_exact_length(self):
        """Test truncating text that is exactly max_length."""
        text = "a" * 80
        result = truncate(text, max_length=80)
        assert result == text

    def test_truncate_with_newlines(self):
        """Test truncating text with newlines (default behavior)."""
        text = "Line 1\nLine 2\nLine 3"
        result = truncate(text, max_length=80, preserve_newlines=False)
        assert "\n" not in result
        assert result == "Line 1 Line 2 Line 3"

    def test_truncate_preserve_newlines(self):
        """Test truncating text while preserving newlines."""
        text = "Line 1\nLine 2\nLine 3"
        result = truncate(text, max_length=80, preserve_newlines=True)
        assert result == text

    def test_truncate_custom_suffix(self):
        """Test truncating with custom suffix."""
        text = "This is a very long text that should be truncated"
        result = truncate(text, max_length=30, suffix="[...]")
        assert result.endswith("[...]")
        assert len(result) <= 30

    def test_truncate_empty_text(self):
        """Test truncating empty text."""
        result = truncate("", max_length=80)
        assert result == ""

    def test_truncate_with_leading_trailing_whitespace(self):
        """Test truncating text with leading/trailing whitespace."""
        text = "  Text with spaces  "
        result = truncate(text, max_length=80, preserve_newlines=False)
        assert result == "Text with spaces"

    def test_truncate_zero_max_length(self):
        """Test truncating with zero max_length."""
        text = "Some text"
        result = truncate(text, max_length=3)
        assert result == "..."
