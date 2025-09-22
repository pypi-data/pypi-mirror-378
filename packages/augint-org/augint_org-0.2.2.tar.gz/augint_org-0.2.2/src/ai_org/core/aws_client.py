"""AWS client management and session handling."""

from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError, ProfileNotFound


class AWSClient:
    """Manages AWS service clients with profile and region support."""

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None):
        """Initialize AWS client manager.

        Args:
            profile: AWS profile name (defaults to environment or 'org')
            region: AWS region (defaults to 'us-east-1')
        """
        self.profile = profile or "org"
        self.region = region or "us-east-1"
        self._session: Optional[boto3.Session] = None

    @property
    def session(self) -> boto3.Session:
        """Get or create boto3 session."""
        if self._session is None:
            try:
                self._session = boto3.Session(
                    profile_name=self.profile,
                    region_name=self.region,
                )
            except ProfileNotFound:
                # Fall back to default session if profile doesn't exist
                self._session = boto3.Session(region_name=self.region)
        return self._session

    def client(self, service: str, **kwargs: Any) -> Any:
        """Create a service client.

        Args:
            service: AWS service name (e.g., 'organizations', 'sso-admin')
            **kwargs: Additional arguments for the client

        Returns:
            Boto3 service client
        """
        return self.session.client(service, **kwargs)  # type: ignore[call-overload]

    def get_caller_identity(self) -> dict[str, Any]:
        """Get current AWS caller identity.

        Returns:
            Dict with Account, UserId, and Arn
        """
        sts = self.client("sts")
        return sts.get_caller_identity()

    def get_account_id(self) -> str:
        """Get current AWS account ID.

        Returns:
            12-digit AWS account ID
        """
        return self.get_caller_identity()["Account"]

    def get_region(self) -> str:
        """Get current AWS region.

        Returns:
            AWS region name
        """
        return self.session.region_name or self.region

    def paginate(self, client: Any, operation: str, **kwargs: Any) -> list[Any]:
        """Paginate through AWS API responses.

        Args:
            client: Boto3 client
            operation: Operation name (e.g., 'list_accounts')
            **kwargs: Parameters for the operation

        Returns:
            List of all results from pagination
        """
        paginator = client.get_paginator(operation)
        results = []

        for page in paginator.paginate(**kwargs):
            # Find the result key (usually plural of the operation)
            for key in page:
                if isinstance(page[key], list):
                    results.extend(page[key])
                    break

        return results

    def handle_error(self, error: ClientError, default_message: str) -> str:
        """Handle AWS client errors with better messages.

        Args:
            error: The ClientError exception
            default_message: Default message if specific handling not available

        Returns:
            User-friendly error message
        """
        error_code = error.response.get("Error", {}).get("Code", "Unknown")
        error_message = error.response.get("Error", {}).get("Message", str(error))

        # Common error mappings
        error_map = {
            "AccessDenied": f"Access denied. Check AWS credentials and permissions: {error_message}",
            "InvalidParameterException": f"Invalid parameter: {error_message}",
            "ResourceNotFoundException": f"Resource not found: {error_message}",
            "DuplicateAccountException": f"Account already exists: {error_message}",
            "LimitExceededException": f"AWS limit exceeded: {error_message}",
            "ValidationException": f"Validation failed: {error_message}",
        }

        return error_map.get(error_code, f"{default_message}: {error_message}")
