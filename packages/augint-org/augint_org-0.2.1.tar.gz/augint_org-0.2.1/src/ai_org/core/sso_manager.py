"""AWS SSO permission management."""

import time
from typing import Any, Optional

from botocore.exceptions import ClientError

from ai_org.core.account_manager import AccountManager
from ai_org.core.aws_client import AWSClient
from ai_org.core.config_manager import ConfigManager


class SSOManager:
    """Manages AWS SSO permissions and assignments."""

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None):
        """Initialize SSO manager.

        Args:
            profile: AWS profile name
            region: AWS region
        """
        self.aws = AWSClient(profile, region)
        self.sso_client = self.aws.client("sso-admin")
        self.identity_client = self.aws.client("identitystore")
        self.config = ConfigManager()
        self._sso_instance_arn: Optional[str] = None
        self._identity_store_id: Optional[str] = None

    @property
    def sso_instance_arn(self) -> str:
        """Get SSO instance ARN from cache or discover it."""
        if not self._sso_instance_arn:
            self._sso_instance_arn = self.config.get_cached_value("sso_instance_arn")
            if not self._sso_instance_arn:
                self._discover_sso_instance()
        return self._sso_instance_arn or ""

    @property
    def identity_store_id(self) -> str:
        """Get Identity Store ID from cache or discover it."""
        if not self._identity_store_id:
            self._identity_store_id = self.config.get_cached_value("identity_store_id")
            if not self._identity_store_id:
                self._discover_sso_instance()
        return self._identity_store_id or ""

    def _discover_sso_instance(self) -> None:
        """Discover SSO instance and Identity Store."""
        try:
            response = self.sso_client.list_instances()
            if not response.get("Instances"):
                raise Exception("No SSO instance found")

            instance = response["Instances"][0]
            self._sso_instance_arn = instance["InstanceArn"]
            self._identity_store_id = instance["IdentityStoreId"]

            # Cache the values
            self.config.set_cached_value("sso_instance_arn", self._sso_instance_arn)
            self.config.set_cached_value("identity_store_id", self._identity_store_id)
            self.config.save()

        except ClientError as e:
            raise Exception(self.aws.handle_error(e, "Failed to discover SSO instance")) from e

    def assign_permission(
        self,
        account_id: str,
        principal: str,
        permission_set: str = "AWSAdministratorAccess",
        principal_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """Assign SSO permission to an account.

        Args:
            account_id: AWS account ID
            principal: Email address or group name
            permission_set: Permission set name
            principal_type: USER or GROUP (auto-detected if not specified)

        Returns:
            Assignment result dictionary
        """
        try:
            # Get principal ID
            principal_id = self._get_principal_id(principal, principal_type)
            if not principal_type:
                principal_type = "USER" if "@" in principal else "GROUP"

            # Get permission set ARN
            permission_set_arn = self._get_permission_set_arn(permission_set)

            # Create assignment
            response = self.sso_client.create_account_assignment(
                InstanceArn=self.sso_instance_arn,
                TargetId=account_id,
                TargetType="AWS_ACCOUNT",
                PermissionSetArn=permission_set_arn,
                PrincipalType=principal_type,
                PrincipalId=principal_id,
            )

            # Wait for provisioning if requested
            request_id = response["AccountAssignmentCreationStatus"]["RequestId"]
            self._wait_for_assignment(request_id)

            return {
                "account_id": account_id,
                "principal": principal,
                "principal_id": principal_id,
                "permission_set": permission_set,
                "status": "success",
            }

        except ClientError as e:
            raise Exception(self.aws.handle_error(e, "Failed to assign SSO permission")) from e

    def _get_principal_id(self, principal: str, principal_type: Optional[str] = None) -> str:
        """Get principal ID from email or group name.

        Args:
            principal: Email address or group name
            principal_type: USER or GROUP (auto-detected if not specified)

        Returns:
            Principal ID
        """
        # Check cache first
        cached_id = self.config.get_cached_user(principal)
        if cached_id:
            return cached_id

        # Auto-detect type if not specified
        if not principal_type:
            principal_type = "USER" if "@" in principal else "GROUP"

        try:
            if principal_type == "USER":
                # Look up user by email
                response = self.identity_client.list_users(
                    IdentityStoreId=self.identity_store_id,
                    Filters=[
                        {
                            "AttributePath": "UserName",
                            "AttributeValue": principal,
                        }
                    ],
                )
                if not response.get("Users"):
                    raise Exception(f"User not found: {principal}")

                user_id = response["Users"][0]["UserId"]
                # Cache the user ID
                self.config.cache_user(principal, user_id)
                return user_id

            # Look up group by name
            response = self.identity_client.list_groups(
                IdentityStoreId=self.identity_store_id,
                Filters=[
                    {
                        "AttributePath": "DisplayName",
                        "AttributeValue": principal,
                    }
                ],
            )
            if not response.get("Groups"):
                raise Exception(f"Group not found: {principal}")

            return response["Groups"][0]["GroupId"]

        except ClientError as e:
            raise Exception(
                self.aws.handle_error(e, f"Failed to find {principal_type.lower()}")
            ) from e

    def _get_permission_set_arn(self, name: str) -> str:
        """Get permission set ARN by name.

        Args:
            name: Permission set name

        Returns:
            Permission set ARN
        """
        try:
            # List all permission sets
            paginator = self.sso_client.get_paginator("list_permission_sets")

            for page in paginator.paginate(InstanceArn=self.sso_instance_arn):
                for arn in page.get("PermissionSets", []):
                    # Describe each to get the name
                    response = self.sso_client.describe_permission_set(
                        InstanceArn=self.sso_instance_arn,
                        PermissionSetArn=arn,
                    )
                    if response["PermissionSet"]["Name"] == name:
                        return arn

            raise Exception(f"Permission set not found: {name}")

        except ClientError as e:
            raise Exception(self.aws.handle_error(e, "Failed to find permission set")) from e

    def _wait_for_assignment(self, request_id: str, timeout: int = 60) -> None:
        """Wait for account assignment to complete.

        Args:
            request_id: Assignment request ID
            timeout: Maximum wait time in seconds
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            response = self.sso_client.describe_account_assignment_creation_status(
                InstanceArn=self.sso_instance_arn,
                AccountAssignmentCreationRequestId=request_id,
            )
            status = response["AccountAssignmentCreationStatus"]["Status"]

            if status == "SUCCEEDED":
                return
            if status == "FAILED":
                reason = response["AccountAssignmentCreationStatus"].get("FailureReason", "Unknown")
                raise Exception(f"Assignment failed: {reason}")

            time.sleep(2)

        raise Exception(f"Assignment timed out after {timeout} seconds")

    def list_assignments(self, account_id: str) -> list[dict[str, Any]]:
        """List SSO assignments for an account.

        Args:
            account_id: AWS account ID

        Returns:
            List of assignment dictionaries
        """
        try:
            assignments = []

            # List all permission sets
            paginator = self.sso_client.get_paginator("list_permission_sets")

            for page in paginator.paginate(InstanceArn=self.sso_instance_arn):
                for permission_set_arn in page.get("PermissionSets", []):
                    # List assignments for this permission set
                    assign_paginator = self.sso_client.get_paginator("list_account_assignments")

                    for assign_page in assign_paginator.paginate(
                        InstanceArn=self.sso_instance_arn,
                        AccountId=account_id,
                        PermissionSetArn=permission_set_arn,
                    ):
                        for assignment in assign_page.get("AccountAssignments", []):
                            # Get permission set name
                            ps_response = self.sso_client.describe_permission_set(
                                InstanceArn=self.sso_instance_arn,
                                PermissionSetArn=permission_set_arn,
                            )
                            assignment["PermissionSet"] = ps_response["PermissionSet"]["Name"]
                            assignment["Status"] = "Active"
                            assignments.append(assignment)

            return assignments

        except ClientError as e:
            raise Exception(self.aws.handle_error(e, "Failed to list assignments")) from e

    def sync_permissions(
        self,
        principal: str,
        permission_set: str = "AWSAdministratorAccess",
        ou: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Sync SSO permissions across multiple accounts.

        Args:
            principal: Email address or group name
            permission_set: Permission set name
            ou: Optional OU ID to filter accounts

        Returns:
            List of sync results
        """
        results = []

        # Get accounts to sync
        account_manager = AccountManager(self.aws.profile, self.aws.region)
        accounts = account_manager.list_accounts(ou=ou)

        for account in accounts:
            account_id = account["Id"]
            try:
                result = self.assign_permission(
                    account_id=account_id,
                    principal=principal,
                    permission_set=permission_set,
                )
                result["message"] = f"Successfully assigned {permission_set}"
                results.append(result)
            except Exception as e:
                results.append(
                    {
                        "account_id": account_id,
                        "status": "failed",
                        "message": str(e),
                    }
                )

        return results

    def list_permission_sets(self) -> list[dict[str, Any]]:
        """List all available permission sets.

        Returns:
            List of permission set dictionaries
        """
        try:
            permission_sets = []
            paginator = self.sso_client.get_paginator("list_permission_sets")

            for page in paginator.paginate(InstanceArn=self.sso_instance_arn):
                for arn in page.get("PermissionSets", []):
                    # Describe each to get details
                    response = self.sso_client.describe_permission_set(
                        InstanceArn=self.sso_instance_arn,
                        PermissionSetArn=arn,
                    )
                    ps = response["PermissionSet"]
                    permission_sets.append(
                        {
                            "Name": ps["Name"],
                            "Description": ps.get("Description", ""),
                            "SessionDuration": ps.get("SessionDuration", ""),
                            "Arn": arn,
                        }
                    )

            return permission_sets

        except ClientError as e:
            raise Exception(self.aws.handle_error(e, "Failed to list permission sets")) from e
