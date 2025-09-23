#!/usr/bin/env python
"""List all SSO users in the Identity Store."""

import boto3
from botocore.exceptions import ClientError


def list_sso_users():
    """List all SSO users."""
    try:
        # Create SSO Admin client
        sso_admin = boto3.client("sso-admin", region_name="us-east-1")
        identity_store = boto3.client("identitystore", region_name="us-east-1")

        # Get SSO instance
        response = sso_admin.list_instances()
        if not response.get("Instances"):
            print("No SSO instance found")
            return

        instance = response["Instances"][0]
        identity_store_id = instance["IdentityStoreId"]

        print(f"Identity Store ID: {identity_store_id}")
        print("\nSSO Users:")
        print("-" * 60)

        # List users
        paginator = identity_store.get_paginator("list_users")
        for page in paginator.paginate(IdentityStoreId=identity_store_id):
            for user in page.get("Users", []):
                user_id = user["UserId"]
                username = user.get("UserName", "N/A")

                # Get user details
                user_details = identity_store.describe_user(
                    IdentityStoreId=identity_store_id, UserId=user_id
                )

                # Extract emails
                emails = user_details.get("Emails", [])
                primary_email = next(
                    (e["Value"] for e in emails if e.get("Primary")),
                    emails[0]["Value"] if emails else "No email",
                )

                # Extract name
                name = user_details.get(
                    "DisplayName",
                    f"{user_details.get('Name', {}).get('GivenName', '')} "
                    f"{user_details.get('Name', {}).get('FamilyName', '')}".strip()
                    or "N/A",
                )

                print(f"User: {username}")
                print(f"  Name: {name}")
                print(f"  Email: {primary_email}")
                print(f"  User ID: {user_id}")
                print()

    except ClientError as e:
        print(f"Error: {e}")
        print("\nMake sure you have the correct AWS profile set and SSO is configured.")


if __name__ == "__main__":
    import os

    # Use the org profile
    os.environ["AWS_PROFILE"] = "org"
    list_sso_users()
