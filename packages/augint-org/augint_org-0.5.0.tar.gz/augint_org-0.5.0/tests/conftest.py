"""Test configuration and fixtures."""

import os
from unittest.mock import MagicMock, patch

import boto3
import click
import pytest
from click.testing import CliRunner
from moto import mock_aws


@pytest.fixture
def runner():
    """Create a Click test runner."""
    return CliRunner()


@pytest.fixture
def mock_aws_setup():
    """Setup mock AWS environment."""
    with mock_aws():
        # Setup basic organizations structure
        org_client = boto3.client("organizations", region_name="us-east-1")
        org_client.create_organization(FeatureSet="ALL")

        # Create OUs
        root_id = org_client.list_roots()["Roots"][0]["Id"]
        workloads_ou = org_client.create_organizational_unit(ParentId=root_id, Name="Workloads")[
            "OrganizationalUnit"
        ]["Id"]

        staging_ou = org_client.create_organizational_unit(ParentId=workloads_ou, Name="Staging")[
            "OrganizationalUnit"
        ]["Id"]

        prod_ou = org_client.create_organizational_unit(ParentId=workloads_ou, Name="Production")[
            "OrganizationalUnit"
        ]["Id"]

        # Setup SSO mock
        sso_client = boto3.client("sso-admin", region_name="us-east-1")
        identity_client = boto3.client("identitystore", region_name="us-east-1")

        yield {
            "org_client": org_client,
            "sso_client": sso_client,
            "identity_client": identity_client,
            "root_id": root_id,
            "workloads_ou": workloads_ou,
            "staging_ou": staging_ou,
            "prod_ou": prod_ou,
        }


@pytest.fixture
def mock_aws_client():
    """Mock AWS client for testing."""
    mock_client = MagicMock()

    # Mock organizations responses
    mock_client.organizations.list_accounts.return_value = {
        "Accounts": [
            {
                "Id": "123456789012",
                "Name": "test-account-1",
                "Email": "test1@example.com",
                "Status": "ACTIVE",
                "JoinedMethod": "INVITED",
                "JoinedTimestamp": "2021-01-01",
            },
            {
                "Id": "123456789013",
                "Name": "test-account-2",
                "Email": "test2@example.com",
                "Status": "ACTIVE",
                "JoinedMethod": "INVITED",
                "JoinedTimestamp": "2021-01-01",
            },
        ]
    }

    mock_client.organizations.describe_account.return_value = {
        "Account": {
            "Id": "123456789012",
            "Name": "test-account",
            "Email": "test@example.com",
            "Status": "ACTIVE",
            "JoinedMethod": "INVITED",
            "JoinedTimestamp": "2021-01-01",
        }
    }

    # Mock SSO responses
    mock_client.sso_admin.list_instances.return_value = {
        "Instances": [
            {
                "InstanceArn": "arn:aws:sso:::instance/ins-12345678",
                "IdentityStoreId": "d-1234567890",
            }
        ]
    }

    mock_client.sso_admin.list_permission_sets.return_value = {
        "PermissionSets": ["arn:aws:sso:::permissionSet/ins-12345678/ps-12345678"]
    }

    return mock_client


@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary config directory with .env file."""
    config_dir = tmp_path / ".ai-org"
    config_dir.mkdir(parents=True)

    # Create a sample .env config file
    config_file = config_dir.parent / ".ai-org.env"
    config_file.write_text("""AWS_PROFILE=test-profile
DEFAULT_SSO_EMAIL=admin@example.com
DEFAULT_PERMISSION_SET=AWSAdministratorAccess
NOTIFICATIONS_EMAIL=alerts@example.com
BUDGETS_MONTHLY_DEFAULT=1000
BUDGETS_ANOMALY_THRESHOLD=100
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
def mock_boto3_client():
    """Mock boto3 client creation."""
    with patch("boto3.client") as mock:
        mock_org_client = MagicMock()
        mock_sso_client = MagicMock()
        mock_cf_client = MagicMock()

        def client_factory(service, **kwargs):
            if service == "organizations":
                return mock_org_client
            if service == "sso-admin":
                return mock_sso_client
            if service == "cloudformation":
                return mock_cf_client
            return MagicMock()

        mock.side_effect = client_factory
        yield {
            "organizations": mock_org_client,
            "sso-admin": mock_sso_client,
            "cloudformation": mock_cf_client,
        }


@pytest.fixture(autouse=True)
def _no_aws_calls():
    """Prevent accidental AWS API calls in tests."""
    with patch.dict(
        os.environ, {"AWS_ACCESS_KEY_ID": "testing", "AWS_SECRET_ACCESS_KEY": "testing"}
    ):
        yield


@pytest.fixture
def cli_context():
    """Create a mock CLI context."""
    ctx = MagicMock(spec=click.Context)
    ctx.obj = {
        "profile": "test-profile",
        "region": "us-east-1",
        "json": False,
        "verbose": False,
        "output": MagicMock(),
    }
    return ctx


@pytest.fixture
def mock_boto3_session():
    """Mock boto3 session for testing."""
    with patch("boto3.Session") as mock_session:
        mock_instance = MagicMock()
        mock_session.return_value = mock_instance

        # Mock client creation
        mock_org_client = MagicMock()
        mock_sso_client = MagicMock()
        mock_cf_client = MagicMock()

        def client_factory(service, **kwargs):
            if service == "organizations":
                return mock_org_client
            if service == "sso-admin":
                return mock_sso_client
            if service == "cloudformation":
                return mock_cf_client
            return MagicMock()

        mock_instance.client = client_factory

        # Setup some default returns
        mock_org_client.describe_account.return_value = {
            "Account": {
                "Id": "123456789012",
                "Name": "test-account",
                "Email": "test@example.com",
                "Status": "ACTIVE",
            }
        }

        yield {
            "session": mock_instance,
            "organizations": mock_org_client,
            "sso-admin": mock_sso_client,
            "cloudformation": mock_cf_client,
        }
