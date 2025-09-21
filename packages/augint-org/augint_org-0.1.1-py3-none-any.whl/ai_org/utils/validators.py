"""Input validation utilities."""

import re


def validate_email(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_account_id(account_id: str) -> bool:
    """Validate AWS account ID.

    Args:
        account_id: AWS account ID to validate

    Returns:
        True if valid 12-digit account ID
    """
    return bool(re.match(r"^\d{12}$", account_id))


def validate_ou_id(ou_id: str) -> bool:
    """Validate organizational unit ID.

    Args:
        ou_id: OU ID to validate

    Returns:
        True if valid OU ID format
    """
    # OU IDs have format: ou-xxxx-xxxxxxxx or r-xxxx (for root)
    ou_pattern = r"^ou-[a-z0-9]{4}-[a-z0-9]{8}$"
    root_pattern = r"^r-[a-z0-9]{4}$"
    return bool(re.match(ou_pattern, ou_id) or re.match(root_pattern, ou_id))


def validate_account_name(name: str) -> bool:
    """Validate AWS account name.

    Args:
        name: Account name to validate

    Returns:
        True if valid account name
    """
    # AWS account names can contain letters, numbers, spaces, and some special characters
    # They must be between 1 and 50 characters
    if not name or len(name) > 50:
        return False

    # Check for allowed characters
    pattern = r"^[a-zA-Z0-9\s\-_]+$"
    return bool(re.match(pattern, name))


def validate_region(region: str) -> bool:
    """Validate AWS region name.

    Args:
        region: Region name to validate

    Returns:
        True if valid region format
    """
    # AWS regions have format: us-east-1, eu-west-2, etc.
    pattern = r"^[a-z]{2}-[a-z]+-\d+$"
    return bool(re.match(pattern, region))


def validate_stackset_name(name: str) -> bool:
    """Validate StackSet name.

    Args:
        name: StackSet name to validate

    Returns:
        True if valid StackSet name
    """
    # StackSet names can contain letters, numbers, and hyphens
    # They must be between 1 and 128 characters
    if not name or len(name) > 128:
        return False

    pattern = r"^[a-zA-Z][a-zA-Z0-9\-]*$"
    return bool(re.match(pattern, name))


def validate_permission_set_name(name: str) -> bool:
    """Validate SSO permission set name.

    Args:
        name: Permission set name to validate

    Returns:
        True if valid permission set name
    """
    # Permission set names can contain letters, numbers, and some special characters
    # They must be between 1 and 32 characters
    if not name or len(name) > 32:
        return False

    pattern = r"^[a-zA-Z0-9\-_]+$"
    return bool(re.match(pattern, name))


def sanitize_account_name(name: str) -> str:
    """Sanitize account name for AWS.

    Args:
        name: Account name to sanitize

    Returns:
        Sanitized account name
    """
    # Replace invalid characters with hyphens
    sanitized = re.sub(r"[^a-zA-Z0-9\s\-_]", "-", name)

    # Replace multiple spaces/hyphens with single hyphen
    sanitized = re.sub(r"[\s\-]+", "-", sanitized)

    # Remove leading/trailing hyphens
    sanitized = sanitized.strip("-")

    # Truncate to 50 characters
    return sanitized[:50]


def parse_principal_type(principal: str) -> str:
    """Determine principal type from string.

    Args:
        principal: Principal string (email or group name)

    Returns:
        "USER" if email format, "GROUP" otherwise
    """
    return "USER" if "@" in principal else "GROUP"
