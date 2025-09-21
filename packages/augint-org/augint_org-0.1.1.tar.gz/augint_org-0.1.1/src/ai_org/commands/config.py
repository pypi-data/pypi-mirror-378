"""Configuration management commands."""

import click

from ai_org.core.config_manager import ConfigManager


@click.group()
def config() -> None:
    """Manage ai-org configuration."""


@config.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """Initialize configuration file with interactive setup.

    This will:
    1. Prompt for your SSO email
    2. Discover SSO instance and Identity Store
    3. Find default OU (Workloads)
    4. Save configuration to ~/.aillc/config.yaml

    \b
    Example:
      ai-org config init
    """
    output = ctx.obj["output"]
    manager = ConfigManager()

    output.info("Initializing AI-ORG configuration...")

    # Prompt for email
    email = click.prompt("Enter your SSO email", type=str)

    output.progress("Discovering SSO configuration...")

    try:
        # Initialize config with discovery
        config_data = manager.initialize(
            email=email,
            profile=ctx.obj.get("profile"),
            region=ctx.obj.get("region"),
        )

        # Save configuration
        config_path = manager.save()

        output.success(f"Configuration saved to {config_path}")
        output.info("\nConfiguration summary:")
        output.dict_display(
            {
                "SSO Email": config_data["sso"]["default_principal_email"],
                "Default OU": config_data["defaults"]["ou"],
                "SSO Instance": config_data["cache"]["sso_instance_arn"],
                "Identity Store": config_data["cache"]["identity_store_id"],
            }
        )

    except Exception as e:
        output.error(f"Failed to initialize configuration: {e}")
        raise click.ClickException(str(e)) from e


@config.command()
@click.pass_context
def show(ctx: click.Context) -> None:
    """Display current configuration.

    \b
    Example:
      ai-org config show
    """
    output = ctx.obj["output"]
    manager = ConfigManager()

    try:
        config_data = manager.load()

        if ctx.obj.get("json"):
            output.json_output(config_data)
        else:
            output.info("Current Configuration:")
            output.info(f"\nConfig file: {manager.config_path}")
            output.dict_display(config_data)

    except FileNotFoundError:
        output.warning("Configuration not found. Run 'ai-org config init' to create.")
    except Exception as e:
        output.error(f"Failed to load configuration: {e}")
        raise click.ClickException(str(e)) from e


@config.command(name="set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def set_value(ctx: click.Context, key: str, value: str) -> None:
    """Set a configuration value.

    \b
    Arguments:
      KEY     Configuration key (dot-separated path)
      VALUE   Value to set

    \b
    Examples:
      ai-org config set sso.default_principal_email jane@company.com
      ai-org config set defaults.ou ou-55d0-custom
      ai-org config set defaults.region us-west-2
    """
    output = ctx.obj["output"]
    manager = ConfigManager()

    try:
        manager.set_value(key, value)
        manager.save()
        output.success(f"Configuration updated: {key} = {value}")

    except Exception as e:
        output.error(f"Failed to update configuration: {e}")
        raise click.ClickException(str(e)) from e


@config.command()
@click.argument("key")
@click.pass_context
def get(ctx: click.Context, key: str) -> None:
    """Get a configuration value.

    \b
    Arguments:
      KEY     Configuration key (dot-separated path)

    \b
    Examples:
      ai-org config get sso.default_principal_email
      ai-org config get defaults.ou
      ai-org config get cache.identity_store_id
    """
    output = ctx.obj["output"]
    manager = ConfigManager()

    try:
        value = manager.get_value(key)
        if value is not None:
            if ctx.obj.get("json"):
                output.json_output({key: value})
            else:
                output.info(f"{key}: {value}")
        else:
            output.warning(f"Configuration key '{key}' not found")

    except Exception as e:
        output.error(f"Failed to get configuration: {e}")
        raise click.ClickException(str(e)) from e


@config.command()
@click.pass_context
def list_permission_sets(ctx: click.Context) -> None:
    """List available SSO permission sets.

    \b
    Example:
      ai-org config list-permission-sets
    """
    output = ctx.obj["output"]
    ConfigManager()

    try:
        # This would call SSO manager to list permission sets
        from ai_org.core.sso_manager import SSOManager

        sso = SSOManager(
            profile=ctx.obj.get("profile"),
            region=ctx.obj.get("region"),
        )
        permission_sets = sso.list_permission_sets()

        if ctx.obj.get("json"):
            output.json_output(permission_sets)
        else:
            output.info("Available Permission Sets:")
            for ps in permission_sets:
                output.info(f"  • {ps['Name']}: {ps.get('Description', 'No description')}")

    except Exception as e:
        output.error(f"Failed to list permission sets: {e}")
        raise click.ClickException(str(e)) from e
