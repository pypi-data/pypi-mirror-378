"""Simple configuration loader with fallback to user config."""

import os
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values


def load_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get config value with simple precedence.

    Precedence order (highest to lowest):
    1. Environment variable (includes .env via python-dotenv)
    2. User config file (~/.aillc/.env.aillc-org)
    3. Default value

    Args:
        key: The configuration key to look up
        default: Default value if not found elsewhere

    Returns:
        The configuration value or None
    """
    # 1. Check environment (already includes .env loaded by python-dotenv)
    value = os.getenv(key)
    if value is not None:
        return value

    # 2. Check user config file (if exists)
    user_config_path = Path.home() / ".aillc" / ".env.aillc-org"
    if user_config_path.exists():
        try:
            user_config = dotenv_values(user_config_path)
            value = user_config.get(key)
            if value is not None:
                return value
        except Exception:
            # Can't read user config - continue without it
            pass

    # 3. Return default
    return default


def create_example_user_config() -> None:
    """Create an example user config file if it doesn't exist."""
    config_dir = Path.home() / ".aillc"
    example_path = config_dir / ".env.aillc-org.example"

    # Don't overwrite if it exists
    if example_path.exists():
        return

    try:
        config_dir.mkdir(parents=True, exist_ok=True)

        example_content = """# User-specific defaults for aillc-org
# Copy to .env.aillc-org to use

# Your GitHub organization
# GH_ACCOUNT=MyOrg

# Your default repository name
# GH_REPO=aillc-org

# Default notification email
# NOTIFICATIONS_EMAIL=me@example.com

# Default AWS profile
# AWS_PROFILE=org

# Default budget settings (USD)
# BUDGETS_MONTHLY_DEFAULT=1000
# BUDGETS_ANOMALY_THRESHOLD=100
"""

        example_path.write_text(example_content)
    except (OSError, PermissionError):
        # Can't create example - not critical
        pass
