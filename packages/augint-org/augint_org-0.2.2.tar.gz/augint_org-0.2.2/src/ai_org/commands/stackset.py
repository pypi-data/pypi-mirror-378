"""StackSet management commands."""

from typing import Optional

import click

from ai_org.core.stackset_manager import StackSetManager


@click.group()
def stackset() -> None:
    """Monitor StackSet deployments."""


@stackset.command()
@click.argument("account-id")
@click.option("--stackset", help="Specific StackSet name (default: all)")
@click.option("--wait", is_flag=True, help="Wait for deployments to complete")
@click.pass_context
def status(ctx: click.Context, account_id: str, stackset: Optional[str], wait: bool) -> None:
    """Check StackSet deployment status for an account.

    \b
    Arguments:
      ACCOUNT-ID    AWS account ID (12 digits)

    \b
    Options:
      --stackset TEXT    Specific StackSet name (default: all)
      --wait            Wait for deployments to complete

    \b
    Examples:
      ai-org stackset status 123456789012
      ai-org stackset status 123456789012 --wait
      ai-org stackset status 123456789012 --stackset org-pipeline-bootstrap
    """
    output = ctx.obj["output"]
    manager = StackSetManager(
        profile=ctx.obj.get("profile"),
        region=ctx.obj.get("region"),
    )

    try:
        if wait:
            output.progress(f"Waiting for StackSet deployments in {account_id}...")
            success = manager.wait_for_deployments(account_id, stackset_name=stackset)
            if success:
                output.success("All StackSets deployed successfully")
            else:
                output.warning("Some StackSets may have failed or are still deploying")

        # Get current status
        statuses = manager.get_deployment_status(account_id, stackset_name=stackset)

        if ctx.obj.get("json"):
            output.json_output(statuses)
        elif statuses:
            output.table(
                statuses,
                columns=["StackSetName", "Status", "StatusReason"],
                title=f"StackSet Status for {account_id}",
            )
        else:
            output.info(f"No StackSets found for account {account_id}")

    except Exception as e:
        output.error(f"Failed to check StackSet status: {e}")
        raise click.ClickException(str(e)) from e


@stackset.command(name="list")
@click.pass_context
def list_stacksets(ctx: click.Context) -> None:
    """List all StackSets in the organization.

    \b
    Example:
      ai-org stackset list
    """
    output = ctx.obj["output"]
    manager = StackSetManager(
        profile=ctx.obj.get("profile"),
        region=ctx.obj.get("region"),
    )

    try:
        stacksets = manager.list_stacksets()

        if ctx.obj.get("json"):
            output.json_output(stacksets)
        elif stacksets:
            output.table(
                stacksets,
                columns=["StackSetName", "Status", "AutoDeployment", "Capabilities"],
                title="Organization StackSets",
            )
        else:
            output.info("No StackSets found")

    except Exception as e:
        output.error(f"Failed to list StackSets: {e}")
        raise click.ClickException(str(e)) from e
