"""Tests for Foreman MCP Server."""

import os
import pytest
from unittest.mock import patch, MagicMock

# Add src to path for testing
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from foreman_mcp_server.server import get_foreman_config


def test_get_foreman_config_success():
    """Test successful configuration retrieval."""
    with patch.dict(os.environ, {
        'FOREMAN_URL': 'https://foreman.example.com',
        'FOREMAN_USERNAME': 'testuser',
        'FOREMAN_PASSWORD': 'testpass',
        'FOREMAN_VERIFY_SSL': 'false'
    }):
        config = get_foreman_config()
        assert config['base_url'] == 'https://foreman.example.com'
        assert config['verify_ssl'] is False


def test_get_foreman_config_missing_url():
    """Test configuration with missing URL."""
    with patch.dict(os.environ, {
        'FOREMAN_USERNAME': 'testuser',
        'FOREMAN_PASSWORD': 'testpass'
    }, clear=True):
        with pytest.raises(ValueError, match="FOREMAN_URL environment variable is required"):
            get_foreman_config()


def test_get_foreman_config_missing_credentials():
    """Test configuration with missing credentials."""
    with patch.dict(os.environ, {
        'FOREMAN_URL': 'https://foreman.example.com'
    }, clear=True):
        with pytest.raises(ValueError, match="FOREMAN_USERNAME and FOREMAN_PASSWORD"):
            get_foreman_config()


def test_get_foreman_config_default_ssl():
    """Test configuration with default SSL verification."""
    with patch.dict(os.environ, {
        'FOREMAN_URL': 'https://foreman.example.com',
        'FOREMAN_USERNAME': 'testuser',
        'FOREMAN_PASSWORD': 'testpass'
    }):
        config = get_foreman_config()
        assert config['verify_ssl'] is True
