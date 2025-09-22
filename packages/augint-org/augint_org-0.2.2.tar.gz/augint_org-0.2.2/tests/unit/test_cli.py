"""Unit tests for the CLI module."""

from ai_org.__version__ import __version__
from ai_org.cli import cli


def test_cli_version(runner):
    """Test that --version shows the correct version."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_cli_help(runner):
    """Test that --help works."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "AI-ORG: Manage" in result.output
    assert "account" in result.output
    assert "sso" in result.output
    assert "stackset" in result.output
    assert "config" in result.output


def test_cli_no_args(runner):
    """Test that CLI shows help when no args provided."""
    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    assert "AI-ORG: Manage" in result.output


def test_cli_with_profile(runner):
    """Test that --profile option is accepted."""
    result = runner.invoke(cli, ["--profile", "test-profile", "--help"])
    assert result.exit_code == 0
    assert "AI-ORG: Manage" in result.output


def test_cli_with_region(runner):
    """Test that --region option is accepted."""
    result = runner.invoke(cli, ["--region", "eu-west-1", "--help"])
    assert result.exit_code == 0
    assert "AI-ORG: Manage" in result.output


def test_account_command_group(runner):
    """Test that account command group is available."""
    result = runner.invoke(cli, ["account", "--help"])
    assert result.exit_code == 0
    assert "Manage AWS accounts in the organization" in result.output
    assert "create" in result.output
    assert "list" in result.output
    assert "get" in result.output


def test_sso_command_group(runner):
    """Test that SSO command group is available."""
    result = runner.invoke(cli, ["sso", "--help"])
    assert result.exit_code == 0
    assert "Manage SSO permissions for accounts" in result.output
    assert "assign" in result.output
    assert "list" in result.output
    assert "sync" in result.output


def test_stackset_command_group(runner):
    """Test that stackset command group is available."""
    result = runner.invoke(cli, ["stackset", "--help"])
    assert result.exit_code == 0
    assert "Monitor StackSet deployments" in result.output
    assert "status" in result.output
    assert "list" in result.output


def test_config_command_group(runner):
    """Test that config command group is available."""
    result = runner.invoke(cli, ["config", "--help"])
    assert result.exit_code == 0
    assert "Manage ai-org configuration" in result.output
    assert "show" in result.output
    assert "set" in result.output
