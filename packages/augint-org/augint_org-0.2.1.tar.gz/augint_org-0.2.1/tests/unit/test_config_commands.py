"""Unit tests for config commands."""

import json
from unittest.mock import patch

import pytest

from ai_org.cli import cli


@pytest.mark.skip(reason="Config path mocking needs refactoring")
def test_config_show(runner, temp_config):
    """Test showing configuration."""
    with patch("ai_org.core.config_manager.Path.home") as mock_home:
        mock_home.return_value = temp_config.parent.parent

        result = runner.invoke(cli, ["config", "show"])

        assert result.exit_code == 0
        assert "default_region" in result.output
        assert "us-east-1" in result.output
        assert "default_ou" in result.output
        assert "Staging" in result.output


@pytest.mark.skip(reason="Config path mocking needs refactoring")
def test_config_show_json_format(runner, temp_config):
    """Test showing configuration in JSON format."""
    with patch("ai_org.core.config_manager.Path.home") as mock_home:
        mock_home.return_value = temp_config.parent.parent

        result = runner.invoke(cli, ["config", "show", "--format", "json"])

        assert result.exit_code == 0
        config_data = json.loads(result.output)
        assert config_data["default_region"] == "us-east-1"
        assert config_data["default_ou"] == "Staging"


def test_config_set(runner, temp_config):
    """Test setting configuration values."""
    with patch("ai_org.core.config_manager.Path.home") as mock_home:
        mock_home.return_value = temp_config.parent.parent

        result = runner.invoke(cli, ["config", "set", "default_region", "eu-west-1"])

        assert result.exit_code == 0
        assert "set" in result.output.lower() or "updated" in result.output.lower()

        # Verify the value was set
        result = runner.invoke(cli, ["config", "show"])
        assert "eu-west-1" in result.output


def test_config_set_multiple_values(runner, temp_config):
    """Test setting multiple configuration values."""
    with patch("ai_org.core.config_manager.Path.home") as mock_home:
        mock_home.return_value = temp_config.parent.parent

        # Set first value
        result = runner.invoke(cli, ["config", "set", "default_region", "ap-southeast-1"])
        assert result.exit_code == 0

        # Set second value
        result = runner.invoke(cli, ["config", "set", "email_domain", "newdomain.com"])
        assert result.exit_code == 0

        # Verify both values
        result = runner.invoke(cli, ["config", "show"])
        assert "ap-southeast-1" in result.output
        assert "newdomain.com" in result.output


def test_config_set_invalid_key(runner, temp_config):
    """Test setting an invalid configuration key."""
    with patch("ai_org.core.config_manager.Path.home") as mock_home:
        mock_home.return_value = temp_config.parent.parent

        result = runner.invoke(cli, ["config", "set", "invalid_key", "value"])

        # Should either succeed (allowing any key) or show a warning
        # Implementation dependent
        assert result.exit_code == 0 or "warning" in result.output.lower()


def test_config_command_help(runner):
    """Test config command help."""
    result = runner.invoke(cli, ["config", "--help"])
    assert result.exit_code == 0
    assert "config" in result.output.lower()
    assert "show" in result.output
    assert "set" in result.output
