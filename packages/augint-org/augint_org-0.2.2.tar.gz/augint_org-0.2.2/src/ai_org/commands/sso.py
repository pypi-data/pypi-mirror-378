"""SSO management commands."""

import os
from typing import Optional

import click

from ai_org.core.config_manager import ConfigManager
from ai_org.core.sso_manager import SSOManager


@click.group()
def sso() -> None:
    """Manage SSO permissions for accounts."""


@sso.command()
@click.argument("account-id")
@click.option("--principal", help="Email or group name (default: from config)")
@click.option(
    "--permission-set",
    default="AWSAdministratorAccess",
    help="Permission set name (default: AWSAdministratorAccess)",
)
@click.option(
    "--principal-type",
    type=click.Choice(["USER", "GROUP"]),
    help="USER or GROUP (auto-detected if not specified)",
)
@click.pass_context
def assign(
    ctx: click.Context,
    account_id: str,
    principal: Optional[str],
    permission_set: str,
    principal_type: Optional[str],
) -> None:
    """Assign SSO permissions to an account.

    \b
    Arguments:
      ACCOUNT-ID    AWS account ID (12 digits)

    \b
    Options:
      --principal TEXT         Email or group name (default: from config)
      --permission-set TEXT    Permission set name (default: AWSAdministratorAccess)
      --principal-type TEXT    USER or GROUP (auto-detected if not specified)

    \b
    Examples:
      # Uses email from config
      ai-org sso assign 123456789012

      # Explicit principal
      ai-org sso assign 123456789012 --principal jane@company.com

      # Group assignment
      ai-org sso assign 123456789012 --principal Developers --principal-type GROUP
    """
    output = ctx.obj["output"]
    config = ConfigManager()

    # Use principal from config if not specified
    if not principal:
        principal = config.get_default_sso_email()
        if not principal:
            raise click.ClickException(
                "No principal specified and no default in config. "
                "Run 'ai-org config init' or provide --principal"
            )

    output.info(f"Assigning SSO permissions to account {account_id}...")

    manager = SSOManager(
        profile=ctx.obj.get("profile"),
        region=ctx.obj.get("region"),
    )

    try:
        result = manager.assign_permission(
            account_id=account_id,
            principal=principal,
            permission_set=permission_set,
            principal_type=principal_type,
        )

        output.success(f"SSO access granted: {principal} → {account_id} ({permission_set})")

        if ctx.obj.get("json"):
            output.json_output(result)

    except Exception as e:
        output.error(f"Failed to assign SSO permissions: {e}")
        raise click.ClickException(str(e)) from e


@sso.command(name="list")
@click.argument("account-id")
@click.pass_context
def list_assignments(ctx: click.Context, account_id: str) -> None:
    """List SSO assignments for an account.

    \b
    Arguments:
      ACCOUNT-ID    AWS account ID (12 digits)

    \b
    Example:
      ai-org sso list 123456789012
    """
    output = ctx.obj["output"]
    manager = SSOManager(
        profile=ctx.obj.get("profile"),
        region=ctx.obj.get("region"),
    )

    try:
        assignments = manager.list_assignments(account_id)

        if ctx.obj.get("json"):
            output.json_output(assignments)
        elif assignments:
            output.table(
                assignments,
                columns=["PrincipalType", "PrincipalId", "PermissionSet", "Status"],
                title=f"SSO Assignments for {account_id}",
            )
        else:
            output.info(f"No SSO assignments found for account {account_id}")

    except Exception as e:
        output.error(f"Failed to list SSO assignments: {e}")
        raise click.ClickException(str(e)) from e


@sso.command()
@click.option("--ou", help="Sync only accounts in this OU")
@click.option(
    "--permission-set",
    default="AWSAdministratorAccess",
    help="Which permission set to sync",
)
@click.option("--principal", help="Principal to sync (default: from config)")
@click.pass_context
def sync(
    ctx: click.Context,
    ou: Optional[str],
    permission_set: str,
    principal: Optional[str],
) -> None:
    """Sync SSO permissions across multiple accounts.

    \b
    Options:
      --ou TEXT               Sync only accounts in this OU
      --permission-set TEXT   Which permission set to sync
      --principal TEXT        Principal to sync (default: from config)

    \b
    Examples:
      # Sync default principal to all Workloads accounts
      ai-org sso sync --ou ou-55d0-workloads

      # Sync specific principal
      ai-org sso sync --principal developer@company.com
    """
    output = ctx.obj["output"]
    config = ConfigManager()

    # Use principal from config if not specified
    if not principal:
        principal = config.get_default_sso_email()
        if not principal:
            raise click.ClickException(
                "No principal specified and no default in config. "
                "Run 'ai-org config init' or provide --principal"
            )

    # Use OU from environment if not specified
    if not ou:
        ou = os.getenv("DEFAULT_OU")

    output.info(f"Syncing SSO permissions for {principal}...")

    manager = SSOManager(
        profile=ctx.obj.get("profile"),
        region=ctx.obj.get("region"),
    )

    try:
        results = manager.sync_ou_assignments(
            principal=principal,
            permission_set=permission_set,
            ou_id=ou,
        )

        success_count = sum(1 for r in results if r.get("status") == "success")
        output.success(f"SSO sync complete: {success_count}/{len(results)} accounts updated")

        if ctx.obj.get("json"):
            output.json_output(results)
        else:
            for result in results:
                if result["status"] == "success":
                    output.success(f"  ✓ {result['account_id']}: {result['message']}")
                else:
                    output.warning(f"  ✗ {result['account_id']}: {result['message']}")

    except Exception as e:
        output.error(f"Failed to sync SSO permissions: {e}")
        raise click.ClickException(str(e)) from e
