from bitvoker.utils import truncate


class TestTruncate:
    def test_short_text_unchanged(self):
        assert truncate("hello", 80) == "hello"

    def test_long_text_truncated(self):
        text = "a" * 100
        result = truncate(text, 80)
        assert len(result) == 80
        assert result.endswith("...")

    def test_preserves_newlines_disabled(self):
        result = truncate("line1\nline2\nline3", 80)
        assert "\n" not in result

    def test_preserves_newlines_enabled(self):
        result = truncate("line1\nline2\nline3", 80, preserve_newlines=True)
        assert "\n" in result

    def test_custom_suffix(self):
        text = "a" * 100
        result = truncate(text, 20, suffix="[...]")
        assert result.endswith("[...]")
        assert len(result) == 20

    def test_empty_string(self):
        assert truncate("", 80) == ""

    def test_exact_length(self):
        text = "a" * 80
        assert truncate(text, 80) == text
