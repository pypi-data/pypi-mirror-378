"""Configuration management for ai-org."""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml

from ai_org.core.account_manager import AccountManager
from ai_org.core.aws_client import AWSClient


class ConfigManager:
    """Manages ai-org configuration and caching."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager.

        Args:
            config_path: Path to config file (defaults to ~/.aillc/config.yaml or /tmp in CI)
        """
        import os

        if config_path:
            self.config_path = Path(config_path)
        elif os.getenv("CI"):  # In CI environment
            self.config_path = Path("/tmp/.aillc/config.yaml")
        else:
            self.config_path = Path.home() / ".aillc" / "config.yaml"

        self.config: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f) or {}

    def initialize(
        self,
        email: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> dict[str, Any]:
        """Initialize configuration with discovery.

        Args:
            email: User's SSO email
            profile: AWS profile
            region: AWS region

        Returns:
            Initialized configuration dictionary
        """
        aws = AWSClient(profile, region)

        # Discover SSO configuration
        sso_client = aws.client("sso-admin")
        response = sso_client.list_instances()

        if not response.get("Instances"):
            raise Exception("No SSO instance found in this account")

        instance = response["Instances"][0]
        sso_instance_arn = instance["InstanceArn"]
        identity_store_id = instance["IdentityStoreId"]

        # Find Workloads OU
        account_manager = AccountManager(profile, region)
        workloads_ou = account_manager.get_ou_by_name("Workloads")

        # Build configuration
        self.config = {
            "sso": {
                "default_principal_email": email,
                "default_permission_set": "AWSAdministratorAccess",
                "default_principal_type": "USER",
            },
            "defaults": {
                "ou": workloads_ou or "",
                "region": region or "us-east-1",
                "profile": profile or "org",
            },
            "cache": {
                "sso_instance_arn": sso_instance_arn,
                "identity_store_id": identity_store_id,
                "user_mappings": {},
                "last_updated": datetime.now().isoformat(),
            },
        }

        return self.config

    def save(self) -> Path:
        """Save configuration to file.

        Returns:
            Path to saved configuration file
        """
        # Create directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Update last_updated timestamp
        if "cache" not in self.config:
            self.config["cache"] = {}
        self.config["cache"]["last_updated"] = datetime.now().isoformat()

        # Save configuration
        with open(self.config_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

        return self.config_path

    def load(self) -> dict[str, Any]:
        """Load configuration from file.

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If configuration file doesn't exist
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration not found at {self.config_path}. "
                "Run 'ai-org config init' to create."
            )

        self._load_config()
        return self.config

    def get_value(self, key: str) -> Any:
        """Get configuration value by dot-separated key.

        Args:
            key: Dot-separated configuration key (e.g., "sso.default_principal_email")

        Returns:
            Configuration value or None if not found
        """
        parts = key.split(".")
        value = self.config

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None

        return value

    def set_value(self, key: str, value: Any) -> None:
        """Set configuration value by dot-separated key.

        Args:
            key: Dot-separated configuration key
            value: Value to set
        """
        parts = key.split(".")
        config = self.config

        # Navigate to the parent
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]

        # Set the value
        config[parts[-1]] = value

    def get_default_principal_email(self) -> Optional[str]:
        """Get default principal email.

        Returns:
            Default principal email or None
        """
        return self.get_value("sso.default_principal_email")

    def get_default_permission_set(self) -> str:
        """Get default permission set.

        Returns:
            Default permission set name
        """
        return self.get_value("sso.default_permission_set") or "AWSAdministratorAccess"

    def get_default_ou(self) -> Optional[str]:
        """Get default organizational unit.

        Returns:
            Default OU ID or None
        """
        return self.get_value("defaults.ou")

    def get_cached_value(self, key: str) -> Any:
        """Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        return self.get_value(f"cache.{key}")

    def set_cached_value(self, key: str, value: Any) -> None:
        """Set cached value.

        Args:
            key: Cache key
            value: Value to cache
        """
        if "cache" not in self.config:
            self.config["cache"] = {}
        self.config["cache"][key] = value

    def get_cached_user(self, email: str) -> Optional[str]:
        """Get cached user ID for email.

        Args:
            email: User email

        Returns:
            User ID or None
        """
        mappings = self.get_cached_value("user_mappings") or {}
        return mappings.get(email)

    def cache_user(self, email: str, user_id: str) -> None:
        """Cache user ID for email.

        Args:
            email: User email
            user_id: SSO user ID
        """
        mappings = self.get_cached_value("user_mappings") or {}
        mappings[email] = user_id
        self.set_cached_value("user_mappings", mappings)
