"""Tests for the main BASdk class."""

from unittest.mock import patch

import pytest

from ba.ba import BASdk


class TestBASdk:
    """Test cases for BASdk."""

    def test_init_with_valid_api_key(self, mock_api_key, mock_api_url):
        """Test SDK initialization with valid API key."""
        with (
            patch("ba.ba.agents.create_agents_client") as mock_agents,
            patch("ba.ba.threads.create_threads_client") as mock_threads,
        ):
            sdk = BASdk(mock_api_key, mock_api_url)

            assert sdk._api_key == mock_api_key
            assert sdk._api_url == mock_api_url
            assert sdk.Agent is not None
            assert sdk.Thread is not None
            mock_agents.assert_called_once_with(mock_api_url, mock_api_key)
            mock_threads.assert_called_once_with(mock_api_url, mock_api_key)

    def test_init_with_empty_api_key(self, mock_api_url):
        """Test SDK initialization with empty API key raises ValueError."""
        with pytest.raises(ValueError, match="API key is required"):
            BASdk("", mock_api_url)

    def test_init_with_none_api_key(self, mock_api_url):
        """Test SDK initialization with None API key raises ValueError."""
        with pytest.raises(ValueError, match="API key is required"):
            BASdk(None, mock_api_url)

    def test_api_key_property(self, mock_sdk):
        """Test API key property returns masked key."""
        masked_key = mock_sdk.api_key
        assert len(masked_key) > 0
        assert "..." in masked_key
        assert mock_sdk._api_key not in masked_key

    def test_api_url_property(self, mock_sdk, mock_api_url):
        """Test API URL property returns correct URL."""
        assert mock_sdk.api_url == mock_api_url

    def test_default_api_url(self, mock_api_key):
        """Test SDK uses default API URL when not provided."""
        with (
            patch("ba.ba.agents.create_agents_client") as mock_agents,
            patch("ba.ba.threads.create_threads_client") as mock_threads,
        ):
            sdk = BASdk(mock_api_key)

            assert sdk._api_url == "https://belaraby.ai"
            mock_agents.assert_called_once_with("https://belaraby.ai", mock_api_key)
            mock_threads.assert_called_once_with("https://belaraby.ai", mock_api_key)
