"""AWS Organizations OU management."""

from typing import Any, Optional

from botocore.exceptions import ClientError

from ai_org.core.aws_client import AWSClient


class OUManager:
    """Manages AWS Organizations OUs."""

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None):
        """Initialize OU manager.

        Args:
            profile: AWS profile name
            region: AWS region
        """
        self.aws = AWSClient(profile, region)
        self.org_client = self.aws.client("organizations")

    def get_ou_tree(self) -> dict[str, Any]:
        """Get the complete OU hierarchy as a tree structure.

        Returns:
            Dictionary representing the OU tree with structure:
            {
                "Id": "r-xxxx",
                "Name": "Root",
                "Type": "ROOT",
                "Children": [
                    {
                        "Id": "ou-xxxx-yyyy",
                        "Name": "Security",
                        "Type": "ORGANIZATIONAL_UNIT",
                        "Children": [...]
                    }
                ]
            }
        """
        try:
            # Get the root
            roots = self.org_client.list_roots()
            if not roots["Roots"]:
                raise Exception("No root found in organization")

            root = roots["Roots"][0]
            root_tree = {
                "Id": root["Id"],
                "Name": root["Name"],
                "Type": "ROOT",
                "Children": [],
            }

            # Build the tree recursively
            self._build_ou_tree(root["Id"], root_tree)
            return root_tree

        except ClientError as e:
            raise Exception(self.aws.handle_error(e, "Failed to get OU tree")) from e

    def _build_ou_tree(self, parent_id: str, parent_node: dict[str, Any]) -> None:
        """Recursively build the OU tree.

        Args:
            parent_id: Parent OU/Root ID
            parent_node: Parent node in the tree
        """
        # Get OUs for this parent
        try:
            response = self.org_client.list_organizational_units_for_parent(ParentId=parent_id)
            for ou in response.get("OrganizationalUnits", []):
                ou_node = {
                    "Id": ou["Id"],
                    "Name": ou["Name"],
                    "Type": "ORGANIZATIONAL_UNIT",
                    "Children": [],
                }
                parent_node["Children"].append(ou_node)
                # Recursively get children
                self._build_ou_tree(ou["Id"], ou_node)
        except ClientError:
            # Skip if we can't access this OU
            pass

    def list_ous(self) -> list[dict[str, Any]]:
        """List all OUs in the organization with their paths.

        Returns:
            List of OU dictionaries with Id, Name, and Path
        """
        try:
            tree = self.get_ou_tree()
            ous: list[dict[str, Any]] = []
            self._flatten_ou_tree(tree, ous, "")
            return ous
        except Exception as e:
            raise Exception(f"Failed to list OUs: {e}") from e

    def _flatten_ou_tree(
        self, node: dict[str, Any], result: list[dict[str, Any]], parent_path: str
    ) -> None:
        """Flatten the OU tree into a list with paths.

        Args:
            node: Current node in the tree
            result: Result list to append to
            parent_path: Path of parent
        """
        current_path = f"{parent_path}/{node['Name']}" if parent_path else node["Name"]

        # Add current node
        result.append(
            {"Id": node["Id"], "Name": node["Name"], "Path": current_path, "Type": node["Type"]}
        )

        # Process children
        for child in node.get("Children", []):
            self._flatten_ou_tree(child, result, current_path)

    def get_ou_details(self, ou_id: str) -> dict[str, Any]:
        """Get details for a specific OU.

        Args:
            ou_id: OU ID

        Returns:
            OU details including accounts
        """
        try:
            # Get OU details
            response = self.org_client.describe_organizational_unit(OrganizationalUnitId=ou_id)
            ou = response["OrganizationalUnit"]

            # Get accounts in this OU
            accounts_response = self.org_client.list_accounts_for_parent(ParentId=ou_id)
            accounts = accounts_response.get("Accounts", [])

            # Get child OUs
            children_response = self.org_client.list_organizational_units_for_parent(ParentId=ou_id)
            children = children_response.get("OrganizationalUnits", [])

            return {
                "Id": ou["Id"],
                "Name": ou["Name"],
                "Arn": ou["Arn"],
                "Accounts": accounts,
                "ChildOUs": children,
                "AccountCount": len(accounts),
                "ChildOUCount": len(children),
            }

        except ClientError as e:
            raise Exception(
                self.aws.handle_error(e, f"Failed to get OU details for {ou_id}")
            ) from e

    def get_ou_by_name(self, name: str) -> Optional[str]:
        """Get OU ID by name.

        Args:
            name: OU name to search for

        Returns:
            OU ID if found, None otherwise
        """
        try:
            ous = self.list_ous()
            for ou in ous:
                if ou["Name"].lower() == name.lower():
                    return ou["Id"]
            return None
        except Exception:
            return None

    def format_ou_tree(self, tree: Optional[dict[str, Any]] = None, indent: str = "") -> str:
        """Format OU tree for display.

        Args:
            tree: OU tree dictionary (gets full tree if None)
            indent: Current indentation level

        Returns:
            Formatted tree string
        """
        if tree is None:
            tree = self.get_ou_tree()

        lines = []
        is_last = indent and indent[-1] == "└"

        # Format current node
        if indent:
            prefix = indent[:-4] + ("└── " if is_last else "├── ")
        else:
            prefix = ""

        lines.append(f"{prefix}{tree['Name']} ({tree['Id']})")

        # Format children
        children = tree.get("Children", [])
        for i, child in enumerate(children):
            is_child_last = i == len(children) - 1
            child_indent = indent[:-4] + ("    " if is_last else "│   ") if indent else ""
            child_indent += "└   " if is_child_last else "├   "
            child_lines = self.format_ou_tree(child, child_indent)
            lines.append(child_lines)

        return "\n".join(lines) if isinstance(lines[0], str) else lines[0]
