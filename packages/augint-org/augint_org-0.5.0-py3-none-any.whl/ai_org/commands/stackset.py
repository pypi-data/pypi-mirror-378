"""StackSet management commands."""

from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_org.core.stackset_manager import StackSetManager

console = Console()


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


@stackset.command()
@click.argument("account-id")
@click.option("--stackset", required=True, help="StackSet name to deploy")
@click.option("--param", multiple=True, help="Parameter as key=value (can be used multiple times)")
@click.option(
    "--regions",
    help="Comma-separated list of regions (default: us-east-1,us-west-2)",
    default="us-east-1,us-west-2",
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def deploy(
    ctx: click.Context,
    account_id: str,
    stackset: str,
    param: tuple[str],
    regions: str,
    yes: bool,
) -> None:
    """Deploy a StackSet to a specific account.

    \b
    Arguments:
      ACCOUNT-ID    AWS account ID (12 digits)

    \b
    Options:
      --stackset TEXT    StackSet name to deploy (required)
      --param TEXT       Parameter as key=value (can be used multiple times)
      --regions TEXT     Comma-separated regions (default: us-east-1,us-west-2)
      --yes, -y          Skip confirmation prompt

    \b
    Examples:
      # Deploy with interactive parameter prompts
      ai-org stackset deploy 123456789012 --stackset pipeline-bootstrap-stackset

      # Deploy with all parameters provided
      ai-org stackset deploy 123456789012 \\
        --stackset github-oidc-stackset \\
        --param GitHubOrg=myorg \\
        --param RepoPattern=* \\
        --regions us-east-1 \\
        --yes
    """
    output = ctx.obj["output"]
    manager = StackSetManager(
        profile=ctx.obj.get("profile"),
        region=ctx.obj.get("region"),
    )

    try:
        # Parse regions
        region_list = [r.strip() for r in regions.split(",")]

        # Parse provided parameters
        provided_params = {}
        for p in param:
            try:
                key, value = p.split("=", 1)
                provided_params[key] = value
            except ValueError:
                output.error(f"Invalid parameter format: {p}. Use key=value")
                raise click.ClickException(
                    f"Invalid parameter format: {p}. Use key=value"
                ) from None

        # Get parameter definitions from the StackSet
        output.info(f"Querying {stackset} parameters...")
        param_definitions = manager.get_stackset_parameters(stackset)

        # Collect all parameters (provided + interactive prompts for missing)
        final_params = {}

        if param_definitions and not yes:
            click.echo()
            click.echo("Enter parameters (press Enter for default):")

            for param_def in param_definitions:
                param_name = param_def["name"]

                # Skip if already provided via CLI
                if param_name in provided_params:
                    final_params[param_name] = provided_params[param_name]
                    continue

                # Build prompt text
                prompt_text = param_name
                if param_def.get("description"):
                    prompt_text = f"{param_name} - {param_def['description']}"

                # Determine default value
                default_value = param_def.get("current_value") or param_def.get("default")

                # Interactive prompt
                if default_value:
                    value = click.prompt(
                        prompt_text,
                        default=default_value,
                        show_default=True,
                    )
                else:
                    value = click.prompt(
                        prompt_text,
                        default="",
                        show_default=False,
                    )
                    if not value:
                        continue  # Skip if no value provided and no default

                final_params[param_name] = value
        else:
            # Use only provided parameters
            final_params = provided_params

        # Show confirmation unless --yes is provided
        if not yes:
            click.echo()

            # Create confirmation table
            table = Table(show_header=False, box=None)
            table.add_column(style="cyan", width=20)
            table.add_column()

            table.add_row("StackSet:", stackset)
            table.add_row("Account:", account_id)
            table.add_row("Regions:", ", ".join(region_list))

            if final_params:
                table.add_row("", "")  # Empty row for spacing
                table.add_row("Parameters:", "")
                for key, value in final_params.items():
                    table.add_row(f"  • {key}:", value)

            panel = Panel(
                table,
                title="[bold yellow]DEPLOYMENT CONFIRMATION[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
            console.print(panel)

            click.echo()
            if not click.confirm("Proceed with deployment?"):
                output.warning("Deployment cancelled")
                return

        # Execute deployment
        output.progress(f"Deploying {stackset} to account {account_id}...")

        operation_id = manager.deploy_to_account(
            account_id=account_id,
            stackset_name=stackset,
            parameters=final_params,
            regions=region_list,
        )

        output.info(f"Deployment started. Operation ID: {operation_id}")

        # Wait for deployment to complete
        output.progress("Waiting for deployment to complete...")

        success = manager.wait_for_deployment_operation(
            stackset_name=stackset,
            operation_id=operation_id,
            timeout=600,
        )

        if success:
            output.success(f"Successfully deployed {stackset} to account {account_id}")

            # Show final status
            statuses = manager.get_deployment_status(account_id, stackset_name=stackset)
            if statuses:
                output.table(
                    statuses,
                    columns=["StackSetName", "Status", "StatusReason"],
                    title="Deployment Status",
                )
        else:
            output.error("Deployment failed or timed out")

            # Show current status
            statuses = manager.get_deployment_status(account_id, stackset_name=stackset)
            if statuses:
                output.table(
                    statuses,
                    columns=["StackSetName", "Status", "StatusReason"],
                    title="Current Status",
                )

    except Exception as e:
        output.error(f"Failed to deploy StackSet: {e}")
        raise click.ClickException(str(e)) from e
