"""AWS CloudFormation StackSet management."""

import json
import time
from typing import Any, Optional

import yaml
from botocore.exceptions import ClientError

from ai_org.core.aws_client import AWSClient


class StackSetManager:
    """Manages AWS CloudFormation StackSets."""

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None):
        """Initialize StackSet manager.

        Args:
            profile: AWS profile name
            region: AWS region
        """
        self.aws = AWSClient(profile, region)
        self.cfn_client = self.aws.client("cloudformation")

    def get_deployment_status(
        self, account_id: str, stackset_name: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Get StackSet deployment status for an account.

        Args:
            account_id: AWS account ID
            stackset_name: Specific StackSet name (optional)

        Returns:
            List of status dictionaries
        """
        try:
            statuses = []

            if stackset_name:
                # Get status for specific StackSet
                stacksets = [stackset_name]
            else:
                # List all StackSets
                stacksets = self._list_all_stacksets()

            for name in stacksets:
                try:
                    # Get stack instance status
                    response = self.cfn_client.describe_stack_instance(
                        StackSetName=name,
                        StackInstanceAccount=account_id,
                        StackInstanceRegion=self.aws.region,
                    )
                    instance = response["StackInstance"]
                    statuses.append(
                        {
                            "StackSetName": name,
                            "Status": instance.get("Status", "UNKNOWN"),
                            "StatusReason": instance.get("StatusReason", ""),
                            "DriftStatus": instance.get("DriftStatus", "NOT_CHECKED"),
                        }
                    )
                except ClientError as e:
                    if e.response["Error"]["Code"] == "StackInstanceNotFoundException":
                        # Stack instance doesn't exist for this account
                        statuses.append(
                            {
                                "StackSetName": name,
                                "Status": "NOT_DEPLOYED",
                                "StatusReason": "Stack instance not found",
                                "DriftStatus": "NOT_CHECKED",
                            }
                        )
                    else:
                        raise

            return statuses

        except ClientError as e:
            raise Exception(self.aws.handle_error(e, "Failed to get deployment status")) from e

    def wait_for_deployments(
        self,
        account_id: str,
        stackset_name: Optional[str] = None,
        timeout: int = 300,
    ) -> bool:
        """Wait for StackSet deployments to complete.

        Args:
            account_id: AWS account ID
            stackset_name: Specific StackSet name (optional)
            timeout: Maximum wait time in seconds

        Returns:
            True if all deployments succeeded, False otherwise
        """
        start_time = time.time()
        check_interval = 10

        while time.time() - start_time < timeout:
            statuses = self.get_deployment_status(account_id, stackset_name)

            # Check if all are in a terminal state
            all_complete = True
            all_success = True

            for status in statuses:
                state = status["Status"]
                if state in ["PENDING", "RUNNING", "OUTDATED"]:
                    all_complete = False
                    break
                if state not in ["CURRENT", "SUCCEEDED"]:
                    all_success = False

            if all_complete:
                return all_success

            time.sleep(check_interval)

        return False  # Timed out

    def list_stacksets(self) -> list[dict[str, Any]]:
        """List all StackSets in the organization.

        Returns:
            List of StackSet dictionaries
        """
        try:
            stacksets = []
            paginator = self.cfn_client.get_paginator("list_stack_sets")

            for page in paginator.paginate(Status="ACTIVE"):
                for summary in page.get("Summaries", []):
                    stacksets.append(
                        {
                            "StackSetName": summary["StackSetName"],
                            "Status": summary.get("Status", "UNKNOWN"),
                            "AutoDeployment": "Enabled"
                            if summary.get("AutoDeployment", {}).get("Enabled")
                            else "Disabled",
                            "Capabilities": ", ".join(summary.get("Capabilities", [])),
                            "DriftStatus": summary.get("DriftStatus", "NOT_CHECKED"),
                        }
                    )

            return stacksets

        except ClientError as e:
            raise Exception(self.aws.handle_error(e, "Failed to list StackSets")) from e

    def _list_all_stacksets(self) -> list[str]:
        """List all StackSet names.

        Returns:
            List of StackSet names
        """
        stacksets = []
        paginator = self.cfn_client.get_paginator("list_stack_sets")

        for page in paginator.paginate(Status="ACTIVE"):
            for summary in page.get("Summaries", []):
                stacksets.append(summary["StackSetName"])

        return stacksets

    def get_stackset_operations(self, stackset_name: str, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent operations for a StackSet.

        Args:
            stackset_name: StackSet name
            limit: Maximum number of operations to return

        Returns:
            List of operation dictionaries
        """
        try:
            response = self.cfn_client.list_stack_set_operations(
                StackSetName=stackset_name,
                MaxResults=limit,
            )

            operations = []
            for op in response.get("Summaries", []):
                operations.append(
                    {
                        "OperationId": op["OperationId"],
                        "Action": op.get("Action", "UNKNOWN"),
                        "Status": op.get("Status", "UNKNOWN"),
                        "CreationTime": op.get("CreationTimestamp"),
                        "EndTime": op.get("EndTimestamp"),
                    }
                )

            return operations

        except ClientError as e:
            raise Exception(
                self.aws.handle_error(e, f"Failed to get operations for {stackset_name}")
            ) from e

    def get_stackset_parameters(self, stackset_name: str) -> list[dict[str, Any]]:
        """Get parameter definitions from a StackSet.

        Args:
            stackset_name: Name of the StackSet

        Returns:
            List of parameter definitions with names, types, defaults, and descriptions
        """
        try:
            # Try with DELEGATED_ADMIN first, fall back to default if not delegated
            try:
                response = self.cfn_client.describe_stack_set(
                    StackSetName=stackset_name,
                    CallAs="DELEGATED_ADMIN",
                )
            except ClientError as e:
                if "ValidationError" in str(e):
                    # Not a delegated admin, try without CallAs
                    response = self.cfn_client.describe_stack_set(
                        StackSetName=stackset_name,
                    )
                else:
                    raise

            stackset = response.get("StackSet", {})
            template_body = stackset.get("TemplateBody", "")
            current_params = {
                p["ParameterKey"]: p["ParameterValue"] for p in stackset.get("Parameters", [])
            }

            # Parse template to get parameter definitions
            try:
                # Try parsing as JSON first
                template = json.loads(template_body)
            except json.JSONDecodeError:
                # Fall back to YAML
                try:
                    template = yaml.safe_load(template_body)
                except Exception:
                    # If both fail, return current parameters without definitions
                    return [
                        {
                            "name": key,
                            "type": "String",
                            "default": None,
                            "description": None,
                            "current_value": value,
                        }
                        for key, value in current_params.items()
                    ]

            # Extract parameter definitions from template
            parameters = []
            for param_name, param_def in template.get("Parameters", {}).items():
                parameters.append(
                    {
                        "name": param_name,
                        "type": param_def.get("Type", "String"),
                        "default": param_def.get("Default"),
                        "description": param_def.get("Description"),
                        "allowed_values": param_def.get("AllowedValues"),
                        "current_value": current_params.get(param_name, param_def.get("Default")),
                    }
                )

            return parameters

        except ClientError as e:
            raise Exception(
                self.aws.handle_error(e, f"Failed to get parameters for {stackset_name}")
            ) from e

    def deploy_to_account(
        self,
        account_id: str,
        stackset_name: str,
        parameters: Optional[dict[str, str]] = None,
        regions: Optional[list[str]] = None,
    ) -> str:
        """Deploy a StackSet to a specific account.

        Args:
            account_id: Target AWS account ID
            stackset_name: Name of the StackSet to deploy
            parameters: Parameter overrides as key-value pairs
            regions: List of regions to deploy to (defaults to us-east-1, us-west-2)

        Returns:
            Operation ID for tracking the deployment
        """
        try:
            if not regions:
                regions = ["us-east-1", "us-west-2"]

            # Convert parameters to CloudFormation format
            param_overrides = []
            if parameters:
                for key, value in parameters.items():
                    param_overrides.append({"ParameterKey": key, "ParameterValue": value})

            # Create stack instances
            try:
                response = self.cfn_client.create_stack_instances(
                    StackSetName=stackset_name,
                    DeploymentTargets={"Accounts": [account_id]},
                    Regions=regions,
                    ParameterOverrides=param_overrides if param_overrides else [],
                    OperationPreferences={
                        "RegionConcurrencyType": "PARALLEL",
                        "MaxConcurrentPercentage": 100,
                    },
                    CallAs="DELEGATED_ADMIN",
                )
            except ClientError as e:
                if "ValidationError" in str(e) and "delegated administrator" in str(e):
                    # Not a delegated admin, try without CallAs
                    response = self.cfn_client.create_stack_instances(
                        StackSetName=stackset_name,
                        DeploymentTargets={"Accounts": [account_id]},
                        Regions=regions,
                        ParameterOverrides=param_overrides if param_overrides else [],
                        OperationPreferences={
                            "RegionConcurrencyType": "PARALLEL",
                            "MaxConcurrentPercentage": 100,
                        },
                    )
                else:
                    raise

            return response["OperationId"]

        except ClientError as e:
            # Check if stack instances already exist
            if e.response["Error"]["Code"] == "StackInstanceNotFoundException":
                # Try updating existing instances
                try:
                    try:
                        response = self.cfn_client.update_stack_instances(
                            StackSetName=stackset_name,
                            DeploymentTargets={"Accounts": [account_id]},
                            Regions=regions,
                            ParameterOverrides=param_overrides if param_overrides else [],
                            OperationPreferences={
                                "RegionConcurrencyType": "PARALLEL",
                                "MaxConcurrentPercentage": 100,
                            },
                            CallAs="DELEGATED_ADMIN",
                        )
                    except ClientError as update_e:
                        if "ValidationError" in str(update_e) and "delegated administrator" in str(
                            update_e
                        ):
                            # Not a delegated admin, try without CallAs
                            response = self.cfn_client.update_stack_instances(
                                StackSetName=stackset_name,
                                DeploymentTargets={"Accounts": [account_id]},
                                Regions=regions,
                                ParameterOverrides=param_overrides if param_overrides else [],
                                OperationPreferences={
                                    "RegionConcurrencyType": "PARALLEL",
                                    "MaxConcurrentPercentage": 100,
                                },
                            )
                        else:
                            raise
                    return response["OperationId"]
                except ClientError as update_error:
                    raise Exception(
                        self.aws.handle_error(
                            update_error, f"Failed to update stack instances for {stackset_name}"
                        )
                    ) from update_error
            else:
                raise Exception(
                    self.aws.handle_error(e, f"Failed to deploy {stackset_name} to {account_id}")
                ) from e

    def wait_for_deployment_operation(
        self, stackset_name: str, operation_id: str, timeout: int = 600
    ) -> bool:
        """Wait for a StackSet operation to complete.

        Args:
            stackset_name: Name of the StackSet
            operation_id: Operation ID to monitor
            timeout: Maximum wait time in seconds

        Returns:
            True if operation succeeded, False otherwise
        """
        start_time = time.time()
        check_interval = 5

        while time.time() - start_time < timeout:
            try:
                try:
                    response = self.cfn_client.describe_stack_set_operation(
                        StackSetName=stackset_name,
                        OperationId=operation_id,
                        CallAs="DELEGATED_ADMIN",
                    )
                except ClientError as e:
                    if "ValidationError" in str(e) and "delegated administrator" in str(e):
                        # Not a delegated admin, try without CallAs
                        response = self.cfn_client.describe_stack_set_operation(
                            StackSetName=stackset_name,
                            OperationId=operation_id,
                        )
                    else:
                        raise

                operation = response.get("StackSetOperation", {})
                status = operation.get("Status")

                if status == "SUCCEEDED":
                    return True
                if status in ["FAILED", "STOPPED"]:
                    return False
                # Status is RUNNING or QUEUED, keep waiting

                time.sleep(check_interval)

            except ClientError as e:
                raise Exception(
                    self.aws.handle_error(e, f"Failed to check operation status for {operation_id}")
                ) from e

        return False  # Timed out
