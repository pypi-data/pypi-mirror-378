"""Configuration management commands."""

import os

import click
from dotenv import dotenv_values

from ai_org.core.config_manager import ConfigManager
from ai_org.core.sso_manager import SSOManager


@click.group()
def config() -> None:
    """Manage ai-org configuration."""


@config.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """Initialize configuration file with interactive setup.

    This will:
    1. Prompt for configuration values
    2. Save configuration to ~/.ai-org.env

    \b
    Example:
      ai-org config init
    """
    output = ctx.obj["output"]
    manager = ConfigManager()

    output.info("Initializing AI-ORG configuration...")
    output.info("")

    try:
        config = manager.initialize_interactive()

        output.success("\nConfiguration initialized successfully!")
        if config:
            output.info("\nConfigured values:")
            for key, value in config.items():
                output.info(f"  {key}: {value}")
    except Exception as e:
        output.error(f"Failed to initialize configuration: {e}")
        ctx.exit(1)


@config.command()
@click.pass_context
def show(ctx: click.Context) -> None:
    """Display current configuration.

    Shows the effective configuration from:
    1. Environment variables (highest priority)
    2. ~/.ai-org.env file
    3. Default values (lowest priority)

    \b
    Example:
      ai-org config show
    """
    output = ctx.obj["output"]
    manager = ConfigManager()

    try:
        config = manager.load()

        output.info("Current configuration:")
        output.info(f"  Config file: {manager.config_path}")
        output.info("")

        for key, value in sorted(config.items()):
            # Mark where the value comes from
            source = ""
            if os.getenv(key):
                source = " (from environment)"
            elif manager.config_path.exists() and key in dotenv_values(manager.config_path):
                source = " (from file)"
            else:
                source = " (default)"

            output.info(f"  {key}: {value}{source}")

        if not manager.config_path.exists():
            output.info("")
            output.info("Note: No config file exists. Run 'ai-org config init' to create one.")

    except Exception as e:
        output.error(f"Failed to show configuration: {e}")
        ctx.exit(1)


@config.command(name="set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def set_value(ctx: click.Context, key: str, value: str) -> None:
    """Set a configuration value.

    \b
    Arguments:
      KEY     Configuration key
      VALUE   Value to set

    \b
    Examples:
      ai-org config set AWS_PROFILE org
      ai-org config set DEFAULT_SSO_EMAIL user@example.com
      ai-org config set BUDGETS_MONTHLY_DEFAULT 2000
    """
    output = ctx.obj["output"]
    manager = ConfigManager()

    try:
        manager.set(key, value)
        output.success(f"Set {key} = {value}")
    except Exception as e:
        output.error(f"Failed to set configuration: {e}")
        ctx.exit(1)


@config.command()
@click.argument("key")
@click.pass_context
def get(ctx: click.Context, key: str) -> None:
    """Get a configuration value.

    \b
    Arguments:
      KEY     Configuration key

    \b
    Examples:
      ai-org config get AWS_PROFILE
      ai-org config get DEFAULT_SSO_EMAIL
    """
    output = ctx.obj["output"]
    manager = ConfigManager()

    try:
        value = manager.get(key)
        if value:
            if ctx.obj.get("json"):
                output.json_output({key: value})
            else:
                output.info(value)
        else:
            output.warning(f"Configuration key '{key}' not found")
    except Exception as e:
        output.error(f"Failed to get configuration: {e}")
        ctx.exit(1)


@config.command()
@click.pass_context
def list_permission_sets(ctx: click.Context) -> None:
    """List available SSO permission sets.

    \b
    Example:
      ai-org config list-permission-sets
    """
    output = ctx.obj["output"]
    config = ConfigManager()

    try:
        # Get AWS profile from config
        profile = config.get_aws_profile()

        sso = SSOManager(profile=profile, region=ctx.obj.get("region"))
        permission_sets = sso.list_permission_sets()

        if ctx.obj.get("json"):
            output.json_output(permission_sets)
        else:
            output.info("Available permission sets:")
            for ps in permission_sets:
                output.info(f"  • {ps['name']}")
                if ps.get("description"):
                    output.info(f"    {ps['description']}")

    except Exception as e:
        output.error(f"Failed to list permission sets: {e}")
        ctx.exit(1)


@config.command()
@click.pass_context
def reset(ctx: click.Context) -> None:
    """Reset configuration to defaults.

    This will delete ~/.ai-org.env if it exists.

    \b
    Example:
      ai-org config reset
    """
    output = ctx.obj["output"]
    manager = ConfigManager()

    if manager.exists():
        if click.confirm(f"Delete {manager.config_path}?"):
            manager.delete()
            output.success("Configuration reset to defaults")
        else:
            output.info("Reset cancelled")
    else:
        output.info("No configuration file exists")
