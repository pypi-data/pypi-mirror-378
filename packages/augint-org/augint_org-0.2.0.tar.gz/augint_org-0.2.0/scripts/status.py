#!/usr/bin/env python3
"""
Show deployment status of AWS Organization infrastructure.
"""

import os
import sys
from typing import Optional

import boto3
import click
from dotenv import load_dotenv

from .bootstrap import OrgBootstrap

# Load environment variables
load_dotenv()


class DeploymentStatus:
    """Check and display deployment status."""

    def __init__(self, profile: Optional[str] = None):
        """Initialize AWS clients."""
        try:
            session = boto3.Session(profile_name=profile) if profile else boto3.Session()
            self.cf = session.client("cloudformation", region_name="us-east-1")
            self.org = session.client("organizations")
            self.sts = session.client("sts")

            # Get account info
            identity = self.sts.get_caller_identity()
            self.account_id = identity["Account"]
            self.account_name = (
                identity["Arn"].split("/")[-2] if "/" in identity["Arn"] else "Unknown"
            )
        except Exception as e:
            click.echo(f"❌ Failed to initialize AWS session: {e}", err=True)
            click.echo("💡 Make sure you're logged in: aws sso login --profile org", err=True)
            sys.exit(1)

    def check_ou_structure(self) -> dict:
        """Check OU structure status."""
        bootstrap = OrgBootstrap()
        ou_structure = {}

        try:
            root_id = bootstrap.get_root_id()
            root_ous = self.org.list_organizational_units_for_parent(ParentId=root_id)

            for ou in root_ous["OrganizationalUnits"]:
                if ou["Name"] == "Workloads":
                    ou_structure["workloads"] = ou["Id"]
                    # Check for child OUs
                    child_ous = self.org.list_organizational_units_for_parent(ParentId=ou["Id"])
                    for child in child_ous["OrganizationalUnits"]:
                        if child["Name"] == "Production":
                            ou_structure["production"] = child["Id"]
                        elif child["Name"] == "Staging":
                            ou_structure["staging"] = child["Id"]
                elif ou["Name"] == "Sandbox":
                    ou_structure["sandbox"] = ou["Id"]
        except Exception as e:
            click.echo(f"⚠️  Error checking OU structure: {e}")

        return ou_structure

    def check_stacksets(self) -> list:
        """Check deployed StackSets."""
        stacksets = []
        try:
            response = self.cf.list_stack_sets(Status="ACTIVE")
            for ss in response["Summaries"]:
                # Get more details
                details = self.cf.describe_stack_set(StackSetName=ss["StackSetName"])
                stackset = details["StackSet"]

                # Count instances
                instances = self.cf.list_stack_instances(StackSetName=ss["StackSetName"])[
                    "Summaries"
                ]

                stacksets.append(
                    {
                        "name": ss["StackSetName"],
                        "status": ss["Status"],
                        "auto_deploy": stackset.get("AutoDeployment", {}).get("Enabled", False),
                        "instance_count": len(instances),
                        "instances": instances,
                        "last_updated": ss.get("LastDriftCheckTimestamp", ss.get("CreationTime")),
                    }
                )
        except Exception as e:
            click.echo(f"⚠️  Error checking StackSets: {e}")

        return stacksets

    def check_scps(self) -> list:
        """Check Service Control Policies."""
        scps = []
        try:
            response = self.org.list_policies(Filter="SERVICE_CONTROL_POLICY")
            for policy in response["Policies"]:
                if policy["Name"] != "FullAWSAccess":  # Skip default
                    # Get targets
                    targets = self.org.list_targets_for_policy(PolicyId=policy["Id"])
                    scps.append(
                        {
                            "name": policy["Name"],
                            "id": policy["Id"],
                            "targets": len(targets["Targets"]),
                        }
                    )
        except Exception as e:
            click.echo(f"⚠️  Error checking SCPs: {e}")

        return scps

    def display_status(self):
        """Display comprehensive status."""
        click.echo("\n" + "=" * 60)
        click.echo(" AWS ORGANIZATION INFRASTRUCTURE STATUS")
        click.echo("=" * 60)

        # Management Account
        click.echo(f"\n📍 Management Account: {self.account_id}")
        click.echo(f"   Account Name: {self.account_name}")

        # OU Structure
        click.echo("\n🏗️  Organization Unit Structure:")
        ou_structure = self.check_ou_structure()

        if ou_structure.get("workloads"):
            click.echo(f"   ✅ Workloads OU: {ou_structure['workloads']}")
            if ou_structure.get("production"):
                click.echo(f"      ✅ Production: {ou_structure['production']}")
            else:
                click.echo("      ❌ Production: Not found")
            if ou_structure.get("staging"):
                click.echo(f"      ✅ Staging: {ou_structure['staging']}")
            else:
                click.echo("      ❌ Staging: Not found")
        else:
            click.echo("   ❌ Workloads OU: Not found")

        if ou_structure.get("sandbox"):
            click.echo(f"   ✅ Sandbox OU: {ou_structure['sandbox']}")

        # Count accounts in each OU
        click.echo("\n📊 Account Distribution:")
        for name, ou_id in ou_structure.items():
            if ou_id:
                try:
                    accounts = self.org.list_accounts_for_parent(ParentId=ou_id)["Accounts"]
                    if accounts:
                        click.echo(f"   {name.title()}: {len(accounts)} account(s)")
                        for acc in accounts[:3]:  # Show first 3
                            click.echo(f"      • {acc['Name']} ({acc['Id']})")
                        if len(accounts) > 3:
                            click.echo(f"      ... and {len(accounts) - 3} more")
                except:
                    pass

        # StackSets
        click.echo("\n📦 Deployed StackSets:")
        stacksets = self.check_stacksets()

        # Dynamically discover expected StackSets from directories
        from pathlib import Path

        project_root = Path(__file__).parent.parent
        stacksets_dir = project_root / "stacksets"

        expected = []
        if stacksets_dir.exists():
            for item in sorted(stacksets_dir.iterdir()):
                if item.is_dir() and not item.name.startswith("."):
                    template_file = item / "template.yaml"
                    if template_file.exists():
                        expected.append(item.name)

        if stacksets:
            [ss["name"] for ss in stacksets]

            # Check each expected StackSet
            for expected_name in expected:
                # Convert to org-* naming convention (01-foo becomes org-foo)
                if expected_name[0].isdigit():
                    org_name = "org-" + expected_name.split("-", 1)[1]
                else:
                    org_name = expected_name

                found = False
                for ss in stacksets:
                    if ss["name"] == org_name or expected_name in ss["name"]:
                        auto = "🔄" if ss["auto_deploy"] else "🔒"
                        click.echo(f"   ✅ {ss['name']} {auto}")
                        click.echo(f"      Instances: {ss['instance_count']}")
                        found = True
                        break
                if not found:
                    click.echo(f"   ⚠️  {expected_name}: Not deployed")

            # Show any extra StackSets (e.g., Control Tower managed)
            expected_org_names = [
                "org-" + e.split("-", 1)[1] if e[0].isdigit() else e for e in expected
            ]
            for ss in stacksets:
                if ss["name"] not in expected_org_names and not any(
                    e in ss["name"] for e in expected
                ):
                    if "AWSControlTower" in ss["name"]:
                        click.echo(f"   ℹ️  {ss['name']} (Control Tower)")
                    else:
                        click.echo(f"   ℹ️  {ss['name']} (additional)")
        else:
            click.echo("   ❌ No StackSets deployed")

        # SCPs
        click.echo("\n🔒 Service Control Policies:")
        scps = self.check_scps()

        if any(scp["name"] == "workloads-baseline" for scp in scps):
            for scp in scps:
                if scp["name"] == "workloads-baseline":
                    click.echo(f"   ✅ {scp['name']}")
                    click.echo(f"      Attached to: {scp['targets']} target(s)")
        else:
            click.echo("   ⚠️  workloads-baseline: Not found")

        # Summary
        click.echo("\n" + "=" * 60)
        click.echo(" DEPLOYMENT CHECKLIST")
        click.echo("=" * 60)

        checks = []

        # Check OUs
        if (
            ou_structure.get("workloads")
            and ou_structure.get("production")
            and ou_structure.get("staging")
        ):
            checks.append(("OU Structure", True))
        else:
            checks.append(("OU Structure", False))

        # Check StackSets
        if len(stacksets) >= 4:  # At least the core 4
            checks.append(("Core StackSets", True))
        else:
            checks.append(("Core StackSets", False))

        # Check SCPs
        if any(scp["name"] == "workloads-baseline" for scp in scps):
            checks.append(("Security Policies", True))
        else:
            checks.append(("Security Policies", False))

        # Display checklist
        all_good = True
        for check, status in checks:
            icon = "✅" if status else "❌"
            click.echo(f"   {icon} {check}")
            if not status:
                all_good = False

        if all_good:
            click.echo("\n🎉 All systems operational! New accounts will auto-provision.")
        else:
            click.echo("\n⚠️  Some components need deployment. Run 'make deploy' to fix.")

        click.echo("\n" + "=" * 60 + "\n")


@click.command()
@click.option("--profile", default=os.getenv("AWS_PROFILE"), help="AWS profile to use")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def main(profile: str, output_json: bool):
    """Show deployment status of organization infrastructure."""

    status = DeploymentStatus(profile)

    if output_json:
        # TODO: Implement JSON output
        click.echo("JSON output not yet implemented", err=True)
        sys.exit(1)
    else:
        status.display_status()


if __name__ == "__main__":
    main()
