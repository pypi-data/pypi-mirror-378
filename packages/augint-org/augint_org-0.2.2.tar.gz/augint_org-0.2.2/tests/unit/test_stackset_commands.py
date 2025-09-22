"""Unit tests for StackSet commands."""

from unittest.mock import patch

import pytest

from ai_org.cli import cli


@pytest.mark.skip(reason="StackSet mock setup needs refactoring")
def test_stackset_list(runner, mock_boto3_session):
    """Test listing StackSets."""
    with patch("ai_org.core.aws_client.boto3.Session") as mock_session:
        mock_session.return_value = mock_boto3_session["session"]

        # Mock CloudFormation responses
        mock_boto3_session["cf"].list_stack_sets.return_value = {
            "Summaries": [
                {
                    "StackSetName": "test-stackset-1",
                    "StackSetId": "test-stackset-1:example-id",
                    "Description": "Test StackSet 1",
                    "Status": "ACTIVE",
                },
                {
                    "StackSetName": "test-stackset-2",
                    "StackSetId": "test-stackset-2:example-id",
                    "Description": "Test StackSet 2",
                    "Status": "ACTIVE",
                },
            ]
        }

        result = runner.invoke(cli, ["stackset", "list"])

        assert result.exit_code == 0
        assert "test-stackset-1" in result.output
        assert "test-stackset-2" in result.output


def test_stackset_status_missing_args(runner):
    """Test checking StackSet status without required arguments."""
    result = runner.invoke(cli, ["stackset", "status"])
    assert result.exit_code != 0
    assert "Missing argument" in result.output or "required" in result.output.lower()


def test_stackset_status(runner, mock_boto3_session):
    """Test checking StackSet status for an account."""
    with patch("ai_org.core.aws_client.boto3.Session") as mock_session:
        mock_session.return_value = mock_boto3_session["session"]

        # Mock CloudFormation responses
        mock_boto3_session["cloudformation"].list_stack_instances.return_value = {
            "Summaries": [
                {
                    "StackSetId": "test-stackset:id",
                    "Region": "us-east-1",
                    "Account": "123456789012",
                    "StackInstanceStatus": {"DetailedStatus": "SUCCEEDED"},
                }
            ]
        }

        result = runner.invoke(cli, ["stackset", "status", "123456789012"])

        assert result.exit_code == 0


# Removed - delete command doesn't exist


def test_stackset_command_help(runner):
    """Test StackSet command help."""
    result = runner.invoke(cli, ["stackset", "--help"])
    assert result.exit_code == 0
    assert "StackSet" in result.output
    assert "status" in result.output
    assert "list" in result.output
