"""Account management commands."""

import os
from typing import Optional

import click

from ai_org.core.account_manager import AccountManager
from ai_org.core.config_manager import ConfigManager
from ai_org.core.ou_manager import OUManager
from ai_org.core.sso_manager import SSOManager
from ai_org.core.stackset_manager import StackSetManager


@click.group()
def account() -> None:
    """Manage AWS accounts in the organization."""


@account.command()
@click.argument("name")
@click.argument("email")
@click.option("--ou", help="Target OU ID or name (required if not in environment)")
@click.option("--wait", is_flag=True, help="Wait for account creation to complete")
@click.option("--skip-sso", is_flag=True, help="Skip automatic SSO assignment")
@click.option("--skip-stacksets", is_flag=True, help="Skip waiting for StackSet deployment")
@click.option("--list-ous", is_flag=True, help="List available OUs and exit")
@click.pass_context
def create(
    ctx: click.Context,
    name: str,
    email: str,
    ou: Optional[str],
    wait: bool,
    skip_sso: bool,
    skip_stacksets: bool,
    list_ous: bool,
) -> None:
    """Create a new AWS account in the organization.

    \b
    Arguments:
      NAME    Account name (e.g., "lls-staging")
      EMAIL   Root email address for the account

    \b
    Examples:
      ai-org account create lls-staging lls-staging@company.com --wait
      ai-org account create myapp-prod myapp-prod@company.com --ou Production
      ai-org account create myapp-prod myapp-prod@company.com --ou ou-55d0-custom

    \b
    List available OUs:
      ai-org account create dummy dummy --list-ous
    """
    output = ctx.obj["output"]
    config = ConfigManager()

    # If --list-ous, show OUs and exit
    if list_ous:
        ou_manager = OUManager(
            profile=ctx.obj.get("profile"),
            region=ctx.obj.get("region"),
        )
        try:
            ous = ou_manager.list_ous()
            # Filter out ROOT
            ous_filtered = [ou for ou in ous if ou["Type"] != "ROOT"]
            output.table(
                ous_filtered,
                columns=["Id", "Name", "Path"],
                title="Available OUs for Account Creation",
            )
            return
        except Exception as e:
            output.error(f"Failed to list OUs: {e}")
            raise click.ClickException(str(e)) from e

    # OU is required - user must specify target OU
    if not ou:
        # Try to get from environment
        ou = os.getenv("DEFAULT_OU")
        if not ou:
            output.error("No OU specified. Use --ou to specify target OU.")
            output.info("\nTip: Use --list-ous to see available OUs:")
            output.text("  ai-org account create dummy dummy --list-ous")
            raise click.ClickException("Missing required --ou parameter")

    # Check if ou is a name rather than an ID
    if not ou.startswith("ou-") and not ou.startswith("r-"):
        ou_manager = OUManager(
            profile=ctx.obj.get("profile"),
            region=ctx.obj.get("region"),
        )
        output.info(f"Looking up OU by name: {ou}")
        ou_id = ou_manager.get_ou_by_name(ou)
        if ou_id:
            output.success(f"Found OU '{ou}': {ou_id}")
            ou = ou_id
        else:
            output.error(f"No OU found with name '{ou}'")
            # Try to suggest similar OUs
            try:
                ous = ou_manager.list_ous()
                similar = [
                    o for o in ous if ou.lower() in o["Name"].lower() and o["Type"] != "ROOT"
                ]
                if similar:
                    output.info("\nDid you mean one of these?")
                    for o in similar:
                        output.text(f"  - {o['Name']} ({o['Id']})")
            except Exception:
                pass
            raise click.ClickException(f"OU not found: {ou}")

    output.info(f"Creating account '{name}'...")

    # Create account
    manager = AccountManager(
        profile=ctx.obj.get("profile"),
        region=ctx.obj.get("region"),
    )

    try:
        account_id = manager.create_account(name, email, ou, wait=wait)
        output.success(f"Account created: {account_id}")

        # Assign SSO permissions
        if not skip_sso:
            output.progress("Assigning SSO permissions...")
            sso = SSOManager(
                profile=ctx.obj.get("profile"),
                region=ctx.obj.get("region"),
            )

            principal = config.get_default_sso_email()
            if principal:
                sso.assign_permission(
                    account_id,
                    principal,
                    config.get_default_permission_set(),
                )
                output.success(f"SSO access granted to {principal}")
            else:
                output.warning("No default principal configured, skipping SSO assignment")

        # Wait for StackSets
        if not skip_stacksets and wait:
            output.progress("Waiting for StackSets...")
            stackset = StackSetManager(
                profile=ctx.obj.get("profile"),
                region=ctx.obj.get("region"),
            )
            if stackset.wait_for_deployments(account_id):
                output.success("StackSets deployed")
            else:
                output.warning("Some StackSets may still be deploying")

        output.info("\nAccount ready for use!")
        if ctx.obj.get("json"):
            output.json_output(
                {
                    "account_id": account_id,
                    "name": name,
                    "email": email,
                    "ou_id": ou,
                    "sso_assigned": not skip_sso and bool(principal),
                    "stacksets_deployed": not skip_stacksets and wait,
                }
            )

    except Exception as e:
        output.error(f"Failed to create account: {e}")
        raise click.ClickException(str(e)) from e


@account.command(name="list")
@click.option("--ou", help="Filter by OU ID")
@click.option("--status", default="ACTIVE", help="Filter by status (ACTIVE, SUSPENDED)")
@click.option("--no-tree", is_flag=True, help="Don't show OU tree structure")
@click.pass_context
def list_accounts(ctx: click.Context, ou: Optional[str], status: str, no_tree: bool) -> None:
    """List accounts in the organization.

    \b
    Examples:
      ai-org account list
      ai-org account list --ou ou-55d0-workloads
      ai-org account list --status SUSPENDED
      ai-org account list --no-tree  # Skip OU tree display
    """
    output = ctx.obj["output"]
    manager = AccountManager(
        profile=ctx.obj.get("profile"),
        region=ctx.obj.get("region"),
    )

    try:
        # Show OU structure first (unless --no-tree or --json)
        if not no_tree and not ctx.obj.get("json"):
            ou_manager = OUManager(
                profile=ctx.obj.get("profile"),
                region=ctx.obj.get("region"),
            )
            try:
                ou_tree = ou_manager.get_ou_tree()
                output.info("Organization Structure:")
                tree_str = ou_manager.format_ou_tree(ou_tree)
                output.text(tree_str)
                output.text("")  # Empty line for spacing
            except Exception:
                # If we can't get OU tree, just skip it
                pass

        # Get accounts with OU information
        accounts = manager.list_accounts_with_ou(ou=ou, status=status)

        if ctx.obj.get("json"):
            output.json_output(accounts)
        else:
            # Format OU path for display
            for account in accounts:
                # Build OU path
                if account.get("ParentType") == "ROOT":
                    account["OU"] = "Root"
                elif account.get("ParentName"):
                    account["OU"] = account["ParentName"]
                else:
                    account["OU"] = account.get("ParentId", "Unknown")

            output.table(
                accounts,
                columns=["Id", "Name", "Email", "Status", "OU"],
                title=f"AWS Accounts ({status})",
            )
    except Exception as e:
        output.error(f"Failed to list accounts: {e}")
        raise click.ClickException(str(e)) from e


@account.command()
@click.argument("account-id")
@click.pass_context
def get(ctx: click.Context, account_id: str) -> None:
    """Get details for a specific account.

    \b
    Arguments:
      ACCOUNT-ID    AWS account ID (12 digits)

    \b
    Example:
      ai-org account get 123456789012
    """
    output = ctx.obj["output"]
    manager = AccountManager(
        profile=ctx.obj.get("profile"),
        region=ctx.obj.get("region"),
    )

    try:
        account = manager.get_account(account_id)
        if ctx.obj.get("json"):
            output.json_output(account)
        else:
            output.dict_display(account, title=f"Account {account_id}")
    except Exception as e:
        output.error(f"Failed to get account: {e}")
        raise click.ClickException(str(e)) from e
