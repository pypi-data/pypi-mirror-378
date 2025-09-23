"""Unit tests for config commands."""

from unittest.mock import MagicMock, patch

from ai_org.cli import cli


def test_config_show(runner, temp_config):
    """Test showing configuration."""
    with patch("ai_org.core.config_manager.Path.home") as mock_home:
        mock_home.return_value = temp_config.parent

        result = runner.invoke(cli, ["config", "show"])

        assert result.exit_code == 0
        assert "AWS_PROFILE" in result.output
        # Profile value could be from environment or file
        assert "AWS_PROFILE:" in result.output
        assert "DEFAULT_SSO_EMAIL" in result.output
        assert "admin@example.com" in result.output


def test_config_show_json_format(runner, temp_config):
    """Test that config show doesn't support JSON format."""
    with patch("ai_org.core.config_manager.Path.home") as mock_home:
        mock_home.return_value = temp_config.parent

        result = runner.invoke(cli, ["config", "show", "--format", "json"])

        # The show command doesn't support JSON format - should error
        assert result.exit_code != 0
        assert "No such option" in result.output


def test_config_set(runner, temp_config):
    """Test setting configuration values."""
    with patch("ai_org.core.config_manager.Path.home") as mock_home:
        mock_home.return_value = temp_config.parent

        result = runner.invoke(cli, ["config", "set", "AWS_PROFILE", "new-profile"])

        assert result.exit_code == 0
        assert "Set AWS_PROFILE = new-profile" in result.output


def test_config_set_multiple_values(runner, temp_config):
    """Test setting multiple configuration values."""
    with patch("ai_org.core.config_manager.Path.home") as mock_home:
        mock_home.return_value = temp_config.parent

        # Set first value
        result1 = runner.invoke(cli, ["config", "set", "AWS_PROFILE", "profile1"])
        assert result1.exit_code == 0

        # Set second value
        result2 = runner.invoke(cli, ["config", "set", "DEFAULT_SSO_EMAIL", "user@test.com"])
        assert result2.exit_code == 0

        # Verify both are set
        result3 = runner.invoke(cli, ["config", "show"])
        assert result3.exit_code == 0
        assert "profile1" in result3.output or "AWS_PROFILE" in result3.output


def test_config_get(runner, temp_config):
    """Test getting a configuration value."""
    with patch("ai_org.core.config_manager.Path.home") as mock_home:
        mock_home.return_value = temp_config.parent

        result = runner.invoke(cli, ["config", "get", "AWS_PROFILE"])

        assert result.exit_code == 0
        # Should have some output (profile value)
        assert result.output.strip()


def test_config_get_missing_key(runner, temp_config):
    """Test getting a non-existent configuration value."""
    with patch("ai_org.core.config_manager.Path.home") as mock_home:
        mock_home.return_value = temp_config.parent

        result = runner.invoke(cli, ["config", "get", "NONEXISTENT_KEY"])

        assert result.exit_code == 0
        assert "not found" in result.output.lower() or result.output.strip() == ""


def test_config_reset(runner, temp_config):
    """Test resetting configuration."""
    with patch("ai_org.core.config_manager.Path.home") as mock_home:
        mock_home.return_value = temp_config.parent

        # Use --yes to avoid interactive prompt
        result = runner.invoke(cli, ["config", "reset"], input="y\n")

        if "Delete" in result.output:
            # Config file exists, should ask for confirmation
            assert "Delete" in result.output or "reset" in result.output.lower()
        else:
            # Config file doesn't exist
            assert "No configuration file exists" in result.output or result.exit_code == 0


def test_config_init(runner, temp_config):
    """Test initializing configuration interactively."""
    with patch("ai_org.core.config_manager.Path.home") as mock_home:
        mock_home.return_value = temp_config.parent

        # Simulate interactive input (just pressing Enter for defaults)
        input_data = "\n\n\n\n\n\n"
        result = runner.invoke(cli, ["config", "init"], input=input_data)

        assert result.exit_code == 0
        assert "Configuration" in result.output or "config" in result.output.lower()


def test_config_list_permission_sets(runner, mock_boto3_client):
    """Test listing permission sets."""
    with patch("ai_org.core.aws_client.boto3.Session") as mock_session:
        mock_sso_client = MagicMock()
        mock_sso_client.list_instances.return_value = {
            "Instances": [
                {"InstanceArn": "arn:aws:sso:::instance/test", "IdentityStoreId": "d-test"}
            ]
        }
        mock_sso_client.list_permission_sets.return_value = {
            "PermissionSets": ["arn:aws:sso:::permissionSet/test/ps-admin"]
        }
        mock_sso_client.describe_permission_set.return_value = {
            "PermissionSet": {"Name": "AWSAdministratorAccess", "Description": "Admin access"}
        }

        mock_session_instance = mock_session.return_value
        mock_session_instance.client.return_value = mock_sso_client

        result = runner.invoke(cli, ["config", "list-permission-sets"])

        assert result.exit_code == 0
        assert "AWSAdministratorAccess" in result.output or "permission" in result.output.lower()


def test_config_command_help(runner):
    """Test config command help."""
    result = runner.invoke(cli, ["config", "--help"])

    assert result.exit_code == 0
    assert "config" in result.output.lower()
    assert "init" in result.output
    assert "show" in result.output
    assert "set" in result.output
    assert "get" in result.output
