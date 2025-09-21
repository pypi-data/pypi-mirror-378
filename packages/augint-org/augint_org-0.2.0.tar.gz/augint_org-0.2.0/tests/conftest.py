"""Pytest configuration and shared fixtures."""

import os
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    """Provide a Click test runner."""
    return CliRunner()


@pytest.fixture
def mock_boto3_session():
    """Mock boto3 Session to avoid real AWS calls."""
    with patch("boto3.Session") as mock_session:
        # Mock the session instance
        session_instance = MagicMock()
        mock_session.return_value = session_instance

        # Mock commonly used clients
        mock_orgs = MagicMock()
        mock_sso = MagicMock()
        mock_cf = MagicMock()
        mock_sts = MagicMock()

        # Configure client returns
        def get_client(service_name, **kwargs):
            clients = {
                "organizations": mock_orgs,
                "sso-admin": mock_sso,
                "cloudformation": mock_cf,
                "sts": mock_sts,
            }
            return clients.get(service_name, MagicMock())

        session_instance.client = get_client

        # Set up default returns for common operations
        mock_sts.get_caller_identity.return_value = {
            "UserId": "AIDAI23HXD2O5EXAMPLE",
            "Account": "123456789012",
            "Arn": "arn:aws:iam::123456789012:user/test",
        }

        mock_orgs.list_accounts.return_value = {
            "Accounts": [
                {
                    "Id": "123456789012",
                    "Arn": "arn:aws:organizations::123456789012:account/o-example/123456789012",
                    "Email": "account1@example.com",
                    "Name": "Account1",
                    "Status": "ACTIVE",
                    "JoinedMethod": "CREATED",
                    "JoinedTimestamp": "2024-01-01T00:00:00Z",
                },
                {
                    "Id": "234567890123",
                    "Arn": "arn:aws:organizations::123456789012:account/o-example/234567890123",
                    "Email": "account2@example.com",
                    "Name": "Account2",
                    "Status": "ACTIVE",
                    "JoinedMethod": "CREATED",
                    "JoinedTimestamp": "2024-01-02T00:00:00Z",
                },
            ]
        }

        mock_orgs.list_organizational_units_for_parent.return_value = {
            "OrganizationalUnits": [
                {
                    "Id": "ou-root-example1",
                    "Arn": "arn:aws:organizations::123456789012:ou/o-example/ou-root-example1",
                    "Name": "Production",
                },
                {
                    "Id": "ou-root-example2",
                    "Arn": "arn:aws:organizations::123456789012:ou/o-example/ou-root-example2",
                    "Name": "Staging",
                },
            ]
        }

        mock_orgs.describe_organization.return_value = {
            "Organization": {
                "Id": "o-example",
                "Arn": "arn:aws:organizations::123456789012:organization/o-example",
                "FeatureSet": "ALL",
                "MasterAccountId": "123456789012",
                "MasterAccountEmail": "master@example.com",
            }
        }

        yield {
            "session": session_instance,
            "orgs": mock_orgs,
            "sso": mock_sso,
            "cf": mock_cf,
            "sts": mock_sts,
        }


@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / ".config" / "ai-org"
    config_dir.mkdir(parents=True)

    # Create a sample config file
    config_file = config_dir / "config.yaml"
    config_file.write_text("""
default_region: us-east-1
default_ou: Staging
email_domain: example.com
""")

    # Mock the home directory
    with patch.dict(os.environ, {"HOME": str(tmp_path)}):
        yield config_dir


@pytest.fixture
def mock_env_vars():
    """Mock common environment variables."""
    env_vars = {
        "AWS_PROFILE": "test-profile",
        "AWS_REGION": "us-east-1",
        "GH_ACCOUNT": "test-org",
        "GH_REPO": "test-repo",
        "NOTIFICATIONS_EMAIL": "admin@example.com",
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_stackset_template():
    """Provide a sample StackSet template."""
    return {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Sample StackSet Template",
        "Resources": {
            "TestBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "BucketName": "test-bucket",
                    "VersioningConfiguration": {"Status": "Enabled"},
                },
            }
        },
    }
