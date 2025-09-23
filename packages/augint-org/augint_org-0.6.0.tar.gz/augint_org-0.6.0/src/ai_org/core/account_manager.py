"""AWS Organizations account management."""

import time
from typing import Any, Optional

from botocore.exceptions import ClientError

from ai_org.core.aws_client import AWSClient


class AccountManager:
    """Manages AWS Organizations accounts."""

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None):
        """Initialize account manager.

        Args:
            profile: AWS profile name
            region: AWS region
        """
        self.aws = AWSClient(profile, region)
        self.org_client = self.aws.client("organizations")

    def create_account(self, name: str, email: str, ou_id: str, wait: bool = True) -> str:
        """Create a new AWS account.

        Args:
            name: Account name
            email: Root email address
            ou_id: Target organizational unit ID
            wait: Whether to wait for creation to complete

        Returns:
            Account ID of the created account

        Raises:
            Exception: If account creation fails
        """
        try:
            # Create the account
            response = self.org_client.create_account(
                Email=email,
                AccountName=name,
                IamUserAccessToBilling="ALLOW",
            )

            request_id = response["CreateAccountStatus"]["Id"]

            # Always wait for account ID (needed for SSO assignment)
            account_id = self._wait_for_account_creation(request_id)

            # Move to specified OU if waiting and not root
            if wait and ou_id and ou_id != self._get_root_ou_id():
                self._move_account_to_ou(account_id, ou_id)

            return account_id

        except ClientError as e:
            raise Exception(self.aws.handle_error(e, "Failed to create account")) from e

    def _wait_for_account_creation(self, request_id: str, timeout: int = 600) -> str:
        """Wait for account creation to complete.

        Args:
            request_id: Create account request ID
            timeout: Maximum wait time in seconds

        Returns:
            Account ID of the created account

        Raises:
            Exception: If creation fails or times out
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            response = self.org_client.describe_create_account_status(
                CreateAccountRequestId=request_id
            )
            status = response["CreateAccountStatus"]

            if status["State"] == "SUCCEEDED":
                return status["AccountId"]
            if status["State"] == "FAILED":
                reason = status.get("FailureReason", "Unknown reason")
                raise Exception(f"Account creation failed: {reason}")

            time.sleep(10)

        raise Exception(f"Account creation timed out after {timeout} seconds")

    def _get_root_ou_id(self) -> str:
        """Get the root organizational unit ID.

        Returns:
            Root OU ID
        """
        response = self.org_client.list_roots()
        return response["Roots"][0]["Id"]

    def _move_account_to_ou(self, account_id: str, ou_id: str) -> None:
        """Move account to specified organizational unit.

        Args:
            account_id: AWS account ID
            ou_id: Target organizational unit ID
        """
        # Find current parent
        response = self.org_client.list_parents(ChildId=account_id)
        current_parent = response["Parents"][0]["Id"]

        # Move to new OU
        self.org_client.move_account(
            AccountId=account_id,
            SourceParentId=current_parent,
            DestinationParentId=ou_id,
        )

    def list_accounts(
        self, ou: Optional[str] = None, status: str = "ACTIVE"
    ) -> list[dict[str, Any]]:
        """List accounts in the organization.

        Args:
            ou: Optional OU ID to filter by
            status: Account status filter

        Returns:
            List of account dictionaries
        """
        try:
            if ou:
                # List accounts for specific OU
                response = self.org_client.list_accounts_for_parent(ParentId=ou)
                accounts = response.get("Accounts", [])
            else:
                # List all accounts
                accounts = self.aws.paginate(self.org_client, "list_accounts")

            # Filter by status
            return [a for a in accounts if a.get("Status") == status]

        except ClientError as e:
            raise Exception(self.aws.handle_error(e, "Failed to list accounts")) from e

    def get_account(self, account_id: str) -> dict[str, Any]:
        """Get details for a specific account.

        Args:
            account_id: AWS account ID

        Returns:
            Account details dictionary
        """
        try:
            response = self.org_client.describe_account(AccountId=account_id)
            return response["Account"]
        except ClientError as e:
            raise Exception(self.aws.handle_error(e, "Failed to get account")) from e

    def get_account_parent_ou(self, account_id: str) -> dict[str, Any]:
        """Get parent OU information for an account.

        Args:
            account_id: AWS account ID

        Returns:
            Dictionary with parent OU information
        """
        try:
            response = self.org_client.list_parents(ChildId=account_id)
            if not response["Parents"]:
                return {"Id": None, "Name": None, "Type": None}

            parent = response["Parents"][0]
            parent_id = parent["Id"]
            parent_type = parent["Type"]

            # Get parent name
            if parent_type == "ROOT":
                roots = self.org_client.list_roots()
                parent_name = roots["Roots"][0]["Name"] if roots["Roots"] else "Root"
            else:
                # It's an OU
                ou_response = self.org_client.describe_organizational_unit(
                    OrganizationalUnitId=parent_id
                )
                parent_name = ou_response["OrganizationalUnit"]["Name"]

            return {"Id": parent_id, "Name": parent_name, "Type": parent_type}

        except ClientError as e:
            # If we can't get parent info, return unknown
            return {"Id": "unknown", "Name": "Unknown", "Type": "UNKNOWN"}

    def list_accounts_with_ou(
        self, ou: Optional[str] = None, status: str = "ACTIVE"
    ) -> list[dict[str, Any]]:
        """List accounts with their parent OU information.

        Args:
            ou: Optional OU ID to filter by
            status: Account status filter

        Returns:
            List of account dictionaries with OU info
        """
        try:
            # Get base account list
            accounts = self.list_accounts(ou=ou, status=status)

            # Add OU information to each account
            for account in accounts:
                parent_info = self.get_account_parent_ou(account["Id"])
                account["ParentId"] = parent_info["Id"]
                account["ParentName"] = parent_info["Name"]
                account["ParentType"] = parent_info["Type"]

            return accounts

        except Exception as e:
            # If we fail to get OU info, return accounts without it
            return accounts

    def get_ou_by_name(self, name: str) -> Optional[str]:
        """Get OU ID by name.

        Args:
            name: OU name to search for

        Returns:
            OU ID if found, None otherwise
        """
        try:
            root = self._get_root_ou_id()
            return self._find_ou_recursive(root, name)
        except ClientError as e:
            raise Exception(self.aws.handle_error(e, "Failed to find OU")) from e

    def _find_ou_recursive(self, parent_id: str, name: str) -> Optional[str]:
        """Recursively search for OU by name.

        Args:
            parent_id: Parent OU ID to search from
            name: OU name to find

        Returns:
            OU ID if found, None otherwise
        """
        response = self.org_client.list_organizational_units_for_parent(ParentId=parent_id)

        for ou in response.get("OrganizationalUnits", []):
            if ou["Name"].lower() == name.lower():
                return ou["Id"]

            # Recursively search children
            found = self._find_ou_recursive(ou["Id"], name)
            if found:
                return found

        return None
