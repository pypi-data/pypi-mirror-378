"""Simple configuration management for ai-org using .env files."""

import os
from pathlib import Path
from typing import Any, ClassVar, Optional

from dotenv import dotenv_values, set_key


class ConfigManager:
    """Manages ai-org configuration using .env files."""

    # Default values for configuration
    DEFAULTS: ClassVar[dict[str, str]] = {
        "AWS_PROFILE": "default",
        "DEFAULT_PERMISSION_SET": "AWSAdministratorAccess",
        "BUDGETS_MONTHLY_DEFAULT": "1000",
        "BUDGETS_ANOMALY_THRESHOLD": "100",
    }

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager.

        Args:
            config_path: Path to config file (defaults to ~/.ai-org.env)
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".ai-org.env"

    def load(self) -> dict[str, Any]:
        """Load configuration from file and environment.

        Returns config with precedence:
        1. Environment variables (highest)
        2. Config file
        3. Defaults (lowest)
        """
        config = {}

        # Start with defaults
        config.update(self.DEFAULTS)

        # Override with config file if it exists
        if self.config_path.exists():
            file_config = dotenv_values(self.config_path)
            # Only include non-empty values
            config.update({k: v for k, v in file_config.items() if v})

        # Override with environment variables
        for key in self.DEFAULTS:
            env_value = os.getenv(key)
            if env_value:
                config[key] = env_value

        # Also check for some common env vars
        sso_email = os.getenv("DEFAULT_SSO_EMAIL")
        if sso_email:
            config["DEFAULT_SSO_EMAIL"] = sso_email
        elif self.config_path.exists():
            file_value = dotenv_values(self.config_path).get("DEFAULT_SSO_EMAIL")
            if file_value:
                config["DEFAULT_SSO_EMAIL"] = file_value

        notif_email = os.getenv("NOTIFICATIONS_EMAIL")
        if notif_email:
            config["NOTIFICATIONS_EMAIL"] = notif_email
        elif self.config_path.exists():
            file_value = dotenv_values(self.config_path).get("NOTIFICATIONS_EMAIL")
            if file_value:
                config["NOTIFICATIONS_EMAIL"] = file_value

        return config

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        config = self.load()
        return config.get(key, default)

    def set(self, key: str, value: str) -> None:
        """Set a configuration value in the file.

        Args:
            key: Configuration key
            value: Value to set
        """
        # Create config file if it doesn't exist
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.touch()

        # Set the key in the file
        set_key(str(self.config_path), key, value)

    def initialize_interactive(self) -> dict[str, str]:
        """Initialize configuration file with interactive prompts.

        Returns:
            The configured values
        """
        import click

        click.echo("Creating ~/.ai-org.env configuration...")
        click.echo()

        config: dict[str, str] = {}

        # Only prompt for values that are actually saved and used
        prompts = [
            (
                "AWS_PROFILE",
                "AWS profile for organization management",
                self.DEFAULTS["AWS_PROFILE"],
            ),
            (
                "DEFAULT_SSO_EMAIL",
                "Your SSO email for account access (used when --principal not specified)",
                None,
            ),
            (
                "NOTIFICATIONS_EMAIL",
                "Email for budget alerts and account notifications (optional, uses SSO email if blank)",
                None,
            ),
        ]

        for key, prompt_text, default in prompts:
            if default:
                value = click.prompt(prompt_text, default=default, show_default=True)
                # If user just hit enter on a default, don't save it
                if value == default:
                    continue
            else:
                value = click.prompt(prompt_text, default="", show_default=False)
                # If user didn't enter anything, skip
                if not value:
                    # For NOTIFICATIONS_EMAIL, if blank, we can use DEFAULT_SSO_EMAIL as fallback
                    if key == "NOTIFICATIONS_EMAIL" and config.get("DEFAULT_SSO_EMAIL"):
                        click.echo(
                            f"  → Will use SSO email ({config['DEFAULT_SSO_EMAIL']}) for notifications"
                        )
                    continue

            config[key] = value
            self.set(key, value)

        click.echo()
        click.echo(f"Configuration saved to {self.config_path}")
        return config

    def exists(self) -> bool:
        """Check if configuration file exists."""
        return self.config_path.exists()

    def delete(self) -> None:
        """Delete the configuration file."""
        if self.config_path.exists():
            self.config_path.unlink()

    # Simplified methods for common values
    def get_aws_profile(self) -> str:
        """Get AWS profile name."""
        return self.get("AWS_PROFILE", "default") or "default"

    def get_default_sso_email(self) -> Optional[str]:
        """Get default SSO email."""
        return self.get("DEFAULT_SSO_EMAIL")

    def get_default_permission_set(self) -> str:
        """Get default permission set."""
        return (
            self.get("DEFAULT_PERMISSION_SET", "AWSAdministratorAccess") or "AWSAdministratorAccess"
        )

    def get_notifications_email(self) -> Optional[str]:
        """Get notifications email."""
        return self.get("NOTIFICATIONS_EMAIL")

    def get_monthly_budget(self) -> int:
        """Get monthly budget."""
        value = self.get("BUDGETS_MONTHLY_DEFAULT", "1000")
        return int(value or "1000")

    def get_anomaly_threshold(self) -> int:
        """Get anomaly threshold."""
        value = self.get("BUDGETS_ANOMALY_THRESHOLD", "100")
        return int(value or "100")
