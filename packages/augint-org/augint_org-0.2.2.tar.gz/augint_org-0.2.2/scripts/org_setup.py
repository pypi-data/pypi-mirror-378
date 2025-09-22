#!/usr/bin/env python3
"""
Setup GitHub OIDC and deployment role in management account.
This enables the GitHub Actions pipeline to deploy infrastructure.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import boto3
import click
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.ai_org.utils.config_loader import create_example_user_config, load_config_value

# Load environment variables
load_dotenv()

# Create example user config on first run
create_example_user_config()

# Configuration with fallback to user config
GITHUB_ORG = load_config_value("GH_ACCOUNT")
GITHUB_REPO = load_config_value("GH_REPO")

# AWS Configuration
HOME_REGION = "us-east-1"
STACK_NAME = "org-pipeline-role"

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATE_PATH = PROJECT_ROOT / "stacksets" / "pipeline-role.yaml"


class OrgSetup:
    """Handles management account setup for pipeline deployment."""

    def __init__(self, profile: Optional[str] = None):
        """Initialize AWS clients."""
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.cf = session.client("cloudformation", region_name=HOME_REGION)
        self.sts = session.client("sts")

        # Get account info
        identity = self.sts.get_caller_identity()
        self.account_id = identity["Account"]
        self.account_arn = identity["Arn"]
        click.echo(f"🔧 Operating as: {self.account_arn}")
        click.echo(f"📍 Management Account: {self.account_id}")

    def deploy_pipeline_role(self) -> str:
        """Deploy GitHub OIDC provider and pipeline role."""
        click.echo("\n🚀 Deploying pipeline role to management account...")

        # Check template exists
        if not TEMPLATE_PATH.exists():
            click.echo(f"❌ Template not found: {TEMPLATE_PATH}", err=True)
            click.echo("Please create stacksets/pipeline-role.yaml first", err=True)
            sys.exit(1)

        with open(TEMPLATE_PATH) as f:
            template_body = f.read()

        # Deploy or update stack
        try:
            # Check if stack exists
            self.cf.describe_stacks(StackName=STACK_NAME)
            exists = True
            click.echo("  ♻️  Updating existing stack...")
        except ClientError as e:
            if "does not exist" in str(e):
                exists = False
                click.echo("  🆕 Creating new stack...")
            else:
                raise

        parameters = [
            {"ParameterKey": "GitHubOrg", "ParameterValue": GITHUB_ORG},
            {"ParameterKey": "GitHubRepo", "ParameterValue": GITHUB_REPO},
        ]

        if exists:
            try:
                self.cf.update_stack(
                    StackName=STACK_NAME,
                    TemplateBody=template_body,
                    Parameters=parameters,
                    Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
                )
                self._wait_for_stack(STACK_NAME, "UPDATE_COMPLETE")
            except ClientError as e:
                if "No updates are to be performed" in str(e):
                    click.echo("  ✅ Stack is up to date")
                else:
                    raise
        else:
            self.cf.create_stack(
                StackName=STACK_NAME,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            )
            self._wait_for_stack(STACK_NAME, "CREATE_COMPLETE")

        # Get role ARN from outputs
        stacks = self.cf.describe_stacks(StackName=STACK_NAME)
        outputs = stacks["Stacks"][0].get("Outputs", [])

        role_arn = None
        for output in outputs:
            if output["OutputKey"] == "RoleArn":
                role_arn = output["OutputValue"]
                break

        if role_arn:
            click.echo("\n✅ Pipeline role deployed successfully!")
            click.echo(f"📝 Role ARN: {role_arn}")
            click.echo("\n🔑 Add this to GitHub Actions secrets:")
            click.echo(f"   AWS_ROLE_ARN = {role_arn}")
            return role_arn
        click.echo("⚠️  Role ARN not found in stack outputs")
        return ""

    def _wait_for_stack(self, stack_name: str, success_status: str) -> None:
        """Wait for CloudFormation stack operation to complete."""
        click.echo("  ⏳ Waiting for stack operation...")

        waiter_type = (
            "stack_create_complete" if "CREATE" in success_status else "stack_update_complete"
        )
        waiter = self.cf.get_waiter(waiter_type)

        try:
            waiter.wait(
                StackName=stack_name,
                WaiterConfig={
                    "Delay": 5,
                    "MaxAttempts": 120,  # 10 minutes max
                },
            )
            click.echo("  ✅ Stack operation completed")
        except Exception as e:
            # Get stack events to show what went wrong
            events = self.cf.describe_stack_events(StackName=stack_name)
            for event in events["StackEvents"][:5]:  # Show last 5 events
                if "FAILED" in event.get("ResourceStatus", ""):
                    click.echo(
                        f"  ❌ {event['LogicalResourceId']}: {event.get('ResourceStatusReason', 'Unknown error')}",
                        err=True,
                    )
            raise Exception(f"Stack operation failed: {e}")

    def verify_setup(self) -> None:
        """Verify the pipeline role can be assumed from GitHub."""
        click.echo("\n🔍 Verifying setup...")

        # Check OIDC provider exists
        iam = boto3.client("iam")
        providers = iam.list_open_id_connect_providers()

        github_provider = None
        for provider in providers["OpenIDConnectProviderList"]:
            provider_detail = iam.get_open_id_connect_provider(
                OpenIDConnectProviderArn=provider["Arn"]
            )
            if "token.actions.githubusercontent.com" in provider_detail["Url"]:
                github_provider = provider["Arn"]
                break

        if github_provider:
            click.echo("  ✅ GitHub OIDC provider exists")
        else:
            click.echo("  ❌ GitHub OIDC provider not found", err=True)

        # Check role exists
        try:
            role = iam.get_role(RoleName="OrgPipelineRole")
            click.echo("  ✅ OrgPipelineRole exists")

            # Show trust policy
            trust_policy = role["Role"]["AssumeRolePolicyDocument"]
            for statement in trust_policy["Statement"]:
                if "Federated" in statement["Principal"]:
                    conditions = statement.get("Condition", {}).get("StringLike", {})
                    sub_patterns = conditions.get("token.actions.githubusercontent.com:sub", [])
                    if sub_patterns:
                        click.echo("  📋 Trust patterns:")
                        for pattern in sub_patterns:
                            click.echo(f"     - {pattern}")
        except ClientError:
            click.echo("  ❌ OrgPipelineRole not found", err=True)

    def destroy(self) -> None:
        """Remove the pipeline role stack."""
        click.confirm(f"⚠️  Delete stack '{STACK_NAME}'?", abort=True)

        try:
            click.echo("🗑️  Deleting stack...")
            self.cf.delete_stack(StackName=STACK_NAME)

            # Wait for deletion
            waiter = self.cf.get_waiter("stack_delete_complete")
            waiter.wait(StackName=STACK_NAME, WaiterConfig={"Delay": 5, "MaxAttempts": 120})
            click.echo("✅ Stack deleted successfully")
        except ClientError as e:
            if "does not exist" in str(e):
                click.echo("Stack not found")
            else:
                click.echo(f"❌ Error deleting stack: {e}", err=True)


@click.command()
@click.option("--verify", is_flag=True, help="Verify the setup")
@click.option("--destroy", is_flag=True, help="Remove the pipeline role")
@click.option("--profile", default=os.getenv("AWS_PROFILE"), help="AWS profile to use")
def main(verify: bool, destroy: bool, profile: str):
    """Setup GitHub OIDC and deployment role in management account."""
    # Validate required environment variables
    global GITHUB_ORG, GITHUB_REPO

    if not GITHUB_ORG:
        click.echo("❌ Error: GH_ACCOUNT is required", err=True)
        click.echo("Set via one of:", err=True)
        click.echo("  • .env file in project", err=True)
        click.echo("  • export GH_ACCOUNT=YourGitHubOrg", err=True)
        click.echo("  • ~/.aillc/.env.aillc-org", err=True)
        sys.exit(1)

    if not GITHUB_REPO:
        click.echo("❌ Error: GH_REPO is required", err=True)
        click.echo("Set via one of:", err=True)
        click.echo("  • .env file in project", err=True)
        click.echo("  • export GH_REPO=YourRepoName", err=True)
        click.echo("  • ~/.aillc/.env.aillc-org", err=True)
        sys.exit(1)

    try:
        setup = OrgSetup(profile=profile)

        if destroy:
            setup.destroy()
        elif verify:
            setup.verify_setup()
        else:
            click.echo("\n" + "=" * 60)
            click.echo("  STEP 2: PIPELINE ROLE SETUP")
            click.echo("=" * 60)
            role_arn = setup.deploy_pipeline_role()
            if role_arn:
                setup.verify_setup()

    except Exception as e:
        click.echo(f"❌ ERROR: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
