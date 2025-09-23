"""Main CLI entry point for AI-ORG AWS Organization management tool.

This module defines the primary command-line interface for AI-ORG, including:
- Command-line argument parsing and validation
- Global configuration and context management
- Error handling and user-friendly output formatting
- Integration with all command modules (account, SSO, StackSet, config)

The CLI supports both interactive usage and automation through JSON output modes,
making it suitable for both manual operations and CI/CD pipeline integration.

Example:
    Basic CLI usage::

        $ ai-org --help
        $ ai-org account create lls-staging lls-staging@company.com --wait
        $ ai-org sso assign 123456789012 --principal jane@company.com
        $ ai-org stackset status 123456789012 --wait
"""

import sys
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console

from ai_org.__version__ import __version__
from ai_org.commands import account, config, sso, stackset
from ai_org.utils.output import OutputFormatter

# Load .env file from current directory if it exists
load_dotenv()

console = Console()
output = OutputFormatter()


@click.group(invoke_without_command=True)
@click.option(
    "--profile",
    envvar="AWS_PROFILE",
    help="AWS profile to use (default: from config or 'org')",
)
@click.option(
    "--region",
    envvar="AWS_REGION",
    default="us-east-1",
    help="AWS region (default: from config or 'us-east-1')",
)
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--json", is_flag=True, help="Output in JSON format for automation")
@click.version_option(version=__version__, prog_name="ai-org")
@click.pass_context
def cli(
    ctx: click.Context,
    profile: Optional[str],
    region: str,
    debug: bool,
    json: bool,
) -> None:
    """AI-ORG: Manage AWS Organization accounts with Control Tower.

    This tool automates AWS account creation, SSO permission assignment,
    and StackSet deployment monitoring for Control Tower organizations.

    Args:
        ctx: Click context object for passing data between commands
        profile: AWS profile name to use (defaults to 'org' or from environment)
        region: AWS region to operate in (defaults to 'us-east-1')
        debug: Enable debug logging for troubleshooting
        json: Output results in JSON format for automation

    Quick start:
      ai-org config init        # Initialize configuration
      ai-org account create     # Create new account
      ai-org sso assign         # Assign SSO permissions

    Environment Variables:
        AWS_PROFILE: Default AWS profile name
        AWS_REGION: Default AWS region
    """
    # Store options in context
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile
    ctx.obj["region"] = region
    ctx.obj["debug"] = debug
    ctx.obj["json"] = json
    ctx.obj["output"] = output

    # Set output format
    output.set_json_mode(json)

    # Show help if no command provided
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Add command groups
cli.add_command(account.account)
cli.add_command(sso.sso)
cli.add_command(stackset.stackset)
cli.add_command(config.config)


def main() -> int:
    """Main entry point for the CLI application.

    Handles top-level exception catching and returns appropriate exit codes
    for different types of errors encountered during execution.

    Returns:
        Exit code: 0 for success, 1 for general errors, 130 for keyboard interrupt

    Raises:
        SystemExit: Always exits with appropriate code based on execution result
    """
    try:
        cli()
        return 0
    except click.ClickException as e:
        e.show()
        return 1
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        return 130
    except Exception as e:
        if "--debug" in sys.argv:
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
