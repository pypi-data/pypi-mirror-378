#!/usr/bin/env python3
"""
Bootstrap AWS Organization structure for landing zone.
Creates OU hierarchy in an idempotent way - safe to run multiple times.
"""

import os
import sys
from typing import Optional

import boto3
import click
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OrgBootstrap:
    """Handles creation of Organization Unit structure."""

    def __init__(self, profile: Optional[str] = None):
        """Initialize AWS clients."""
        try:
            session = boto3.Session(profile_name=profile) if profile else boto3.Session()
            self.session = session  # Store session for later use
            self.org = session.client("organizations")
            self.sts = session.client("sts")
            self.ct = session.client("controltower")  # Add Control Tower client

            # Verify we're in the management account
            identity = self.sts.get_caller_identity()
            self.account_id = identity["Account"]
        except Exception as e:
            click.echo(f"❌ Failed to initialize AWS session: {e}", err=True)
            click.echo("💡 Make sure you're logged in: aws sso login --profile org", err=True)
            sys.exit(1)

    def get_root_id(self) -> str:
        """Get the organization root ID."""
        try:
            roots = self.org.list_roots()
            return roots["Roots"][0]["Id"]
        except Exception as e:
            click.echo(f"❌ Failed to get root ID: {e}", err=True)
            sys.exit(1)

    def get_or_create_ou(self, parent_id: str, name: str) -> str:
        """
        Get an OU ID, creating it if it doesn't exist.
        This is idempotent - safe to call multiple times.
        """
        try:
            # Check if OU already exists
            response = self.org.list_organizational_units_for_parent(ParentId=parent_id)
            for ou in response["OrganizationalUnits"]:
                if ou["Name"] == name:
                    return ou["Id"]

            # Create if not exists
            response = self.org.create_organizational_unit(ParentId=parent_id, Name=name)
            ou_id = response["OrganizationalUnit"]["Id"]
            click.echo(f"  ✅ Created OU: {name}")
            return ou_id

        except ClientError as e:
            if e.response["Error"]["Code"] == "DuplicateOrganizationalUnitException":
                # This shouldn't happen due to our check, but handle it anyway
                click.echo(f"⚠️  OU '{name}' already exists, fetching ID...")
                response = self.org.list_organizational_units_for_parent(ParentId=parent_id)
                for ou in response["OrganizationalUnits"]:
                    if ou["Name"] == name:
                        return ou["Id"]
            else:
                click.echo(f"❌ Failed to create OU '{name}': {e}", err=True)
                sys.exit(1)

    def list_ous_recursive(self, parent_id: str) -> list[dict[str, str]]:
        """Recursively list all OUs under a parent."""
        ous = []
        try:
            paginator = self.org.get_paginator("list_organizational_units_for_parent")
            for page in paginator.paginate(ParentId=parent_id):
                for ou in page["OrganizationalUnits"]:
                    ous.append(ou)
                    # Recursively get child OUs
                    child_ous = self.list_ous_recursive(ou["Id"])
                    ous.extend(child_ous)
        except Exception as e:
            click.echo(f"⚠️  Error listing OUs under {parent_id}: {e}")
        return ous

    def check_stacksets_trusted_access(self) -> bool:
        """Check if trusted access is enabled for StackSets."""
        try:
            response = self.org.list_aws_service_access_for_organization()
            service_principals = [
                s["ServicePrincipal"] for s in response.get("EnabledServicePrincipals", [])
            ]
            return "member.org.stacksets.cloudformation.amazonaws.com" in service_principals
        except ClientError:
            return False

    def get_ou_ids_only(self) -> dict[str, str]:
        """
        Get existing OU IDs without creating anything or enabling baselines.
        Used by deploy.py to avoid duplicate operations.
        """
        root_id = self.get_root_id()

        result = {"root": root_id}

        # Get existing OUs
        try:
            # Get Workloads OU
            response = self.org.list_organizational_units_for_parent(ParentId=root_id)
            for ou in response["OrganizationalUnits"]:
                if ou["Name"] == "Workloads":
                    result["workloads"] = ou["Id"]
                elif ou["Name"] == "Sandbox":
                    result["sandbox"] = ou["Id"]

            # Get Production/Staging under Workloads
            if "workloads" in result:
                response = self.org.list_organizational_units_for_parent(
                    ParentId=result["workloads"]
                )
                for ou in response["OrganizationalUnits"]:
                    if ou["Name"] == "Production":
                        result["production"] = ou["Id"]
                    elif ou["Name"] == "Staging":
                        result["staging"] = ou["Id"]
        except Exception:
            pass

        return result

    def get_ou_structure(self) -> dict[str, str]:
        """
        Get or create the complete OU structure.
        Returns a dictionary with all OU IDs.
        """
        # Check (but don't enable) StackSets trusted access
        if not self.check_stacksets_trusted_access():
            click.echo("⚠️  StackSets trusted access is not enabled!")
            click.echo(
                "   Run: aws organizations enable-aws-service-access "
                "--service-principal member.org.stacksets.cloudformation.amazonaws.com"
            )

        # Get root
        root_id = self.get_root_id()

        # Create/Get OUs
        workloads_id = self.get_or_create_ou(root_id, "Workloads")
        production_id = self.get_or_create_ou(workloads_id, "Production")
        staging_id = self.get_or_create_ou(workloads_id, "Staging")

        # Check for Sandbox OU (Control Tower created)
        sandbox_id = None
        try:
            response = self.org.list_organizational_units_for_parent(ParentId=root_id)
            for ou in response["OrganizationalUnits"]:
                if ou["Name"] == "Sandbox":
                    sandbox_id = ou["Id"]
                    break
        except Exception:
            pass

        result = {
            "root": root_id,
            "workloads": workloads_id,
            "production": production_id,
            "staging": staging_id,
            "sandbox": sandbox_id,
        }

        click.echo("\n📊 Organization Structure:")
        click.echo("  └─ Workloads")
        click.echo("      ├─ Production")
        click.echo("      └─ Staging")

        # Enable Control Tower baselines for all OUs under Workloads
        self.enable_workloads_baselines(workloads_id)

        return result

    def enable_workloads_baselines(self, workloads_ou_id: str) -> None:
        """Enable Control Tower baselines for all OUs under Workloads."""
        click.echo("\n⚙️  Configuring Control Tower baselines...")

        # Constants
        baseline_arn = (
            "arn:aws:controltower:us-east-1::baseline/17BSJV3IGJ2QSGA2"  # AWSControlTowerBaseline
        )
        baseline_version = "4.0"

        try:
            # Get organization ID
            workloads_info = self.org.describe_organizational_unit(
                OrganizationalUnitId=workloads_ou_id
            )
            org_id = workloads_info["OrganizationalUnit"]["Arn"].split("/")[1]

            # Get Identity Center baseline ARN (required parameter)
            identity_center_arn = None
            try:
                enabled_response = self.ct.list_enabled_baselines(maxResults=100)
                for baseline in enabled_response.get("enabledBaselines", []):
                    if "LN25R72TTG6IGPTQ" in baseline.get("baselineIdentifier", ""):
                        identity_center_arn = baseline.get("arn")
                        break
            except Exception as e:
                click.echo(f"  ⚠️  Could not get Identity Center baseline: {e}")
                return

            if not identity_center_arn:
                click.echo("  ⚠️  Identity Center baseline not found - cannot proceed")
                return

            # Get all currently enabled baselines
            enabled_ous = set()
            try:
                enabled_response = self.ct.list_enabled_baselines(maxResults=100)
                for baseline in enabled_response.get("enabledBaselines", []):
                    target = baseline.get("targetIdentifier", "")
                    if "/ou/" in target:
                        ou_id = target.split("/")[-1]
                        enabled_ous.add(ou_id)
            except Exception:
                pass

            # Get all OUs under Workloads (NOT including Workloads itself)
            child_ous = self.list_ous_recursive(workloads_ou_id)

            if not child_ous:
                click.echo("  ℹ️  No child OUs found under Workloads")
                return

            # Enable baseline for each child OU
            for ou in child_ous:
                ou_id = ou["Id"]
                ou_name = ou["Name"]

                if ou_id in enabled_ous:
                    click.echo(f"  ✅ Baseline already enabled for {ou_name}")
                    continue

                try:
                    # Construct the target ARN
                    target_arn = f"arn:aws:organizations::{self.account_id}:ou/{org_id}/{ou_id}"

                    click.echo(f"  🚀 Enabling baseline for {ou_name}...")

                    response = self.ct.enable_baseline(
                        baselineIdentifier=baseline_arn,
                        baselineVersion=baseline_version,
                        targetIdentifier=target_arn,
                        parameters=[
                            {
                                "key": "IdentityCenterEnabledBaselineArn",
                                "value": identity_center_arn,
                            }
                        ],
                    )

                    operation_id = response["operationIdentifier"]

                    # Wait for operation to complete
                    import time

                    max_wait = 300  # 5 minutes
                    start_time = time.time()

                    while time.time() - start_time < max_wait:
                        try:
                            op_response = self.ct.get_baseline_operation(
                                operationIdentifier=operation_id
                            )
                            status = op_response["baselineOperation"]["status"]

                            if status == "SUCCEEDED":
                                click.echo(f"  ✅ Baseline enabled for {ou_name}")
                                break
                            if status in ["FAILED", "STOPPED"]:
                                msg = op_response["baselineOperation"].get(
                                    "statusMessage", "Unknown error"
                                )
                                click.echo(f"  ❌ Failed to enable baseline for {ou_name}: {msg}")
                                break
                            time.sleep(5)
                        except Exception:
                            time.sleep(5)

                except Exception as e:
                    error_msg = str(e)
                    if "already enabled" in error_msg.lower():
                        click.echo(f"  ✅ Baseline already enabled for {ou_name}")
                    elif "modify your landing zone settings" in error_msg.lower():
                        click.echo(
                            f"  ⚠️  {ou_name}: Requires landing zone update "
                            "(manual action needed in Control Tower console)"
                        )
                    else:
                        click.echo(f"  ⚠️  Could not enable baseline for {ou_name}: {error_msg}")

        except Exception as e:
            click.echo(f"  ⚠️  Error configuring baselines: {e}")

    def verify_structure(self) -> bool:
        """
        Verify the OU structure is correctly set up.
        Returns True if all expected OUs exist.
        """
        try:
            structure = self.get_ou_structure()

            required = ["root", "workloads", "production", "staging"]
            missing = [k for k in required if not structure.get(k)]

            if missing:
                click.echo(f"❌ Missing required OUs: {', '.join(missing)}", err=True)
                return False

            click.echo("✅ All required OUs are present")
            return True

        except Exception as e:
            click.echo(f"❌ Failed to verify structure: {e}", err=True)
            return False

    def list_accounts_in_ou(self, ou_id: str) -> list[dict[str, str]]:
        """List all accounts in an OU."""
        try:
            accounts = []
            paginator = self.org.get_paginator("list_accounts_for_parent")
            for page in paginator.paginate(ParentId=ou_id):
                accounts.extend(page["Accounts"])
            return accounts
        except Exception as e:
            click.echo(f"⚠️  Could not list accounts in OU {ou_id}: {e}")
            return []

    def show_current_state(self):
        """Display the current state of the organization."""
        click.echo("\n📋 Current Organization State:")

        try:
            structure = self.get_ou_structure()

            # Show accounts in each OU
            for name, ou_id in structure.items():
                if ou_id and name != "root":
                    accounts = self.list_accounts_in_ou(ou_id)
                    if accounts:
                        click.echo(f"\n   {name.title()} OU ({ou_id}):")
                        for acc in accounts:
                            status = "✅" if acc["Status"] == "ACTIVE" else "⏳"
                            click.echo(f"      {status} {acc['Name']} ({acc['Id']})")
                    else:
                        click.echo(f"\n   {name.title()} OU ({ou_id}): No accounts")

        except Exception as e:
            click.echo(f"❌ Failed to show current state: {e}", err=True)


@click.command()
@click.option("--profile", default=os.getenv("AWS_PROFILE"), help="AWS profile to use")
@click.option("--verify", is_flag=True, help="Only verify, don't create")
@click.option("--status", is_flag=True, help="Show current organization state")
def main(profile: str, verify: bool, status: bool):
    """Bootstrap AWS Organization structure for landing zone."""

    bootstrap = OrgBootstrap(profile)

    if status:
        bootstrap.show_current_state()
        return

    if verify:
        click.echo("🔍 Verifying organization structure...")
        if bootstrap.verify_structure():
            click.echo("✅ Organization structure is ready")
            sys.exit(0)
        else:
            click.echo("❌ Organization structure needs setup", err=True)
            sys.exit(1)

    # Create/verify structure
    click.echo("\n" + "=" * 60)
    click.echo("  STEP 1: ORGANIZATION STRUCTURE")
    click.echo("=" * 60)

    bootstrap.get_ou_structure()

    click.echo("\n✅ Organization structure is ready!")


if __name__ == "__main__":
    main()
