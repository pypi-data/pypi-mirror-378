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
        """Get SSO instance ARN by discovering it from AWS."""
        if not self._sso_instance_arn:
            self._discover_sso_instance()
        return self._sso_instance_arn or ""

    @property
    def identity_store_id(self) -> str:
        """Get Identity Store ID by discovering it from AWS."""
        if not self._identity_store_id:
            self._discover_sso_instance()
        return self._identity_store_id or ""

    def _discover_sso_instance(self) -> None:
        """Discover SSO instance and Identity Store from AWS."""
        try:
            response = self.sso_client.list_instances()
            if not response.get("Instances"):
                raise Exception("No SSO instance found")

            instance = response["Instances"][0]
            self._sso_instance_arn = instance["InstanceArn"]
            self._identity_store_id = instance["IdentityStoreId"]

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

            # Wait for provisioning to complete
            if response.get("AccountAssignmentCreationStatus"):
                request_id = response["AccountAssignmentCreationStatus"]["RequestId"]
                self._wait_for_provisioning(request_id)

            return {
                "account_id": account_id,
                "principal": principal,
                "permission_set": permission_set,
                "status": "assigned",
            }

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "ConflictException":
                # Assignment already exists
                return {
                    "account_id": account_id,
                    "principal": principal,
                    "permission_set": permission_set,
                    "status": "already_exists",
                }
            raise Exception(
                self.aws.handle_error(e, f"Failed to assign permission to {account_id}")
            ) from e

    def _get_principal_id(self, principal: str, principal_type: Optional[str] = None) -> str:
        """Get principal ID from email or group name.

        Args:
            principal: Email address or group name
            principal_type: USER or GROUP (auto-detected if not specified)

        Returns:
            Principal ID

        Raises:
            Exception: If principal not found
        """
        try:
            # Auto-detect type if not specified
            if not principal_type:
                principal_type = "USER" if "@" in principal else "GROUP"

            if principal_type == "USER":
                # Search for user by email
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
                    raise Exception(f"User {principal} not found in Identity Store")

                return response["Users"][0]["UserId"]

            # Search for group by name
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
                raise Exception(f"Group {principal} not found in Identity Store")

            return response["Groups"][0]["GroupId"]

        except ClientError as e:
            raise Exception(
                self.aws.handle_error(e, f"Failed to find principal {principal}")
            ) from e

    def _get_permission_set_arn(self, permission_set_name: str) -> str:
        """Get permission set ARN from name.

        Args:
            permission_set_name: Permission set name

        Returns:
            Permission set ARN

        Raises:
            Exception: If permission set not found
        """
        try:
            paginator = self.sso_client.get_paginator("list_permission_sets")
            for page in paginator.paginate(InstanceArn=self.sso_instance_arn):
                for permission_set_arn in page.get("PermissionSets", []):
                    # Describe each permission set to get its name
                    details = self.sso_client.describe_permission_set(
                        InstanceArn=self.sso_instance_arn,
                        PermissionSetArn=permission_set_arn,
                    )
                    if details["PermissionSet"]["Name"] == permission_set_name:
                        return permission_set_arn

            raise Exception(f"Permission set {permission_set_name} not found")

        except ClientError as e:
            raise Exception(
                self.aws.handle_error(e, f"Failed to find permission set {permission_set_name}")
            ) from e

    def _wait_for_provisioning(self, request_id: str, timeout: int = 60) -> None:
        """Wait for account assignment provisioning to complete.

        Args:
            request_id: Request ID from create_account_assignment
            timeout: Timeout in seconds

        Raises:
            Exception: If provisioning fails or times out
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.sso_client.describe_account_assignment_creation_status(
                    InstanceArn=self.sso_instance_arn,
                    AccountAssignmentCreationRequestId=request_id,
                )
                status = response["AccountAssignmentCreationStatus"]["Status"]

                if status == "SUCCEEDED":
                    return
                if status == "FAILED":
                    failure_reason = response["AccountAssignmentCreationStatus"].get(
                        "FailureReason", "Unknown"
                    )
                    raise Exception(f"Assignment provisioning failed: {failure_reason}")

                time.sleep(2)

            except ClientError as e:
                raise Exception(
                    self.aws.handle_error(e, "Failed to check provisioning status")
                ) from e

        raise Exception("Assignment provisioning timed out")

    def list_assignments(self, account_id: str) -> list[dict[str, Any]]:
        """List all SSO assignments for an account.

        Args:
            account_id: AWS account ID

        Returns:
            List of assignment dictionaries
        """
        assignments = []

        try:
            # Get all permission sets
            paginator = self.sso_client.get_paginator("list_permission_sets_provisioned_to_account")
            for page in paginator.paginate(
                InstanceArn=self.sso_instance_arn,
                AccountId=account_id,
            ):
                for permission_set_arn in page.get("PermissionSets", []):
                    # Get permission set details
                    ps_details = self.sso_client.describe_permission_set(
                        InstanceArn=self.sso_instance_arn,
                        PermissionSetArn=permission_set_arn,
                    )
                    ps_name = ps_details["PermissionSet"]["Name"]

                    # List assignments for this permission set
                    assign_paginator = self.sso_client.get_paginator("list_account_assignments")
                    for assign_page in assign_paginator.paginate(
                        InstanceArn=self.sso_instance_arn,
                        AccountId=account_id,
                        PermissionSetArn=permission_set_arn,
                    ):
                        for assignment in assign_page.get("AccountAssignments", []):
                            # Get principal details
                            principal_details = self._get_principal_details(
                                assignment["PrincipalId"],
                                assignment["PrincipalType"],
                            )

                            assignments.append(
                                {
                                    "account_id": account_id,
                                    "permission_set": ps_name,
                                    "principal_type": assignment["PrincipalType"],
                                    "principal_id": assignment["PrincipalId"],
                                    "principal_name": principal_details.get("name", "Unknown"),
                                    "principal_email": principal_details.get("email"),
                                }
                            )

            return assignments

        except ClientError as e:
            raise Exception(
                self.aws.handle_error(e, f"Failed to list assignments for {account_id}")
            ) from e

    def _get_principal_details(
        self, principal_id: str, principal_type: str
    ) -> dict[str, Optional[str]]:
        """Get principal details from ID.

        Args:
            principal_id: Principal ID
            principal_type: USER or GROUP

        Returns:
            Dictionary with name and email (if applicable)
        """
        try:
            if principal_type == "USER":
                response = self.identity_client.describe_user(
                    IdentityStoreId=self.identity_store_id,
                    UserId=principal_id,
                )
                emails = response.get("Emails", [])
                primary_email = next((e["Value"] for e in emails if e.get("Primary")), None)
                return {
                    "name": response.get("DisplayName", response.get("UserName", "Unknown")),
                    "email": primary_email,
                }
            response = self.identity_client.describe_group(
                IdentityStoreId=self.identity_store_id,
                GroupId=principal_id,
            )
            return {
                "name": response.get("DisplayName", "Unknown"),
                "email": None,
            }
        except ClientError:
            # Principal may have been deleted
            return {"name": "Unknown", "email": None}

    def sync_ou_assignments(
        self,
        principal: str,
        permission_set: str = "AWSAdministratorAccess",
        ou_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Sync SSO assignments for all accounts in an OU.

        Args:
            principal: Email address or group name
            permission_set: Permission set name
            ou_id: OU ID (optional, uses default if not specified)

        Returns:
            List of assignment results
        """
        # Get accounts in the OU
        account_manager = AccountManager(self.aws.profile, self.aws.region)
        accounts = account_manager.list_accounts(ou_id)

        results = []
        for account in accounts:
            try:
                result = self.assign_permission(
                    account["Id"],
                    principal,
                    permission_set,
                )
                results.append(result)
            except Exception as e:
                results.append(
                    {
                        "account_id": account["Id"],
                        "account_name": account["Name"],
                        "status": "failed",
                        "error": str(e),
                    }
                )

        return results

    def list_permission_sets(self) -> list[dict[str, str]]:
        """List all available permission sets.

        Returns:
            List of permission set dictionaries with name and ARN
        """
        permission_sets = []

        try:
            paginator = self.sso_client.get_paginator("list_permission_sets")
            for page in paginator.paginate(InstanceArn=self.sso_instance_arn):
                for permission_set_arn in page.get("PermissionSets", []):
                    # Describe each permission set to get its name
                    details = self.sso_client.describe_permission_set(
                        InstanceArn=self.sso_instance_arn,
                        PermissionSetArn=permission_set_arn,
                    )
                    permission_sets.append(
                        {
                            "name": details["PermissionSet"]["Name"],
                            "arn": permission_set_arn,
                            "description": details["PermissionSet"].get("Description", ""),
                        }
                    )

            return sorted(permission_sets, key=lambda x: x["name"])

        except ClientError as e:
            raise Exception(self.aws.handle_error(e, "Failed to list permission sets")) from e
