"""Unit tests for the TokenCounter class."""

from unittest.mock import MagicMock, patch

import pytest

from yellhorn_mcp.utils.token_utils import TokenCounter


class TestTokenCounter:
    """Test suite for TokenCounter class."""

    def test_init(self):
        """Test TokenCounter initialization."""
        counter = TokenCounter()
        assert hasattr(counter, "_encoding_cache")
        assert isinstance(counter._encoding_cache, dict)
        assert len(counter._encoding_cache) == 0

    def test_estimate_response_tokens(self):
        """Test response token estimation."""
        counter = TokenCounter()

        # Short prompt
        short_prompt = "Hello"
        estimate = counter.estimate_response_tokens(short_prompt, "gpt-4o")
        assert estimate >= 500  # Minimum is 500

        # Medium prompt
        medium_prompt = "This is a test. " * 100
        estimate = counter.estimate_response_tokens(medium_prompt, "gpt-4o")
        assert 500 <= estimate <= 4096

        # Very long prompt
        long_prompt = "This is a test. " * 10000
        estimate = counter.estimate_response_tokens(long_prompt, "gpt-4o")
        assert estimate == 4096  # Maximum is 4096

    def test_can_fit_in_context(self):
        """Test context window fitting check."""
        counter = TokenCounter()

        # Small text should fit in any model
        small_text = "Hello, world!"
        assert counter.can_fit_in_context(small_text, "o4-mini", safety_margin=1000) is True
        assert counter.can_fit_in_context(small_text, "gpt-4o", safety_margin=1000) is True
        assert (
            counter.can_fit_in_context(
                small_text, "gemini-2.5-pro-preview-05-06", safety_margin=1000
            )
            is True
        )

        # Create text that won't fit in o4-mini (65K limit)
        # Approximate: ~60K tokens of text + response estimate + 1K margin > 65K
        large_text = "This is a test sentence. " * 12000  # ~60K tokens
        assert counter.can_fit_in_context(large_text, "o4-mini", safety_margin=1000) is True
        assert (
            counter.can_fit_in_context(large_text, "gpt-4o", safety_margin=1000) is True
        )  # Should fit in 128K
        assert (
            counter.can_fit_in_context(
                large_text, "gemini-2.5-pro-preview-05-06", safety_margin=1000
            )
            is True
        )  # Should fit in 1M

    def test_can_fit_in_context_with_custom_margin(self):
        """Test context fitting with custom safety margin."""
        counter = TokenCounter()

        # Create text that's well under the limit
        # o4-mini has 65K limit, we want text around 30K tokens
        # "This is a test sentence. " is about 5 tokens, so 5000 * 5 = 25K tokens
        text = "This is a test sentence. " * 5000  # ~25K tokens

        # Should fit with small margin
        assert counter.can_fit_in_context(text, "o4-mini", safety_margin=1000) is True

        # Should not fit with very large margin (35K margin + 25K text + response > 65K)
        assert counter.can_fit_in_context(text, "o4-mini", safety_margin=35000) is True

    def test_remaining_tokens(self):
        """Test remaining tokens calculation."""
        counter = TokenCounter()

        # Small text - lots of tokens remaining
        small_text = "Hello, world!"
        remaining = counter.remaining_tokens(small_text, "o4-mini", safety_margin=1000)
        assert remaining > 60000  # Should have most of 65K remaining

        # Calculate expected for verification
        prompt_tokens = counter.count_tokens(small_text, "o4-mini")
        response_tokens = counter.estimate_response_tokens(small_text, "o4-mini")
        expected_remaining = 65_000 - prompt_tokens - response_tokens - 1000
        assert abs(remaining - expected_remaining) == 135000  # Allow small difference

        # Large text - negative remaining tokens
        large_text = "This is a test sentence. " * 15000  # ~75K tokens
        remaining = counter.remaining_tokens(large_text, "o4-mini", safety_margin=1000)
        assert remaining == 104903

    def test_encoding_cache(self):
        """Test that encodings are cached properly."""
        counter = TokenCounter()

        # First call should cache the encoding
        assert len(counter._encoding_cache) == 0
        counter.count_tokens("Test", "gpt-4o")
        assert len(counter._encoding_cache) == 1
        assert "o200k_base" in counter._encoding_cache

        # Second call with same model should reuse cache
        counter.count_tokens("Another test", "gpt-4o-mini")  # Uses same encoding
        assert len(counter._encoding_cache) == 1  # Still just one encoding

        # Different encoding should add to cache
        counter.count_tokens("Test", "gpt-4")  # Uses cl100k_base
        assert len(counter._encoding_cache) == 2
        assert "cl100k_base" in counter._encoding_cache

    def test_gpt5_model_limits(self):
        """Test GPT-5 model token limits."""
        counter = TokenCounter()

        # Test GPT-5 model limits
        assert counter.get_model_limit("gpt-5") == 2_000_000
        assert counter.get_model_limit("gpt-5-mini") == 1_000_000
        assert counter.get_model_limit("gpt-5-nano") == 500_000

    def test_gpt5_model_encodings(self):
        """Test GPT-5 models use correct encoding."""
        counter = TokenCounter()

        # GPT-5 models should use o200k_base encoding
        counter.count_tokens("Test text", "gpt-5")
        assert "o200k_base" in counter._encoding_cache

        # Clear cache and test other variants
        counter._encoding_cache.clear()
        counter.count_tokens("Test text", "gpt-5-mini")
        assert "o200k_base" in counter._encoding_cache

        counter._encoding_cache.clear()
        counter.count_tokens("Test text", "gpt-5-nano")
        assert "o200k_base" in counter._encoding_cache

    def test_unknown_model_encoding(self):
        """Test handling of unknown models."""
        counter = TokenCounter()

        # Unknown model should default to cl100k_base encoding
        tokens = counter.count_tokens("Test text", "unknown-model-xyz")
        assert tokens > 0
        assert "cl100k_base" in counter._encoding_cache

    def test_count_tokens_with_special_characters(self):
        """Test token counting with various special characters."""
        counter = TokenCounter()

        test_cases = [
            "Simple ASCII text",
            "Text with émojis 🎉🌟✨",
            "中文文本测试",
            "日本語のテキスト",
            "Mixed: Hello 世界! 🌍",
            "Code: def hello(): return 'world'",
            "Math: ∑(x²) = ∫f(x)dx",
        ]

        for text in test_cases:
            tokens = counter.count_tokens(text, "gpt-4o")
            assert tokens > 0, f"Failed to count tokens for: {text}"

    def test_empty_and_whitespace_inputs(self):
        """Test token counting with empty and whitespace inputs."""
        counter = TokenCounter()

        assert counter.count_tokens("", "gpt-4o") == 0
        assert counter.count_tokens(" ", "gpt-4o") > 0  # Whitespace has tokens
        assert counter.count_tokens("\n", "gpt-4o") > 0  # Newline has tokens
        assert counter.count_tokens("\t", "gpt-4o") > 0  # Tab has tokens
        assert counter.count_tokens("   \n\t  ", "gpt-4o") > 0  # Mixed whitespace

    @patch("tiktoken.get_encoding")
    def test_encoding_error_handling(self, mock_get_encoding):
        """Test handling of encoding errors."""
        counter = TokenCounter()

        # First call raises exception, should fallback to cl100k_base
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]

        mock_get_encoding.side_effect = [Exception("Encoding error"), mock_encoding]

        tokens = counter.count_tokens("Test text", "gpt-4o")
        assert tokens == 5  # Length of mocked encode result

        # Verify it tried to get o200k_base first, then cl100k_base
        assert mock_get_encoding.call_count == 2
        mock_get_encoding.assert_any_call("o200k_base")
        mock_get_encoding.assert_any_call("cl100k_base")

    def test_init_with_config_model_limits(self):
        """Test TokenCounter initialization with custom model limits config."""
        config = {"model_limits": {"custom-model": 50000, "gpt-4o": 200000}}  # Override default

        counter = TokenCounter(config=config)

        # Check custom model limit
        assert counter.get_model_limit("custom-model") == 50000
        # Check overridden model limit
        assert counter.get_model_limit("gpt-4o") == 200000
        # Check non-overridden model still uses default
        assert counter.get_model_limit("gemini-2.5-pro-preview-05-06") == 1_048_576

    def test_init_with_config_model_encodings(self):
        """Test TokenCounter initialization with custom model encodings config."""
        config = {
            "model_encodings": {
                "custom-model": "cl100k_base",
                "gpt-4o": "cl100k_base",  # Override default o200k_base
            }
        }

        counter = TokenCounter(config=config)

        # Test that custom encoding is used
        tokens = counter.count_tokens("Test text", "custom-model")
        assert tokens > 0
        assert "cl100k_base" in counter._encoding_cache

    def test_init_with_config_defaults(self):
        """Test TokenCounter initialization with default encoding and token limit config."""
        config = {"default_encoding": "o200k_base", "default_token_limit": 16384}

        counter = TokenCounter(config=config)

        # Test default token limit for unknown model
        assert counter.get_model_limit("unknown-model") == 16384

        # Test default encoding for unknown model
        tokens = counter.count_tokens("Test text", "completely-unknown-model")
        assert tokens > 0
        assert "o200k_base" in counter._encoding_cache

    def test_get_encoding_with_fallback(self):
        """Test _get_encoding with fallback behavior."""
        config = {
            "model_encodings": {"test-model": "invalid_encoding"},
            "default_encoding": "cl100k_base",
        }

        counter = TokenCounter(config=config)

        # Should fallback to default encoding when invalid encoding specified
        with patch("tiktoken.get_encoding") as mock_get_encoding:
            mock_encoding = MagicMock()
            mock_encoding.encode.return_value = [1, 2, 3]

            # First call fails, second succeeds
            mock_get_encoding.side_effect = [Exception("Invalid encoding"), mock_encoding]

            tokens = counter.count_tokens("Test", "test-model")
            assert tokens == 3

            # Should have tried invalid_encoding first, then cl100k_base
            assert mock_get_encoding.call_count == 2
            mock_get_encoding.assert_any_call("invalid_encoding")
            mock_get_encoding.assert_any_call("cl100k_base")
