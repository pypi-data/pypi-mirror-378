"""Account management commands."""

import os
from typing import Optional

import click

from ai_org.core.account_manager import AccountManager
from ai_org.core.config_manager import ConfigManager
from ai_org.core.sso_manager import SSOManager
from ai_org.core.stackset_manager import StackSetManager


@click.group()
def account() -> None:
    """Manage AWS accounts in the organization."""


@account.command()
@click.argument("name")
@click.argument("email")
@click.option("--ou", help="Target OU ID (required if not in environment)")
@click.option("--wait", is_flag=True, help="Wait for account creation to complete")
@click.option("--skip-sso", is_flag=True, help="Skip automatic SSO assignment")
@click.option("--skip-stacksets", is_flag=True, help="Skip waiting for StackSet deployment")
@click.pass_context
def create(
    ctx: click.Context,
    name: str,
    email: str,
    ou: Optional[str],
    wait: bool,
    skip_sso: bool,
    skip_stacksets: bool,
) -> None:
    """Create a new AWS account in the organization.

    \b
    Arguments:
      NAME    Account name (e.g., "lls-staging")
      EMAIL   Root email address for the account

    \b
    Examples:
      ai-org account create lls-staging lls-staging@company.com --wait
      ai-org account create myapp-prod myapp-prod@company.com --ou ou-55d0-custom
    """
    output = ctx.obj["output"]
    config = ConfigManager()

    # OU is required - user must specify target OU
    if not ou:
        # Try to get from environment
        ou = os.getenv("DEFAULT_OU")
        if not ou:
            raise click.ClickException(
                "No OU specified. Use --ou to specify target OU ID or set DEFAULT_OU environment variable."
            )

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
@click.pass_context
def list_accounts(ctx: click.Context, ou: Optional[str], status: str) -> None:
    """List accounts in the organization.

    \b
    Examples:
      ai-org account list
      ai-org account list --ou ou-55d0-workloads
      ai-org account list --status SUSPENDED
    """
    output = ctx.obj["output"]
    manager = AccountManager(
        profile=ctx.obj.get("profile"),
        region=ctx.obj.get("region"),
    )

    try:
        accounts = manager.list_accounts(ou=ou, status=status)
        if ctx.obj.get("json"):
            output.json_output(accounts)
        else:
            output.table(
                accounts,
                columns=["Id", "Name", "Email", "Status"],
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
